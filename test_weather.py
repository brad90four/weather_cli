import unittest

from loguru import logger
from weather import API_KEY, build_weather_query, read_user_cli_args

logger.level("INFO")


class TestWeather(unittest.TestCase):
    def test_read_user_cli_args(self):
        test_city_args = ["chattanooga"]
        test_city_namespace = read_user_cli_args(test_city_args)
        logger.debug(f"{test_city_namespace =}")
        self.assertEqual(test_city_namespace.city, ["chattanooga"])

        test_options_args = ["chattanooga", "-v", "-d", "-f"]
        test_options_namespace = read_user_cli_args(test_options_args)
        logger.debug(f"{test_options_namespace =}")
        self.assertEqual(test_options_namespace.city, ["chattanooga"])
        self.assertEqual(test_options_namespace.verbose, True)
        self.assertEqual(test_options_namespace.debug, True)
        self.assertEqual(test_options_namespace.forecast, True)

    def test_build_weather_query(self):
        test_city_input = ["chattanooga"]
        test_city_url = build_weather_query(test_city_input, count=1, forecast=False)
        default_city_url = (
            "http://api.openweathermap.org/data/2.5/weather"
            f"?q=chattanooga&appid={API_KEY}&units=imperial"
        )
        logger.debug(f"{test_city_url =}\n{default_city_url =}")
        self.assertEqual(test_city_url, default_city_url)

        test_forecast_url = build_weather_query(test_city_input, count=1, forecast=True)
        default_forecast_url = (
            "http://api.openweathermap.org/data/2.5/forecast"
            f"?q=chattanooga&appid={API_KEY}&units=imperial&cnt=8"
        )
        logger.debug(f"{test_forecast_url =}\n{default_forecast_url =}")
        self.assertEqual(test_forecast_url, default_forecast_url)

        test_count_url = build_weather_query(test_city_input, count=3, forecast=True)
        default_count_url = (
            "http://api.openweathermap.org/data/2.5/forecast"
            f"?q=chattanooga&appid={API_KEY}&units=imperial&cnt=24"
        )
        logger.debug(f"{test_count_url =}\n{default_count_url =}")
        self.assertEqual(test_count_url, default_count_url)

    # def test_get_weather_base(self):
    #     pass

    # def test_get_weather_forecast(self):
    #     pass


if __name__ == "__main__":
    unittest.main()
