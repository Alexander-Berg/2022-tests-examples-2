NAME = 'fines-1c'


def _handler_retrieve(context):
    def handler(request):
        return context['fines_response']

    return handler


def _handler_add(context):
    def handler(request):
        cars = []
        for car in request.json:
            car_new = car.copy()
            car_new.update({'error': False})
            cars.append(car_new)
        return cars

    return handler


def _handler_change_activity(context):
    def handler(request):
        cars = []
        for car in request.json:
            car_new = car.copy()
            car_new.update({'error': False})
            cars.append(car_new)
        return cars

    return handler


def _handler_foto(context):
    def handler(request):
        return 'BINARY_FOTO'

    return handler


def _handler_foto_404(context):
    def handler(request, mockserver):
        return mockserver.make_response(status=404)

    return handler


def _handler_company(context):
    def handler(request):
        return []

    return handler


def setup(context, mockserver):
    mocks = {}

    def add(url, handler):
        mocks[url] = mockserver.json_handler('/' + NAME + url)(handler)

    add('/Fines/v1/Load', _handler_retrieve(context))
    add('/Car/v1/Add', _handler_add(context))
    add('/Car/v1/ChangeActivity', _handler_change_activity(context))
    add('/Fines/v1/FOTO/FINE_UIN_01/1', _handler_foto(context))
    add('/Fines/v1/FOTO/FINE_UIN_01/2', _handler_foto_404(context))
    add('/Company/v1/Add', _handler_company(context))
    add('/Company/v1/ChangeActivity', _handler_company(context))

    return mocks
