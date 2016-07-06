This is a simple [SparkPay](https://github.com/SparkPay/rest-api) client for python. 

#### Usage
The getorders method will return a list of orders that have been modified after the given start date.
```python
from sparkpayclient import SparkPayClient

client = SparkPayClient("http://somesparkpayurl.com", "authtoken")

for order in client.getorders('2016-07-05'):
    print order['id']
```

#### Tests

```
>$ python test_sparkpayclient.py
```