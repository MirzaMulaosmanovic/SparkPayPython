"""Client used to interact with the SparkPay API """

import requests
import dateutil.parser as parser

class SparkPayClient(object):
    """The :class:`SparkPayClient <SparkPayClient>` object,
    used to interact with the SparkPay API
    """

    def __init__(self, basestoreurl, authtoken):
        """Initializes the SparkPayClient with the given store URL and token"""

        #: the SparkPay base store url
        self.basestoreurl = basestoreurl

        #: the SparkPay auth token
        self.authtoken = authtoken

    def getorders(self, startdate):
        """Gets order data from the SparkPay API

        :param startdate: Start date from which to request orders
        :returns dictionary of orders
        :rtype: dict
        """

        # parse date time string into dateTime object
        if isinstance(startdate, basestring):
            startdate = parser.parse(startdate)

        headers = self.getrequestheaders()
        requesturl = self.basestoreurl + '/api/v1/orders?updated_at=gt:' + startdate.isoformat()

        # make a GET request to the orders api using the start date provided
        response = requests.get(requesturl, headers=headers)

        # if the response is valid return a dictionary of orders
        if response.status_code == 200:
            responsejson = response.json()

            if 'orders' in responsejson:
                return responsejson['orders']
            else:
                return list()

        elif response.status_code == 429:
            # per the documentation a 429 means that the rate limit has been exceeded
            raise Exception('Api request limit reached, '+
                            'please wait a few seconds before trying again.')
        else:
            # something went wrong, inspect the response for info
            self.__rethrowexception(response)

    def __rethrowexception(self, response):
        reason = response.reason
        message = ''
        details = ''
        exmessage = 'Unknown error occured' + ' ' + reason

        # so that we dont have to load the json multiple times save it to a variable
        responsejson = response.json()

        # check to see if the response contains more info about what went wrong
        if 'message' in responsejson:
            message = responsejson['message']
        if 'details' in responsejson:
            details = responsejson['details']

        if message != '':
            exmessage = exmessage + message

        if message != '':
            exmessage = exmessage + ': ' + details

        raise Exception(exmessage)

    def getrequestheaders(self):
        """Gets the headers for requests to the SparkPay API"""
        return {'Content-Type': 'application/json', 'X-AC-Auth-Token': self.authtoken}
