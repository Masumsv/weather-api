import requests
from fastapi import FastAPI
import os
from dotenv import load_dotenv


load_dotenv()
app = FastAPI()
@app.get("/")
def read_root():
    return {"message": "Weather API is running"}

@app.get("/weather/{city}")
def get_weather(city: str):
    api_key = os.getenv("WEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    return data