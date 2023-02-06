from copy import deepcopy

from pytest import raises

from rtnmgr_agent.document import Document


class TestConfig:
    def setup(self):
        self.document = Document()
        self.object = {
            "code": 200,
            "data": {
                "rotation_id": 137,
                "static": [
                    {
                        "provider": "telia",
                        "int_ip": "20.20.20.20",
                        "timestamp": "",
                        "ext_ip": "200.200.200.200",
                        "pool": "pool.with.static.mapping",
                    }
                ],
                "current": [
                    {
                        "provider": "telia",
                        "int_ip": "5.45.202.135",
                        "timestamp": "2020-08-19 15:19:05.755399",
                        "pool": "market.yandex.ua",
                        "ext_ip": "80.239.201.45",
                    }
                ],
            },
            "error_message": None,
            "status": "success",
        }

    def test_valid(self):
        assert self.document.raise_if_invalid(self.object) is None

        # raise Value Error: document doesn't contain version error
        document = deepcopy(self.object)
        del document["data"]["rotation_id"]

        with raises(ValueError):
            self.document.raise_if_invalid(document)

    def test_save(self):
        assert self.document.save(self.object)

        assert self.document.is_equal_id(137)
        assert not self.document.is_equal_id(123)

    def test_update(self):
        assert self.document.update(self.object)
        assert not self.document.update(self.object)

    def test_show(self):
        assert self.document.save(self.object)
        assert self.object == self.document.show()
