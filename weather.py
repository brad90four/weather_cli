import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path
from urllib import error, parse, request

from dotenv import load_dotenv
from loguru import logger


root_dir = Path(__file__).parent
load_dotenv(root_dir.joinpath(".env"))
API_KEY = os.environ.get("API_KEY")
BASE_WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_API_URL = "http://api.openweathermap.org/data/2.5/forecast"
PADDING = 20
THUNDERSTORM = range(200, 300)
DRIZZLE = range(300, 400)
RAIN = range(500, 600)
SNOW = range(600, 700)
ATMOSPHERE = range(700, 800)
CLEAR = range(800, 801)
CLOUDY = range(801, 900)


def read_user_cli_args() -> argparse.Namespace:
    """Handles the user input from the command line.

    Returns:
        argparse.Namespace: Populated namespace object.
    """
    parser = argparse.ArgumentParser(
        description="gets weather and temperature info for a city"
    )
    parser.add_argument(
        "city",
        nargs="+",
        type=str,
        help="enter the city name"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="display additional output for the query",
    )
    parser.add_argument(
        "-f",
        "--forecast",
        action="store_true",
        help="get the forecasted weather for the next 5 days",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="run the script in debug mode for more detailed information",
    )
    return parser.parse_args()


def _select_weather_display_emoji(weather_id: int) -> str:
    """Add an emoji based on the weather ID.

    Args:
        weather_id (int): Weather ID number given by the API.

    Returns:
        display_emoji (str): The emoji for a given weather ID.
    """
    if weather_id in THUNDERSTORM:
        display_emoji = "💥"
    elif weather_id in DRIZZLE:
        display_emoji = "💧"
    elif weather_id in RAIN:
        display_emoji = "💦"
    elif weather_id in SNOW:
        display_emoji = "⛄️"
    elif weather_id in ATMOSPHERE:
        display_emoji = "🌀"
    elif weather_id in CLEAR:
        display_emoji = "🔆"
    elif weather_id in CLOUDY:
        display_emoji = "💨"
    else:  # In case the API adds new weather codes
        display_emoji = "🌈"

    return display_emoji


def display_weather_data(data: dict, verbose: bool = False, forecast: bool = False) -> None:
    """Displays the weather data from the API response.

    Args:
        data (dict): JSON response from the API.
        verbose (bool): Display additional output for the query.
        forecast (bool): Display the forecasted weather for the next 5 days.
    """
    if forecast:
        city = data["city"]["name"]
        forecast_data = {}
        for datestamp in data["list"]:
            local_time = datetime.datetime.fromtimestamp(datestamp["dt"]).strftime("%Y-%m-%d %H:%M")
            forecast_data[local_time] = {
                "temp": datestamp["main"]["temp"],
                "weather_type": datestamp["weather"][0]["description"],
                "weather_id": datestamp["weather"][0]["id"],
                "humidity": datestamp["main"]["humidity"],
                "wind_speed": datestamp["wind"]["speed"]
            }
            try:
                forecast_data[local_time]["rain"] = round(datestamp["rain"]["3h"] * 0.0393701, 2)
            except KeyError:
                pass

    else:
        city = data["name"]
        temp = data["main"]["temp"]
        weather_id = data["weather"][0]["id"]
        weather_emoji = _select_weather_display_emoji(weather_id)
        weather_type = data["weather"][0]["description"]
        print(
            f"{city:<{PADDING}} {weather_emoji} {weather_type.capitalize():<{PADDING}}{temp}°F"
        )
    if forecast:
        for datestamp in forecast_data:
            #logger.debug(f"{datestamp = }")
            temp = forecast_data[datestamp]["temp"]
            weather_type = forecast_data[datestamp]["weather_type"]
            weather_emoji = _select_weather_display_emoji(forecast_data[datestamp]["weather_id"])
            if verbose:
                humidity = forecast_data[datestamp]["humidity"]
                wind_speed = forecast_data[datestamp]["wind_speed"]
                try:
                    rainfall = forecast_data[datestamp]["rain"]
                except KeyError:
                    rainfall = 0
                print(
                    f"{datestamp:<{PADDING}} {weather_emoji} "
                    f"{weather_type.capitalize():<{PADDING}}{temp}°F "
                    f"{rainfall}in rain, {humidity}% humidity, {wind_speed} mph"
                )
            else:
                print(
                    f"{datestamp:<{PADDING}} {weather_emoji} {weather_type.capitalize():<{PADDING}}{temp}°F"
                )
    if verbose:
        if forecast:
            pass
        else:
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]
            min_temp = data["main"]["temp_min"]
            max_temp = data["main"]["temp_max"]
            try:
                rainfall = round(data["rain"]["3h"] * 0.0393701, 2)
            except KeyError:
                rainfall = 0
            print(
                f"Max:{max_temp}°F | Min:{min_temp}°F | "
                f"{rainfall}in rain | {humidity}% humidity | {wind_speed} mph"
            )


def build_weather_query(city_input: list[str], forecast: bool = False) -> str:
    """Builds the url for an API request to OpenWeather's API.

    Args:
        city_input (List[str]): Name of a city from user input.
        forecast (bool): Display the forecasted weather for the next 5 days.

    Returns:
        str: URL formatted for a call to the OpenWeather's city name endpoint.
    """
    city_name = " ".join(city_input)
    url_encoded_city_name = parse.quote_plus(city_name)
    units = "imperial"
    if forecast:
        count = 8  # number of 3-hour blocks to use in API call
        url = (
            f"{FORECAST_API_URL}?q={url_encoded_city_name}"
            f"&appid={API_KEY}&units={units}&cnt={count}"
        )
    else:
        url = (
            f"{BASE_WEATHER_API_URL}?q={url_encoded_city_name}"
            f"&appid={API_KEY}&units={units}"
        )
    return url


def get_weather_data(query_url: str, debug: bool = False) -> dict:
    """Makes an API request to a given URL and returns the response.

    Args:
        query_url (str): URL formatted for a call to the OpenWeather's city name endpoint.
        debug (bool): Display additional output for the query.

    Returns:
        dict: JSON response from the API.
    """
    try:
        response = request.urlopen(query_url)
    except error.HTTPError as http_error:
        if http_error.code == 401:
            sys.exit("Invalid API key. Please check your API key.")
        elif http_error.code == 404:
            pattern = r"q=([\w|+]*)&"
            group_match = re.search(pattern, query_url).group(0)
            city = group_match.replace("q=", "").replace("&", "").replace("+", " ")
            sys.exit(f"Can't find city name: {city}")
        else:
            sys.exit(f"HTTP Error: {http_error.code}")

    data = response.read()
    try:
        if debug:
            logger.debug(json.loads(data))
        return json.loads(data)
    except json.JSONDecodeError:
        sys.exit("JSON decode error")


if __name__ == "__main__":
    user_args = read_user_cli_args()
    verbosity = True if user_args.verbose else False
    forecast = True if user_args.forecast else False
    debug = True if user_args.debug else False
    query_url = build_weather_query(user_args.city, forecast)
    weather_data = get_weather_data(query_url, debug)
    display_weather_data(weather_data, verbosity, forecast)
