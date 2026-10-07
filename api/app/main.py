import requests
from fastapi import FastAPI
import os
from dotenv import load_dotenv
import psycopg2
import json


load_dotenv()

DB_HOST = "db"
DB_PORT = "5432"
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")

app = FastAPI()


def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

def get_cached_weather(city: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT data FROM weather_cache WHERE city = %s AND created_at > NOW() - INTERVAL '10 minutes' ORDER BY created_at DESC LIMIT 1",
        (city,)
    )
    result = cur.fetchone()
    cur.close()
    conn.close()
    if result:
        return result[0]
    return None

def save_weather_to_cache(city: str, data: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO weather_cache (city, data) VALUES (%s, %s)",
        (city, json.dumps(data))
    )
    conn.commit()
    cur.close()
    conn.close()

@app.get("/")
def read_root():
    return {"message": "Weather API is running"}

@app.get("/weather/{city}")
def get_weather(city: str):
    cached_data = get_cached_weather(city)
    if cached_data:
        return cached_data

    api_key = os.getenv("WEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()

    save_weather_to_cache(city, data)

    return data
