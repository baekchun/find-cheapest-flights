import datetime
import logging
import json
import requests
import re
from pattern.web import Element

logging.basicConfig(level=logging.DEBUG)

class ExpediaScraper():
    """
    Let's scrape Expedia and find some cheap flights!
    """

    # this one is for roundtrip
    REQUEST_ID_REGEX = r"data-leg-natural-key=\"(\w+)\">"

    def __init__(self, departure_date, return_date, departure_airport, return_airport):
        self.departure_date = departure_date
        self.return_date = return_date
        self.departure_airport = departure_airport
        self.return_airport = return_airport

        self.formatted_url = self.format_base_url()

        get_request = requests.get(self.formatted_url)

        self.e = Element(get_request.content)

        self.departure_request_id = self.get_departure_flight_request_ID()

        self.arrival_request_id = self.get_return_flight_request_ID()

        self.json_url = self.get_flight_data_JSON_URL()

    def format_base_url(self):
        """
        Parse command line arguments and format the base url to get the
        target URL
        """

        # this will be formatted with info provided by hte user
        base_url = "https://www.expedia.com/Flights-Search?trip=roundtrip"\
            "&leg1=from:{DEPT_AIRPORT},to:{RETURN_AIRPORT},departure:{DEPT_DATE}TANYT"\
            "&leg2=from:{RETURN_AIRPORT},to:{DEPT_AIRPORT},departure:{RETURN_DATE}TANYT"\
            "&passengers=adults:1,children:0,seniors:0,infantinlap:Y&options=cabinclass"\
            "%3Aeconomy&mode=search&origref=www.expedia.com"

        formatted_url = base_url.format(
            DEPT_AIRPORT=self.departure_airport,
            RETURN_AIRPORT=self.return_airport,
            DEPT_DATE=self.departure_date,
            RETURN_DATE=self.return_date
        )

        return formatted_url

    def get_departure_flight_request_ID(self):
        """
        This departure flight request ID is needed when making a get request
        """
        # this id is used to make a request to get the depature flights JSON data
        departure_request_id = self.e("div#originalContinuationId")[0].content

        return departure_request_id

    def get_return_flight_request_ID(self):
        """
        This return flight request ID is needed when making a get request
        """

        # this text includes unique id used to make request to get return flights JSON data
        arrival_request_content = self.e("div.flex-card")[0].content

        arrival_request_id = re.search(self.REQUEST_ID_REGEX, arrival_request_content)

        try:
            arrival_request_id = arrival_request_id.group(1)
        except AttributeError:
            logging.debug("Cannot find arrival request ID!")

            arrival_request_id = ""

        return arrival_request_id

    def get_flight_data_JSON_URL(self):

        # this URL gets us to a page of flight data in JSON format
        json_url = "https://www.expedia.com/Flight-Search-Paging?c={DEPT_ID}&is=1" \
            "&fl0={ARRV_ID}&sp=asc&cz=200&cn=0&ul=1"

        # insert the two request ids
        json_url = json_url.format(
            DEPT_ID=self.departure_request_id,
            ARRV_ID=self.arrival_request_id
        )

        return json_url

    def get_flight_data_JSON(self):
        """
        First make a get request and process the json to make it into a list
        of dicts in which each dict contains flgith information
        """

        # make a GET request
        get_request = requests.get(self.json_url)
        e = Element(get_request.content)

        # convert json into dict
        data_dict = json.loads(e.content)

        # get just the flight-related data
        data_dict = data_dict["content"]["legs"]

        # check if it returned anything
        if not data_dict:
            return []

        flight_info_list = []

        for key in data_dict.keys():
            if data_dict[key]["price"]["totalPriceAsDecimal"]:

                # only create dict if the price exists for this flight
                single_flight_dict = {
                    "price($)": data_dict[key]["price"]["totalPriceAsDecimal"],
                    "flight_duration(hours)": data_dict[key]["duration"]["hours"] + \
                        data_dict[key]["duration"]["minutes"] / float(60),
                    "source": "Expedia",
                    "departure_date": self.departure_date,
                    "return_date": self.return_date
                }

                # append this dict to flight info list
                flight_info_list.append(single_flight_dict)

        return flight_info_list
