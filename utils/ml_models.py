import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

class AirQualityPredictor:
    def __init__(self):
        self.models = {}
        self.model_path = 'ml/models/'
        os.makedirs(self.model_path, exist_ok=True)
    
    def prepare_data(self, df):
        """Prepara dados para treinamento"""
        # Selecionar features relevantes
        features = ['pm25', 'pm10', 'no2', 'o3', 'co2', 'temperature', 'humidity', 'pressure']
        
        # Remover linhas com valores nulos
        df_clean = df[features].dropna()
        
        X = df_clean[features[:-1]]  # Todas as features exceto pressure
        y = df_clean['pressure']     # Usando pressure como target para exemplo
        
        return X, y
    
    def train_random_forest(self, X, y):
        """Treina modelo Random Forest"""
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)
        
        # Avaliação
        y_pred = rf_model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Salvar modelo
        joblib.dump(rf_model, os.path.join(self.model_path, 'random_forest.pkl'))
        
        return rf_model, mse, r2
    
    def train_linear_regression(self, X, y):
        """Treina modelo de Regressão Linear"""
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        lr_model = LinearRegression()
        lr_model.fit(X_train, y_train)
        
        # Avaliação
        y_pred = lr_model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Salvar modelo
        joblib.dump(lr_model, os.path.join(self.model_path, 'linear_regression.pkl'))
        
        return lr_model, mse, r2
    
    def train_kmeans(self, X, n_clusters=4):
        """Treina modelo K-Means para clustering"""
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        kmeans.fit(X)
        
        # Salvar modelo
        joblib.dump(kmeans, os.path.join(self.model_path, 'kmeans.pkl'))
        
        return kmeans
    
    def predict_air_quality(self, features, model_type='random_forest'):
        """Faz previsão usando modelo treinado"""
        model_path = os.path.join(self.model_path, f'{model_type}.pkl')
        
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            prediction = model.predict([features])
            return prediction[0]
        else:
            raise FileNotFoundError(f"Modelo {model_type} não encontrado")