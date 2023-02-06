def v1_tc_order_fields(mockserver):
    # pylint: disable=protected-access
    # We need protected-access to use _variables_staring_with_underscore
    # in the @mockserver mock functions
    class OrderCoreOrderFieldsMockContext:
        _response = None
        _expected_order_id = None

        def set_expectations(self, order_id=None):
            self._expected_order_id = order_id

        def set_response(self, response):
            self._response = response

        @property
        def times_called(self):
            return _handler.times_called

    context = OrderCoreOrderFieldsMockContext()

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _handler(request):
        if context._expected_order_id is not None:
            assert request.json['order_id'] == context._expected_order_id
            assert request.json['search_archive'] is True
        return context._response

    return context
