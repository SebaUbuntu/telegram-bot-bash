"""OpenWeatherMap implementation library."""

from homebot.core.config import get_config
import requests

DATA_VERSION = "2.5"

STANDARD_URL = f"https://api.openweathermap.org/data/{DATA_VERSION}"
PRO_URL = f"https://pro.openweathermap.org/data/{DATA_VERSION}"

CURRENT_WEATHER_URL = f"{STANDARD_URL}/weather"
HOURLY_FORECAST_URL = f"{STANDARD_URL}/forecast/hourly"
ONE_CALL_URL = f"{STANDARD_URL}/onecall"
DAILY_FORECAST_URL = f"{STANDARD_URL}/forecast/daily"
CLIMATIC_FORECAST_URL = f"{STANDARD_URL}/forecast/climate"
BULK_SNAPSHOT_URL = "http://bulk.openweathermap.org/snapshot"
BULK_ARCHIVE_URL = "http://bulk.openweathermap.org/archive"
SOLAR_RADIATION_URL = f"{STANDARD_URL}/solar_radiation"
FORECAST_URL = f"{STANDARD_URL}/forecast"
ROADRISK_URL = f"{STANDARD_URL}/roadrisk"

TEMP_UNITS = {
	"imperial": "F",
	"metric": "C"
}

WIND_UNITS = {
	"imperial": "mph",
	"metric": "km/h"
}

class Weather:
	def __init__(self):
		"""Initialize weather instance."""
		self.api_key = get_config("API_KEY")
		if self.api_key is None:
			raise AssertionError("An API key is needed")
		self.base_unit = get_config("TEMP_UNIT") if get_config("TEMP_UNIT") is not None else "metric"
		self.temp_unit = TEMP_UNITS.get(self.base_unit, "K")
		self.wind_unit = WIND_UNITS.get(self.base_unit, "km/h")

	def get_data(self, url: str, **kwargs) -> dict:
		params = {
			"appid": self.api_key,
			"units": self.base_unit,
		}
		params.update(kwargs)

		response = requests.get(url=url, params=params).json()
		if response["cod"] != 200:
			raise ConnectionError(f"Invalid response: {response['message']}")
		return response

	def current_weather(self, q: str):
		"""
		https://openweathermap.org/current

		Call current weather data for one location.
		"""
		return self.get_data(CURRENT_WEATHER_URL, q=q)

	def hourly_forecast(self, q: str):
		"""
		https://openweathermap.org/api/hourly-forecast

		Call hourly forecast data.
		"""
		return self.get_data(HOURLY_FORECAST_URL, q=q)

	def one_call(self, lat: str, lon: str):
		"""
		https://openweathermap.org/api/one-call-api

		Current and forecast weather data.
		"""
		return self.get_data(ONE_CALL_URL, lat=lat, lon=lon)

	def daily_forecast(self, q: str):
		"""
		https://openweathermap.org/forecast16

		Call 16 day / daily forecast data.
		"""
		return self.get_data(DAILY_FORECAST_URL, q=q)

	def climatic_forecast(self, q: str):
		"""
		https://openweathermap.org/api/forecast30

		Call weather forecast for 30 days.
		"""
		return self.get_data(CLIMATIC_FORECAST_URL, q=q)

	def bulk_snapshot(self, file_name: str):
		"""
		https://openweathermap.org/bulk

		Download current and forecast weather data.
		"""
		return self.get_data(f"{BULK_SNAPSHOT_URL}/{file_name}")

	def bulk_archive(self, file_name: str):
		"""
		https://openweathermap.org/bulk

		Download historical weather data.
		"""
		return self.get_data(f"{BULK_ARCHIVE_URL}/{file_name}")

	def solar_radiation(self, lat: str, lon: str):
		"""
		https://openweathermap.org/api/solar-radiation

		Provides current and forecasts solar radiation data for any coordinates on the globe.
		"""
		return self.get_data(SOLAR_RADIATION_URL, lat=lat, lon=lon)

	def forecast(self, q: str):
		"""
		https://openweathermap.org/forecast5

		Call 5 day / 3 hour forecast data.
		"""
		return self.get_data(FORECAST_URL, q=q)

	def roadrisk(self):
		"""
		https://openweathermap.org/api/road-risk

		Provides weather data and national alerts at the point of destination and along a route.
		"""
		return self.get_data(ROADRISK_URL)
