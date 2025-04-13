from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","https://real-time-weather-app-gamma.vercel.app/"],  # Update for your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class WeatherAgent(BaseModel):
    query: str


# 🔍 Function to extract city name from the query
def extract_city(query: str):
    # Simple regex pattern to capture city after "in" or "at"
    match = re.search(r"in ([A-Za-z\s]+)|at ([A-Za-z\s]+)", query, re.IGNORECASE)
    if match:
        return match.group(1) or match.group(2)
    # Fallback: assume last word is the city if regex fails
    return query.strip().split()[-1]


def get_weather(city: str):
    print(f"🔨 Tool Called: get_weather for city {city}")
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)
    if response.status_code == 200:
        return f"The weather in {city} is {response.text.strip()}."
    return "Something went wrong"


@app.post("/api/weather")
async def get_the_weather(weather: WeatherAgent):
    city = extract_city(weather.query)
    response = get_weather(city)
    return {"result": response}
