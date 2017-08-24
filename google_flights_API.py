import logging
import json
import re
import requests
from pattern.web import Element

logging.basicConfig(level=logging.DEBUG)


class GoogleFlights():
    """
    Use Google Flights API to grab flight data
    """

    # regex to capture month, day, year
    MM_DD_YYYY_REGEX = r"(\d{1,2})\/(\d{1,2})\/(\d{4})"

    google_flight_api = "https://www.googleapis.com/qpxExpress/v1/trips/search?key={API_KEY}"

    # create your own Google API key and insert here 
    api_key = ""

    def __init__(self, departure_date, return_date, departure_airport, return_airport):
        self.url = self.google_flight_api.format(API_KEY=self.api_key)
        self.departure_date = self.modify_date(departure_date)
        self.return_date = self.modify_date(return_date)
        self.departure_airport = departure_airport
        self.return_airport = return_airport

        self.data_dict = self.create_data_dict()

    def modify_date(self, date):
        """
        Convert the date from this format MM/DD/YYYY to YYYY-MM-DD
        """

        has_date = re.search(self.MM_DD_YYYY_REGEX, date)
        try:
            month = has_date.group(1)
            day = has_date.group(2)
            year = has_date.group(3)
        except AttributeError:
            logging.warning("The provided date is invalid, please provide the date" \
                "in this format: MM/DD/YYYY")

        return year + "-" + month + "-" + day 

    def create_data_dict(self):
        """
        Given this data dict, add outbound and inbound flight details
        """

        # from this data dict, just add the origin, destination and dates
        data = {
            "request": {
                "slice": [
                {
                    "origin": "",
                    "destination": "",
                    "date": ""
                },
                {
                    "origin": "",
                    "destination": "",
                    "date": ""
                }
                ],
                "passengers": {
                    "adultCount": 1,
                    "infantInLapCount": 0,
                    "infantInSeatCount": 0,
                    "childCount": 0,
                    "seniorCount": 0
                },
                "solutions": 50,
                "refundable": False
            }
        }

        # first set the outbound flight fields
        data["request"]["slice"][0]["origin"] = self.departure_airport
        data["request"]["slice"][0]["destination"] = self.return_airport
        data["request"]["slice"][0]["date"] = self.departure_date

        # now set the inbound flight fields
        data["request"]["slice"][1]["origin"] = self.return_airport
        data["request"]["slice"][1]["destination"] = self.departure_airport
        data["request"]["slice"][1]["date"] = self.return_date

        return data

    def get_flight_data_JSON(self):
        """
        First make a post request to get the flight JSON data. Then process
        it to create a list of dicts in which each dict contains a flight
        information
        """

        # first make a post request to google flights API to grab flight data
        re = requests.post(
            self.url,
            data=json.dumps(self.data_dict),
            headers={
                'Content-Type': 'application/json'
            }
        )

        # convert the response string into a dict
        data = json.loads(re.content)

        data = data["trips"]["tripOption"]
        
        # check if it returned anything
        if not data:
            return []

        # initialize a list of flight dictionaries
        flight_info_list = []

        # NOTE: the returned dict contains 10 results
        for idx in range(len(data)):
            # first remove USD substring and change it to float
            price = float(data[idx]["saleTotal"].replace("USD", ""))

            single_flight_dict = {
                "price($)": float(data[idx]["saleTotal"].replace("USD", "")),
                # flight duration should be in hours
                "flight_duration(hours)": data[idx]["slice"][0]["duration"] / float(60),
                "source": "Google Flights",
                "depature_date": self.departure_date,
                "return_date": self.return_date
            }
            flight_info_list.append(single_flight_dict)

        return flight_info_list
