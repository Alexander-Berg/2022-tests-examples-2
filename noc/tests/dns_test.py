import pytest
import responses

from s3_json.dns import DNSClient


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


class TestDNSAPI:
    def setup(self):
        self.client = DNSClient()

    def test_json(self, mocked_responses):
        mocked_responses.add(
            responses.GET,
            DNSClient.DNS_API_URL,
            json={
                "items": [
                    {
                        "addresses": ["154.47.36.55", "80.239.201.71"],
                        "fqdn": "www.yandex.ru.",
                        "ns": "ns1+ns2",
                        "ns-type": "static",
                        "proxy": "cogent+telia",
                        "ttl": 300,
                        "type": "A",
                        "view": "VIEW_UA",
                        "zone": "yandex.ru",
                    },
                    {
                        "addresses": ["80.239.201.92", "154.47.36.12", "2a02:6b8::21b"],
                        "fqdn": "market.yandex.ua.",
                        "ns": "ns3+ns4",
                        "ns-type": "dynamic",
                        "proxy": "cogent+telia",
                        "ttl": 900,
                        "type": "AAAA",
                        "view": "VIEW_UA",
                        "zone": "market.yandex.ua",
                    },
                ]
            },
            status=200,
            content_type="application/json",
        )

        json_payload = self.client.json_view()

        assert "www.yandex.ru." in [rec.get("fqdn") for rec in json_payload.get("items")]
        assert {
            "addresses": ["80.239.201.92", "154.47.36.12", "2a02:6b8::21b"],
            "fqdn": "market.yandex.ua.",
            "ns": "ns3+ns4",
            "ns-type": "dynamic",
            "proxy": "cogent+telia",
            "ttl": 900,
            "type": "AAAA",
            "view": "VIEW_UA",
            "zone": "market.yandex.ua",
        } in json_payload.get("items")

    def test_filtered(self, mocked_responses):
        mocked_responses.add(
            responses.GET,
            DNSClient.DNS_API_URL,
            json={
                "items": [
                    {
                        "addresses": ["154.47.36.55", "80.239.201.71"],
                        "fqdn": "www.yandex.ru.",
                        "ns": "ns1+ns2",
                        "ns-type": "static",
                        "proxy": "cogent+telia",
                        "ttl": 300,
                        "type": "A",
                        "view": "VIEW_UA",
                        "zone": "yandex.ru",
                    }
                ]
            },
        )

        view_payload = self.client.filtered_view()

        assert "timestamp" in view_payload
        assert {
            "addresses": ["154.47.36.55", "80.239.201.71"],
            "fqdn": "www.yandex.ru.",
        } in view_payload.get("items")
