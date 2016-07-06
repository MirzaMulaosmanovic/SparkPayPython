from sparkpayclient import SparkPayClient
from datetime import datetime
import mock
import unittest
import sys
import json


class MockResponse:
    def __init__(self, json_data, status_code, reason):
        self.status_code = status_code
        self.reason = reason
        self.json_data = json_data

    def json(self):
            return self.json_data

def mocked_requests_get_404(*args, **kwargs):
    return MockResponse({}, 404, 'Not Found')

def mocked_requests_get_429(*args, **kwargs):
    return MockResponse({}, 429, 'Over Rate Limit')

responsejson = '{"orders": [{ "id": 100000, "customer_id": 1, "customer_type_id": 0, "adcode": "", "ordered_at": "2013-11-29T17:12:00-06:00", "order_status_id": 5, "special_instructions": "", "subtotal": 2295, "tax_total": 191.4, "shipping_total": 25, "discount_total": 0, "grand_total": 2511.4, "cost_total": 0, "selected_shipping_method": "FedEx Express Saver", "ip_address": "127.0.0.1", "referrer": "", "order_shipping_address_id": 1, "order_billing_address_id": 1, "admin_comments": "", "source": "[none]", "search_phrase": "", "is_ppc": false, "ppc_keyword": "", "affiliate_id": null, "store_id": 1, "session_id": 363, "handling_total": 0, "is_payment_order_only": false, "selected_shipping_provider_service": "FEDEX_EXPRESS_SAVER", "additional_fees": 0, "adcode_id": 0, "updated_at": "2014-03-19T13:31:47.923-05:00", "created_at": "2013-11-29T17:12:08.16-06:00", "is_gift": false, "gift_message": "", "public_comments": "", "instructions": "", "source_group": "", "from_subscription_id": null, "previous_order_status_id": 2, "order_status_last_changed_at": "2014-03-19T13:31:47.923-05:00", "discounted_shipping_total": 25, "order_number": "", "coupon_code": "", "order_type": "Order", "expires_at": null, "expires": false, "from_quote_id": null, "campaign_code": "", "reward_points_credited": false }]}'

def mocked_requests_get_200(*args, **kwargs):
    return MockResponse(json.loads(responsejson), 200, 'Success')

def mocked_requests_get_empty_200(*args, **kwargs):
    return MockResponse({}, 200, 'Success')

class SparkPayClientTestCase(unittest.TestCase):

    def test_getrequestheaders_ReturnsAuthHeader(self):
        client = SparkPayClient('foo', 'bar')
        headers = client.getrequestheaders();
        
        self.assertEqual('bar', headers['X-AC-Auth-Token'])

    def test_getrequestheaders_ReturnsMimeHeader(self):
        client = SparkPayClient('foo', 'bar')
        headers = client.getrequestheaders();
        
        self.assertEqual('application/json', headers['Content-Type'])

    @mock.patch('sparkpayclient.requests.get', side_effect=mocked_requests_get_404)
    def test_getorders_ThrowsException_WhenResponseCodeIsUnknown(self, mock_get):
        client = SparkPayClient('foo', 'bar')
        with self.assertRaises(Exception) as context:
            client.getorders('2015-01-01')
        ex = context.exception

        self.assertEqual('Unknown error occured Not Found', ex.message)

    @mock.patch('sparkpayclient.requests.get', side_effect=mocked_requests_get_429)
    def test_getorders_ThrowsException_WhenResponseCodeOverRateLimit(self, mock_get):
        client = SparkPayClient('foo', 'bar')
        with self.assertRaises(Exception) as context:
            client.getorders('2015-01-01')
        ex = context.exception

        self.assertEqual('Api request limit reached, please wait a few seconds before trying again.', ex.message)

    @mock.patch('sparkpayclient.requests.get', side_effect=mocked_requests_get_200)
    def test_getorders_ReturnsOrdersList(self, mock_get):
        client = SparkPayClient('foo', 'bar')
        orders = client.getorders('2015-01-01')

        self.assertEqual(1, len(orders))
        self.assertTrue(isinstance(orders, list))
        
    @mock.patch('sparkpayclient.requests.get', side_effect=mocked_requests_get_empty_200)
    def test_getorders_ReturnsEmptyList(self, mock_get):
        client = SparkPayClient('foo', 'bar')
        orders = client.getorders('2015-01-01')

        self.assertEqual(0, len(orders))
        self.assertTrue(isinstance(orders, list))

    @mock.patch('sparkpayclient.requests.get', side_effect=mocked_requests_get_empty_200)
    def test_getorders_CallsRequestsGet_WithStoreUrlAndStartDate(self, mock_get):
        client = SparkPayClient('http://storeurl.com', 'bar')
        start = datetime.utcnow()
        headers = client.getrequestheaders()

        orders = client.getorders(start)

        self.assertIn(mock.call('http://storeurl.com/api/v1/orders?updated_at=gt:' + start.isoformat(), headers=headers ), mock_get.call_args_list)


if __name__ == '__main__':
    unittest.main()