import argparse
import unittest

from loguru import logger
from weather import (
    API_KEY,
    _get_iso_country,
    _get_lat_lon,
    build_weather_query,
    read_user_cli_args,
)


def get_debug_flag() -> argparse.Namespace:
    """Get the debug flag from the command line

    Args:
        args (str): The command line arguments

    Returns:
        argparse.Namespace: The parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Get the debug flag from the command line"
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args()


class TestWeather(unittest.TestCase):
    debug = True

    def test_read_user_cli_args(self):
        test_city_args = ["-city", "chicago"]
        test_city_namespace = read_user_cli_args(test_city_args)
        if self.debug:
            logger.debug(f"{test_city_namespace =}")
            print(f"{test_city_namespace =}")
        self.assertEqual(test_city_namespace.city, ["chicago"])

        test_options_args = ["-city", "chicago", "-v", "-d", "-f"]
        test_options_namespace = read_user_cli_args(test_options_args)
        if self.debug:
            logger.debug(f"{test_options_namespace =}")
        self.assertEqual(test_options_namespace.city, ["chicago"])
        self.assertEqual(test_options_namespace.verbose, True)
        self.assertEqual(test_options_namespace.debug, True)
        self.assertEqual(test_options_namespace.forecast, True)

    def test_build_weather_query(self):
        test_city_url = build_weather_query(
            ("41.8755616", "-87.6244212"), count=1, units="imperial", forecast=False
        )
        default_city_url = (
            "http://api.openweathermap.org/data/2.5/weather"
            f"?lat=41.8755616&lon=-87.6244212&appid={API_KEY}&units=imperial"
        )
        if self.debug:
            logger.debug(f"{test_city_url =}\n{default_city_url =}")
        self.assertEqual(test_city_url, default_city_url)

        test_forecast_url = build_weather_query(
            ("41.8755616", "-87.6244212"), count=1, units="imperial", forecast=True
        )
        default_forecast_url = (
            "http://api.openweathermap.org/data/2.5/forecast"
            f"?lat=41.8755616&lon=-87.6244212&appid={API_KEY}&units=imperial&cnt=8"
        )
        if self.debug:
            logger.debug(f"{test_forecast_url =}\n{default_forecast_url =}")
        self.assertEqual(test_forecast_url, default_forecast_url)

        test_count_url = build_weather_query(
            ("41.8755616", "-87.6244212"), count=3, units="imperial", forecast=True
        )
        default_count_url = (
            "http://api.openweathermap.org/data/2.5/forecast"
            f"?lat=41.8755616&lon=-87.6244212&appid={API_KEY}&units=imperial&cnt=24"
        )
        if self.debug:
            logger.debug(f"{test_count_url =}\n{default_count_url =}")
        self.assertEqual(test_count_url, default_count_url)

    def test_get_country(self):
        test_england = [
            "United Kingdom of Great Britain and Northern Ireland",
            "United Kingdom",
            "UK",
            "England",
        ]
        for country in test_england:
            self.assertEqual(_get_iso_country(country), "GB")

        test_usa = [
            "United States of America",
            "United States",
            "USA",
        ]
        for country in test_usa:
            self.assertEqual(_get_iso_country(country), "US")

    def test_get_lat_lon(self):
        test_lat_lon = [
            ("London", "GB", (51.509865, -0.118092)),
            ("New York", "US", (40.730610, -73.935242)),
            ("Paris", "FR", (48.856614, 2.352222)),
            ("Tokyo", "JP", (35.689487, 139.691711)),
            ("Sydney", "AU", (-33.865143, 151.209900)),
            ("Moscow", "RU", (55.751244, 37.618423)),
            ("Beijing", "CN", (39.904211, 116.407395)),
            ("Seoul", "KR", (37.566535, 126.977969)),
            ("Cairo", "EG", (30.0444, 31.2357)),
            ("New Delhi", "IN", (28.613939, 77.209021)),
            ("Buenos Aires", "AR", (-34.603722, -58.381592)),
            ("Santiago", "CL", (-33.448891, -70.669265)),
            ("Bogota", "CO", (4.598056, -74.075833)),
            ("Lima", "PE", (-12.046374, -77.042793)),
            ("Brasilia", "BR", (-15.780167, -47.918611)),
            ("Sao Paulo", "BR", (-23.550520, -46.633309)),
            ("Mexico City", "MX", (19.432608, -99.133209)),
            ("Lagos", "NG", (6.455, 3.379206)),
            ("Kinshasa", "CD", (-4.329717, 15.313500)),
            ("Johannesburg", "ZA", (-26.202868, 28.039094)),
            ("Khartoum", "SD", (15.500656, 32.534180)),
            ("Dhaka", "BD", (23.710431, 90.407143)),
            ("Manila", "PH", (14.599512, 120.984219)),
            ("Tehran", "IR", (35.694389, 51.421528)),
        ]
        for city, country, lat_lon in test_lat_lon:
            lat, lon = _get_lat_lon(city, country)
            test_lat, test_lon = lat_lon
            try:
                self.assertEqual(
                    (round(lat, 0), round(lon, 0)),
                    (round(test_lat, 0), round(test_lon, 0)),
                )
            except AssertionError:
                logger.error(f"AssertionError: {lat, lon} != {test_lat, test_lon}")
                raise


if __name__ == "__main__":
    TestWeather.debug = get_debug_flag().debug
    runner = unittest.TextTestRunner()
    itersuite = unittest.TestLoader().loadTestsFromTestCase(TestWeather)
    runner.run(itersuite)
