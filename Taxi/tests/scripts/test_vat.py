import aiohttp
import pytest
import yarl
from aiohttp import web

from stall import cfg
from stall.client.woody import WoodyClient
from stall.scripts import vat


class MockResponse:
    def __init__(self, status, data):
        self.status = status
        self._data = data

    async def json(self):
        return self._data

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self


@pytest.fixture
def mock_response(monkeypatch):
    # pylint: disable=unused-argument
    def mock_get(*args, **kwargs):
        return MockResponse(
            status=200,
            data={
                'code': 'OK',
                'products': [
                    {
                        'code': 'code1',
                        'vat': 11,
                        'vat_number': '444',
                    },
                    {
                        'code': 'code2',
                        'vat': 19,
                        'vat_number': None,
                    },
                    {
                        'code': 'code3',
                        'vat': 0,
                        'vat_number': '666',
                    },
                    {
                        'code': 'code4',
                        'vat': -1,
                        'vat_number': '777',
                    },
                    {
                        'code': 'code5',
                        'vat': None,
                        'vat_number': None,
                    },
                ],
            }
        )

    monkeypatch.setattr(aiohttp.ClientSession, 'get', mock_get)


# pylint: disable=redefined-outer-name,unused-argument
async def test_update_vat(tap, dataset, mock_response):
    product1 = await dataset.product(external_id='code1')
    product1.products_scope = ['russia']
    await product1.save()
    product2 = await dataset.product(external_id='code2')
    product2.products_scope = ['russia']
    product2.vars['supplier_tin'] = '555'
    await product2.save()
    product3 = await dataset.product(external_id='code3')
    product3.products_scope = ['russia']
    product3.vat = 69
    await product3.save()

    product4 = await dataset.product(external_id='code4')
    product4.products_scope = ['russia']
    product4.vat = 68
    await product4.save()

    product5 = await dataset.product(external_id='code5')
    product5.products_scope = ['russia']
    product5.vat = 67
    product5.vars['supplier_tin'] = '888'
    await product5.save()

    await vat.update_products_vat(
        'http://example.com/vat', 'login', 'password')

    await product1.reload()
    await product2.reload()
    await product3.reload()
    await product4.reload()
    await product5.reload()

    with tap.plan(10):
        tap.eq_ok(product1.vat, 11, 'product1.vat==11')
        tap.eq_ok(product2.vat, 19, 'product2.vat==19')
        tap.eq_ok(product3.vat, 0, 'product3.vat==0')
        tap.eq_ok(product4.vat, 68, 'product4.vat==68')
        tap.eq_ok(product5.vat, 67, 'product5.vat==67')
        tap.eq_ok(product1.vars['supplier_tin'], '444', 'совпадают')
        tap.eq_ok(product2.vars['supplier_tin'], '555', 'совпадают')
        tap.eq_ok(product3.vars['supplier_tin'], '666', 'совпадают')
        tap.eq_ok(product4.vars['supplier_tin'], '777', 'совпадают')
        tap.eq_ok(product5.vars['supplier_tin'], '888', 'совпадают')


@pytest.fixture
def mock_response_500(monkeypatch):
    # pylint: disable=unused-argument
    def mock_get(*args, **kwargs):
        return MockResponse(
            status=500,
            data={}
        )

    monkeypatch.setattr(aiohttp.ClientSession, 'get', mock_get)


# pylint: disable=redefined-outer-name,unused-argument
async def test_update_vat_fail(tap, mock_response_500):
    with tap.raises(vat.VatUpdateException):
        await vat.update_products_vat(
            'http://example.com/vat', 'login', 'password')


async def test_save_vat(tap, dataset):
    products = [await dataset.product(products_scope=['russia'])
                for _ in range(10)]
    vats = {p.external_id: 10 + i for i, p in enumerate(products)}
    supplier_tins = {p.external_id: str(10 + i)
                     for i, p in enumerate(products)}

    with tap:
        await vat.save_vat(vats,
                           supplier_tins,
                           product_scope=cfg('sync.1c.product_scope'),
                           updated_by='1C',
                           chunk_size=4)

        for product in products:
            await product.reload()
            tap.eq_ok(product.vat, vats[product.external_id],
                      f'vat={vats[product.external_id]}')
            tap.eq_ok(product.vars['supplier_tin'],
                      supplier_tins[product.external_id],
                      f'supplier_tin={supplier_tins[product.external_id]}')


class SessionMock:
    def __init__(self, data):
        self._data = data

    # pylint: disable=unused-argument
    def get(self, url, *args, **kwargs):
        page = int(yarl.URL(url).query.get('page', '1'))

        has_more_page = False
        if page < len(self._data):
            has_more_page = True

        items = []
        if page <= len(self._data):
            items = self._data[page - 1]

        return MockResponse(
            status=200,
            data={
                'code': 0,
                'items': items,
                'page_context': {
                    'page': page,
                    'has_more_page': has_more_page,
                },
            },
        )


# pylint: disable=redefined-outer-name,unused-argument
async def test_save_vat_skip(tap, dataset, mock_response_500):
    products = [await dataset.product(products_scope=['russia'])
                for _ in range(10)]
    vats = {p.external_id: 10 + i for i, p in enumerate(products)}
    supplier_tins = {p.external_id: str(10 + i) for i, p in enumerate(products)}

    await vat.save_vat(
        vats,
        supplier_tins,
        product_scope='israel',
        updated_by='WOODY',
        chunk_size=4
    )

    for product in products:
        await product.reload()
        tap.eq_ok(product.vat, None,
                  f'vat no change for {product.product_id}')
        tap.eq_ok(product.vars.get('supplier_tin', None), None,
                  f'supplier_tin no change for {product.product_id}')


async def test_save_woody(tap, dataset):
    products = [await dataset.product(products_scope=['france'])
                for _ in range(10)]
    vats = {p.external_id: 10 + i for i, p in enumerate(products)}
    supplier_tins = {}

    with tap:
        await vat.save_vat(vats,
                           supplier_tins,
                           product_scope=cfg('sync.woody.fr.product_scope'),
                           updated_by='WOODY',
                           chunk_size=4)

        for product in products:
            await product.reload()
            tap.eq_ok(product.vat, vats[product.external_id],
                      f'vat={vats[product.external_id]}')


async def test_woody(tap, cfg, ext_api):
    requests = []

    async def handler(request):
        requests.append(request)

        if len(requests) == 1:
            return web.json_response(
                [
                    {
                        'default_code': 'code1',
                        'tax_amount': 1,
                        'taxes_id': 1,
                    },
                    {
                        'default_code': 'code2',
                        'tax_amount': 2,
                        'taxes_id': 2,
                    },
                    {
                        'default_code': 'code3',
                        'tax_amount': 3,
                        'taxes_id': 3,
                    },
                ]
            )
        if len(requests) == 2:
            return web.json_response(
                [
                    {
                        'default_code': 'code4',
                        'tax_amount': 4,
                        'taxes_id': 4,
                    },
                    {
                        'default_code': 'code5',
                        'tax_amount': 5,
                        'taxes_id': False,
                    },
                ]
            )
        if len(requests) == 3:
            return web.json_response(
                []
            )

    # только для тестов
    client = WoodyClient(region='fr')
    client.headers = {}

    async with await ext_api(client, handler) as client:

        items = {}
        async for vats in client.get_vat():
            items.update(vats)

        with tap.plan(1):
            # не до 5 включая так как в последнем false
            tap.eq_ok(items,
                      {f'code{i}': i for i in range(1, 5)},
                      'Correct VAT values')
