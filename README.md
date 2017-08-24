# find-cheapest-flights

Find the cheapest or shortest roundtrip flights by comparing prices from Expedia and Google Flights. Given your departing and arriving airports and dates, this scraper tries to find the cheapest or shortest flights. Please note that this scraper looks for flights +/- 1 day of the given dates as well to check to see if we can find any cheaper flights.


## Getting Started

Note: This code has been tested/optimized for Python 2.x

### Prerequisites

Please make sure to install these packages before trying to run this code!

```
pip install pattern
```
```
pip install requests
```

### How to run this code:

```
python price_check.py [departure_date] [return_date] [departure_airport] [return_airport]
```

### Example:
```
python price_check.py 08/30/2017 09/30/2017 BWI ICN
```

## Authors

* **Baekchun Kim** 
