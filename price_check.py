import argparse
import datetime
import logging
import json
import requests
import re
from pattern.web import Element

from expedia_scraper import ExpediaScraper
from google_flights_API import GoogleFlights

logging.basicConfig(level=logging.DEBUG)


def parse_arguments():
    """
    Take in command line  arguments!
    """
    parser = argparse.ArgumentParser()

    # add these command line arg options
    parser.add_argument("departure_date", help="Provide departure date in MM/DD/YYYY")
    parser.add_argument("return_date", help="Provide return date in MM/DD/YYYY")
    parser.add_argument("departure_airport", help="Provide airport code, e.g. BWI")
    parser.add_argument("return_airport", help="Provide airport code, e.g. ICN")

    # parse these command line options
    arg = parser.parse_args()

    departure_date = arg.departure_date
    return_date = arg.return_date
    departure_airport = arg.departure_airport
    return_airport = arg.return_airport

    return departure_date, return_date, departure_airport, return_airport

def print_results(flight_info_list, departure_airport, return_airport):
    """
    Print the cheapest and fastest flights results to user
    """
    flight_info_list = sorted(flight_info_list, key=lambda k: k["price($)"])

    print "*********************************************************"
    print "Top 10 Cheapest Flights From {} to {}".format(
        departure_airport,
        return_airport
    )
    print "*********************************************************"

    for i in flight_info_list[:10]:
        print "----------------------------------"
        print json.dumps(i, indent=4)

    flight_info_list = sorted(flight_info_list, key=lambda k: k["flight_duration(hours)"])

    print "*********************************************************"
    print "Top 10 Shortest Flights From {} to {}".format(
        departure_airport,
        return_airport
    )
    print "*********************************************************"
    
    for i in flight_info_list[:10]:
        print "----------------------------------"
        print json.dumps(i, indent=4)

    print "--------------------------------------"
    print "Total of %s flights were found" % len(flight_info_list)
    print "--------------------------------------"

# grab command line arguments
departure_date, return_date, departure_airport, return_airport = parse_arguments()

flight_info_list = []

# convert string representation of a date into a datetime object
departure_date = datetime.datetime.strptime(departure_date, "%m/%d/%Y")
return_date = datetime.datetime.strptime(return_date, "%m/%d/%Y")

departure_date -= datetime.timedelta(days=1)
return_date -= datetime.timedelta(days=1)

# we want to check the dates around the initially provided dates to see
# if we can find any cheaper tickets
for x in range(3):
    for y in range(3):
        start_date = str(departure_date.month) + "/" + str(departure_date.day) + \
            "/" + str(departure_date.year)
        end_date = str(return_date.month) + "/" + str(return_date.day) + \
            "/" + str(return_date.year)

        # Scrape the expedia website to get flight data with given parameters
        # of departing and returning dates and airports
        scraper = ExpediaScraper(
            start_date,
            end_date,
            departure_airport,
            return_airport
        )

        # Use Google's QPX Express API to get flight data with given parameters
        google_flights = GoogleFlights(
            start_date,
            end_date,
            departure_airport,
            return_airport
        )

        # append flight data from Expedia deals
        flight_info_list.extend(scraper.get_flight_data_JSON())

        # append flight data from Google Flights
        flight_info_list.extend(google_flights.get_flight_data_JSON())

    return_date -= datetime.timedelta(days=3)
    departure_date += datetime.timedelta(days=1)

# finally print results
print_results(flight_info_list, departure_airport, return_airport)
