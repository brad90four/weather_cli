# weather_cli

## A command line program for weather updates

### Usage:
```py
-> py weather.py
usage: weather.py [-h] [-v] [-f] [-d] [-c COUNT] city [city ...]

-> py weather.py New York City
New York             💨 Few clouds          68.14°F

➜ py weather.py New York City -v
New York             💨 Few clouds          68.14°F
Max:82.02°F | Min:58.95°F | 0in rain | 69% humidity | 5.99 mph

➜ py weather.py New York City -f
2022-04-13 17:00     💨 Broken clouds       67.69°F
2022-04-13 20:00     💨 Broken clouds       66°F
2022-04-13 23:00     💦 Light rain          63.43°F
2022-04-14 02:00     💨 Overcast clouds     62.2°F
2022-04-14 05:00     💨 Overcast clouds     62.73°F
2022-04-14 08:00     💨 Overcast clouds     62.87°F
2022-04-14 11:00     💨 Scattered clouds    71.1°F
2022-04-14 14:00     💨 Broken clouds       77.52°F

➜ py weather.py New York City -f -v -c 0.5
2022-04-13 17:00     💨 Broken clouds       67.69°F, 0in rain, 65% humidity, 5.73 mph
2022-04-13 20:00     💨 Broken clouds       66°F, 0in rain, 65% humidity, 4.83 mph
2022-04-13 23:00     💦 Light rain          63.43°F, 0.04in rain, 83% humidity, 5.39 mph
2022-04-14 02:00     💨 Overcast clouds     62.2°F, 0in rain, 81% humidity, 7.43 mph