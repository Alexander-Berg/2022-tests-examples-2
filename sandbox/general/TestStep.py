import json


class TestStep:
    def __init__(self, order, name,
                 host1, host2, method,
                 url, query_params, headers,
                 body=None, expected_status_codes=None,
                 extract=None, ignore_paths=None):
        self.order_id = order
        self.name = name
        self.ignore_paths = ignore_paths
        self.request1 = {
            "host": host1,
            "method": method,
            "query_params": query_params,
            "url": url,
            "headers": json.dumps(headers),
            "body": json.dumps(body)
        }
        self.request2 = {
            "host": host2,
            "method": method,
            "query_params": query_params,
            "url": url,
            "headers": json.dumps(headers),
            "body": json.dumps(body)
        }
        self.expected_status_codes = expected_status_codes
        self.extract = extract
