from s3_json.dns import DNSClient


class TestIntegrationDNSAPI:
    """
    Integration test: using DNS API call in runtime.
    """

    def setup(self):
        self.client = DNSClient()

    def test_json(self):
        json_payload = self.client.json_view()

        assert json_payload
        assert len(json_payload.get("items", []))
        for item in json_payload.get("items", []):
            assert item.get("addresses")
            assert item.get("fqdn")
            assert item.get("ttl", 0)

    def test_filtered(self):
        view_payload = self.client.filtered_view()

        assert view_payload
        assert len(view_payload.get("items", []))
        for item in view_payload.get("items", []):
            assert item.get("addresses")
            assert item.get("fqdn")
            assert item.get("ttl") is None
