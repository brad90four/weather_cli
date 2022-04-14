import argparse
import datetime
import json
import os
import sys
from pathlib import Path
from urllib import error, request

from numpy import arange

import iso3166
from dotenv import load_dotenv
from loguru import logger
from rapidfuzz import process

root_dir = Path(__file__).parent
load_dotenv(root_dir.joinpath(".env"))
API_KEY = os.environ.get("API_KEY")
BASE_WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_API_URL = "http://api.openweathermap.org/data/2.5/forecast"
GEO_URL = "http://api.openweathermap.org/geo/1.0/direct"
PADDING = 20
THUNDERSTORM = range(200, 300)
DRIZZLE = range(300, 400)
RAIN = range(500, 600)
SNOW = range(600, 700)
ATMOSPHERE = range(700, 800)
CLEAR = range(800, 801)
CLOUDY = range(801, 900)


def read_user_cli_args(args: str) -> argparse.Namespace:
    """Handles the user input from the command line.

    Returns:
        argparse.Namespace: Populated namespace object.
    """
    parser = argparse.ArgumentParser(
        description="Gets weather and temperature info for a city."
    )
    parser.add_argument("city", nargs="+", type=str, help="Enter the city name.")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Display additional output for the query.",
    )
    parser.add_argument(
        "-f",
        "--forecast",
        action="store_true",
        help="Get the forecasted weather for the next 5 days.",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Run the script in debug mode for more detailed information.",
    )
    parser.add_argument(
        "-fd",
        "--forecast_days",
        action="store",
        type=float,
        default=1.0,
        choices=arange(0, 5.5, 0.5),
        help="Forecast with a custom number of days. Supports half days.",
    )
    parser.add_argument(
        "-c",
        "--country",
        # action="store",
        type=str,
        default="",
        help="Country to use in the query.",
    )
    parser.add_argument(
        "-u",
        "--units",
        nargs="+",
        action="store",
        type=str,
        default="imperial",
        choices=["metric", "imperial"],
        help="Units to use in the query.",
    )
    return parser.parse_args(args)


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


def _get_iso_country(input_country: str, debug: bool = False) -> str:
    """Get the ISO country code for a given country name.

    Args:
        input_country (str): Country name from user input.

    Returns:
        str: ISO country code.
    """
    try:
        if input_country.lower() in ("uk", "england"):
            country_code = "GB"
        elif input_country.lower() in ("usa", "united states"):
            country_code = "US"
        else:
            fuzzy_match_country = process.extractOne(
                input_country, iso3166.countries_by_name.keys()
            )[0]
            if debug:
                logger.debug(f"{fuzzy_match_country = }")
            country_code = iso3166.countries_by_name[fuzzy_match_country].alpha2
        if debug:
            logger.debug(f"Country code: {country_code} for: {input_country}")
    except KeyError:
        logger.error(f"{input_country} is not a valid country.")
        sys.exit(1)
    return country_code


def _get_lat_lon(city: str, country: str, debug: bool = False) -> tuple[str]:
    """Get the latitude and longitude for a given city and country.

    Args:
        city (str): City name from user input.
        country (str): Country name from user input.
        debug (bool): Whether to display debug information.

    Returns:
        tuple[str]: Latitude and longitude.
    """
    city = city[0].replace(" ", "%20")
    geo_url = f"{GEO_URL}?q={city},{country}&limit=5&appid={API_KEY}"
    if debug:
        logger.debug(f"{geo_url = }")
    try:
        response = request.urlopen(geo_url)
    except error.HTTPError as e:
        logger.error(e)
        sys.exit(1)

    data = json.loads(response.read().decode("utf-8"))
    if debug:
        logger.debug(data)
    lat, lon = data[0]["lat"], data[0]["lon"]
    return lat, lon


def display_weather_data(
    data: dict, verbose: bool = False, forecast: bool = False
) -> None:
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
            local_time = datetime.datetime.fromtimestamp(datestamp["dt"]).strftime(
                "%a, %B %d %I %p"
            )
            forecast_data[local_time] = {
                "temp": datestamp["main"]["temp"],
                "weather_type": datestamp["weather"][0]["description"],
                "weather_id": datestamp["weather"][0]["id"],
                "humidity": datestamp["main"]["humidity"],
                "wind_speed": datestamp["wind"]["speed"],
            }
            try:
                forecast_data[local_time]["rain"] = round(
                    datestamp["rain"]["3h"] * 0.0393701, 2
                )
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
            temp = forecast_data[datestamp]["temp"]
            weather_type = forecast_data[datestamp]["weather_type"]
            weather_emoji = _select_weather_display_emoji(
                forecast_data[datestamp]["weather_id"]
            )
            if verbose:
                humidity = forecast_data[datestamp]["humidity"]
                wind_speed = forecast_data[datestamp]["wind_speed"]
                try:
                    rainfall = forecast_data[datestamp]["rain"]
                except KeyError:
                    rainfall = 0
                print(
                    f"{datestamp:<{PADDING}} {weather_emoji} "
                    f"{weather_type.capitalize():<{PADDING}}{temp}°F, "
                    f"{rainfall}in rain, {humidity}% humidity, {wind_speed} mph"
                )
            else:
                print(
                    f"{datestamp:<{PADDING}} {weather_emoji} {weather_type.capitalize():<{PADDING}}{temp}°F"
                )
    if verbose:
        if forecast:
            pass  # already handled in forecast block
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


def build_weather_query(
    lat_lon: tuple[str], count: float, units: str, forecast: bool = False
) -> str:
    """Builds the url for an API request to OpenWeather's API.

    Args:
        lat_lon (tuple[str]): Latitude and Longitude of the location.
        count (float): Number of days to forecast.
        units (str): Units to use for the query.
        forecast (bool): Display the forecasted weather for the next 5 days.

    Returns:
        str: URL formatted for a call to the OpenWeather's city name endpoint.
    """
    if forecast:
        hour_stamps = round(8 * count)  # number of 3-hour blocks to use in API call
        url = (
            f"{FORECAST_API_URL}?lat={lat_lon[0]}&lon={lat_lon[1]}"
            f"&appid={API_KEY}&units={units}&cnt={hour_stamps}"
        )
    else:
        url = (
            f"{BASE_WEATHER_API_URL}?lat={lat_lon[0]}&lon={lat_lon[1]}"
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
            sys.exit(f"Invalid url: {query_url}")
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
    user_args = read_user_cli_args(sys.argv[1:])
    verbosity = True if user_args.verbose else False
    forecast = True if user_args.forecast else False
    debug = True if user_args.debug else False
    forecast_days = user_args.forecast_days
    units = user_args.units
    country = _get_iso_country(user_args.country, debug) if user_args.country else ""
    lat_lon = _get_lat_lon(user_args.city, country, debug)
    query_url = build_weather_query(lat_lon, forecast_days, units, forecast)
    weather_data = get_weather_data(query_url, debug)
    display_weather_data(weather_data, verbosity, forecast)
    if debug:
        logger.debug(f"{sys.argv[1:] = }")
        logger.debug(f"{user_args = }")
        logger.debug(f"{forecast_days = }")
        logger.debug(f"{units = }")
        logger.debug(f"{country = }")
        logger.debug(f"{lat_lon = }")
        logger.debug(f"{query_url = }")
        logger.debug(f"{weather_data = }")
