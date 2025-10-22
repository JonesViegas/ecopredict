import requests
import pandas as pd
from datetime import datetime, timedelta
import os

class DataCollector:
    def __init__(self):
        self.openaq_url = "https://api.openaq.org/v2/"
        
    def get_openaq_data(self, location=None, parameters=None, limit=1000):
        """Coleta dados do OpenAQ"""
        try:
            url = f"{self.openaq_url}measurements"
            params = {
                'limit': limit,
                'page': 1
            }
            
            if location:
                params['location'] = location
            if parameters:
                params['parameter'] = parameters
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Erro na API OpenAQ: {response.status_code}")
                return None
        except Exception as e:
            print(f"Erro ao coletar dados OpenAQ: {e}")
            return None
    
    def get_inmet_data(self, station_code):
        """Coleta dados do INMET"""
        try:
            url = f"https://apitempo.inmet.gov.br/estacao/{station_code}"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Erro na API INMET: {response.status_code}")
                return None
        except Exception as e:
            print(f"Erro ao coletar dados INMET: {e}")
            return None
    
    def calculate_aqi(self, pm25=None, pm10=None, no2=None, o3=None, co2=None, 
                     temperature=None, humidity=None, pressure=None):
        """
        Calcula o Índice de Qualidade do Ar (AQI) baseado nos poluentes e condições meteorológicas
        """
        aqi_components = []
        
        # Componente PM2.5
        if pm25 is not None:
            aqi_components.append(self._pm25_to_aqi(pm25))
        
        # Componente PM10
        if pm10 is not None:
            aqi_components.append(self._pm10_to_aqi(pm10))
        
        # Componente NO2
        if no2 is not None:
            aqi_components.append(self._no2_to_aqi(no2))
        
        # Componente O3
        if o3 is not None:
            aqi_components.append(self._o3_to_aqi(o3))
        
        # Componente meteorológico (se não há dados de poluentes)
        if not aqi_components and (temperature is not None or humidity is not None):
            base_aqi = 50  # AQI base para condições normais
            
            # Ajustar baseado na temperatura (temperaturas altas podem indicar pior qualidade do ar)
            if temperature and temperature > 30:
                base_aqi += (temperature - 30) * 2
            
            # Ajustar baseado na umidade (umidade muito alta ou muito baixa pode piorar a qualidade)
            if humidity:
                if humidity < 30 or humidity > 80:
                    base_aqi += 10
            
            aqi_components.append(min(base_aqi, 100))
        
        return max(aqi_components) if aqi_components else 25  # Default para dados insuficientes
    
    def _pm25_to_aqi(self, concentration):
        """Converte concentração de PM2.5 para AQI"""
        breakpoints = [
            (0, 12.0, 0, 50),
            (12.1, 35.4, 51, 100),
            (35.5, 55.4, 101, 150),
            (55.5, 150.4, 151, 200),
            (150.5, 250.4, 201, 300),
            (250.5, 500.4, 301, 500)
        ]
        return self._calculate_aqi_component(concentration, breakpoints)
    
    def _pm10_to_aqi(self, concentration):
        """Converte concentração de PM10 para AQI"""
        breakpoints = [
            (0, 54, 0, 50),
            (55, 154, 51, 100),
            (155, 254, 101, 150),
            (255, 354, 151, 200),
            (355, 424, 201, 300),
            (425, 604, 301, 500)
        ]
        return self._calculate_aqi_component(concentration, breakpoints)
    
    def _no2_to_aqi(self, concentration):
        """Converte concentração de NO2 para AQI"""
        # Converter de ppb para ppm se necessário
        if concentration > 1:  # Provavelmente está em ppb
            concentration = concentration / 1000
        
        breakpoints = [
            (0, 0.053, 0, 50),
            (0.054, 0.100, 51, 100),
            (0.101, 0.360, 101, 150),
            (0.361, 0.649, 151, 200),
            (0.650, 1.249, 201, 300),
            (1.250, 2.049, 301, 500)
        ]
        return self._calculate_aqi_component(concentration, breakpoints)
    
    def _o3_to_aqi(self, concentration):
        """Converte concentração de O3 para AQI"""
        breakpoints = [
            (0, 0.059, 0, 50),
            (0.060, 0.075, 51, 100),
            (0.076, 0.095, 101, 150),
            (0.096, 0.115, 151, 200),
            (0.116, 0.374, 201, 300),
            (0.375, 0.604, 301, 500)
        ]
        return self._calculate_aqi_component(concentration, breakpoints)
    
    def _calculate_aqi_component(self, concentration, breakpoints):
        """Calcula componente AQI baseado nos breakpoints"""
        for bp_low, bp_high, aqi_low, aqi_high in breakpoints:
            if bp_low <= concentration <= bp_high:
                return ((aqi_high - aqi_low) / (bp_high - bp_low)) * (concentration - bp_low) + aqi_low
        return 500  # Valor máximo se exceder todos os breakpoints