from app import db
from datetime import datetime

class AirQualityData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    pm25 = db.Column(db.Float)
    pm10 = db.Column(db.Float)
    co2 = db.Column(db.Float)
    no2 = db.Column(db.Float)
    o3 = db.Column(db.Float)
    so2 = db.Column(db.Float)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    pressure = db.Column(db.Float)
    aqi = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    source = db.Column(db.String(50))
    
    def to_dict(self):
        return {
            'id': self.id,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'pm25': self.pm25,
            'pm10': self.pm10,
            'co2': self.co2,
            'no2': self.no2,
            'o3': self.o3,
            'so2': self.so2,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'aqi': self.aqi,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source
        }

class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Dataset {self.name}>'