import allure


class MockJugglerApi:
    def __init__(self, *args, **kwargs):
        self.downtimes = set()

    def set(self, host, **kwargs):
        allure.attach("MockJugglerApi set downtime", f'host {host}')
        self.downtimes.add(host)

    def remove(self, host, **kwargs):
        allure.attach("MockJugglerApi remove downtime", f'host {host}')
        self.downtimes.discard(host)
