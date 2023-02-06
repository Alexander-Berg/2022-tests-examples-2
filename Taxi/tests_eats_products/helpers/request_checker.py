import abc


class RequestCheckerBase(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def check(self, request) -> None:
        pass


class RequestChecker(RequestCheckerBase):
    def __init__(self):
        self._checkers = []

    def check(self, request) -> None:
        for checker in self._checkers:
            checker.check(request)

    def add(self, checker: RequestCheckerBase):
        self._checkers.append(checker)
        return self


class PlaceChecker(RequestCheckerBase):
    def check(self, request) -> None:
        assert 'place_id' in request.query
        assert isinstance(request.query['place_id'], str)
        assert request.query['place_id'].isdigit()


class ProductIdsChecker(RequestCheckerBase):
    def check(self, request) -> None:
        assert 'product_ids' in request.json
        assert request.json['product_ids']
        assert isinstance(request.json['product_ids'], list)


class ProductsWithIdsChecker(RequestCheckerBase):
    def check(self, request) -> None:
        assert 'products' in request.json
        assert request.json['products']
        assert isinstance(request.json['products'], list)


class OriginIdsInProductsChecker(RequestCheckerBase):
    def check(self, request) -> None:
        assert 'products' in request.json
        assert request.json['products']
        assert isinstance(request.json['products'], list)
        for item in request.json['products']:
            assert item['origin_id']


class CategoryIdsChecker(RequestCheckerBase):
    def check(self, request) -> None:
        assert 'category_ids' in request.json
        assert request.json['category_ids']
        assert isinstance(request.json['category_ids'], list)
