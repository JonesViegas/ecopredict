import pandas as pd
import numpy as np
from datetime import datetime

class DataProcessor:
    def __init__(self):
        self.required_columns = ['location', 'latitude', 'longitude']
    
    def validate_dataset(self, df):
        """Valida a estrutura do dataset"""
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Colunas obrigatórias faltando: {missing_columns}")
        
        # Verificar valores nulos em colunas críticas
        critical_columns = ['location', 'latitude', 'longitude']
        for col in critical_columns:
            if df[col].isnull().any():
                raise ValueError(f"Valores nulos encontrados na coluna {col}")
        
        return True
    
    def clean_data(self, df):
        """Limpa e prepara os dados"""
        # Remover duplicatas
        df = df.drop_duplicates()
        
        # Preencher valores numéricos faltantes com a média
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if col not in ['latitude', 'longitude']:  # Não preencher coordenadas
                df[col] = df[col].fillna(df[col].mean())
        
        # Remover outliers usando IQR
        for col in numeric_columns:
            if col not in ['latitude', 'longitude']:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
        
        return df
    
    def calculate_air_quality_index(self, row):
        """Calcula o índice de qualidade do ar baseado nos poluentes"""
        # Implementação simplificada do AQI
        aqi_components = []
        
        if 'pm25' in row and pd.notnull(row['pm25']):
            aqi_components.append(self._pm25_to_aqi(row['pm25']))
        
        if 'pm10' in row and pd.notnull(row['pm10']):
            aqi_components.append(self._pm10_to_aqi(row['pm10']))
        
        if 'no2' in row and pd.notnull(row['no2']):
            aqi_components.append(self._no2_to_aqi(row['no2']))
        
        if 'o3' in row and pd.notnull(row['o3']):
            aqi_components.append(self._o3_to_aqi(row['o3']))
        
        return max(aqi_components) if aqi_components else 0
    
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