class OrderCoreContext:
    def __init__(self):
        self._get_fields_response = {}
        self._driver_found = {}

    def reset(self):
        self._get_fields_response = {}
        self._driver_found = {}

    @property
    def get_fields_response(self):
        return self._get_fields_response

    @property
    def driver_found(self):
        return self._driver_found

    def set_get_fields_response(self, get_fields_response):
        self._get_fields_response = get_fields_response

    def set_driver_found(self, driver_found):
        self._driver_found = driver_found
