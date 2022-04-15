# weather_cli

## A command line program for weather updates

### Usage:
```py
➜ py weather.py
usage: weather.py [-h] [-v] [-f] [-d] [-fd {0.0,0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0}]
                  [-c COUNTRY] [-u {metric,imperial}]
                  city [city ...]

➜ py weather.py new york city
New York             🔆 Clear sky           52.63°F

➜ py weather.py new york city -v
New York             🔆 Clear sky           53.4°F
Max:56.98°F | Min:48.18°F | 0in rain | 53% humidity | 5.75 mph

➜ py weather.py new york city -f --forecast-days 0.5
Fri, April 15 08 AM  🔆 Clear sky           53.11°F
Fri, April 15 11 AM  🔆 Clear sky           55.6°F
Fri, April 15 05 PM  🔆 Clear sky           65.52°F

➜ py weather.py new york city -f --forecast-days 0.5 -v -u metric
Fri, April 15 08 AM  🔆 Clear sky           11.73°C, 0in rain, 52% humidity, 3.84 mph
Fri, April 15 11 AM  🔆 Clear sky           13.11°C, 0in rain, 42% humidity, 3.56 mph
Fri, April 15 02 PM  🔆 Clear sky           16.14°C, 0in rain, 32% humidity, 4.7 mph
Fri, April 15 05 PM  🔆 Clear sky           18.62°C, 0in rain, 29% humidity, 5.24 mph
```