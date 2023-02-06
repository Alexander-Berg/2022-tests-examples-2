# pylint: disable=unused-import,too-many-lines
import asyncio
import datetime
import inspect
import random
import sys
from typing import Union
import typing

import pytest  # pylint: disable=wrong-import-order
from yarl import URL

from libstall import json_pp
import libstall
from libstall.pg.dbh import dbh     # pylint: disable=unused-import
from libstall.timetable import TimeTable, TimeTableItem
from libstall.util import uuid, barcode, tzone, time2time, now
from stall import keyword
from stall import cfg, lp
from stall.api.admin.qr_actions.generate import get_qr_action_data
from stall.client.clickhouse import ClickHouseClient
from stall.model.analytics.courier_metric import CourierMetric
from stall.model.analytics.courier_scoring import CourierScoring
from stall.model.analytics.md_audit import MDAudit
from stall.model.analytics.store_metric import StoreMetric
from stall.model.analytics.writeoff_limit import WriteoffLimit
from stall.model.analytics.tablo_metrics import TabloMetric
from stall.model.asset import Asset
from stall.model.assortment import Assortment
from stall.model.assortment_contractor import AssortmentContractor
from stall.model.assortment_contractor_product import (
    AssortmentContractorProduct
)
from stall.model.assortment_product import AssortmentProduct
from stall.model.briefing_tickets import BriefingTickets
from stall.model.check_project import CheckProject
from stall.model.cluster import Cluster
from stall.model.company import Company
from stall.model.courier import Courier
from stall.model.courier_shift import CourierShift, CourierShiftEvent
from stall.model.courier_shift_schedule import (
    CourierShiftSchedule,
    CourierShiftScheduleItem,
)
from stall.model.courier_shift_tag import CourierShiftTag
from stall.model.delivery import Delivery
from stall.model.delivery_log import DeliveryLog
from stall.model.device import Device
from stall.model.draft.price_list import DraftPriceList
from stall.model.draft.price_list_product import DraftPriceListProduct
from stall.model.event import Event
from stall.model.event_cache import EventCache
from stall.model.file_meta import FileMeta
from stall.model.gate import Gate
from stall.model.gate_slot import GateSlot
from stall.model.inventory_snapshot import InventoryRecord
from stall.model.item import Item
from stall.model.order import Order
from stall.model.order_courier import OrderCourier
from stall.model.order_event import OrderEvent
from stall.model.order_log import OrderLog
from stall.model.price_list import PriceList
from stall.model.price_list_product import PriceListProduct
from stall.model.printer_task import PrinterTask
from stall.model.printer_task_payload import PrinterTaskPayload
from stall.model.product import Product
from stall.model.product_group import ProductGroup
from stall.model.product_sample import ProductSample
from stall.model.provider import Provider
from stall.model.repair_task import RepairTask
from stall.model.role import Role
from stall.model.schedule import Schedule
from stall.model.schet_handler import SCHETS
from stall.model.schet_task import SchetTask
from stall.model.shelf import SHELF_TYPES
from stall.model.shelf import Shelf
from stall.model.stash import Stash
from stall.model.stock import Stock
from stall.model.stock_log import StockLog
from stall.model.store import Store
from stall.model.store_stock import StoreStock
from stall.model.analytics.store_health import StoreHealth
from stall.model.analytics.store_problem import StoreProblem
from stall.model.suggest import Suggest
from stall.model.user import User
from stall.model.zone import Zone
from stall.model.true_mark import TrueMark
from stall.model.rack import Rack
from stall.model.rack_log import RackLog
from stall.model.rack_zone import RackZone
from stall.model.default_store_config import DefaultStoreConfig
from tests.model.clickhouse.grocery.grocery_order_created import (
    GroceryOrderCreated
)
from tests.model.clickhouse.grocery.grocery_order_assemble_ready import (
    GroceryOrderAssembleReady
)
from tests.model.clickhouse.grocery.wms_order_processing import (
    WmsOrderProcessing
)
from tests.model.clickhouse.grocery.wms_order_complete import (
    WmsOrderComplete
)
from tests.model.clickhouse.grocery.grocery_order_matched import (
    GroceryOrderMatched
)
from tests.model.clickhouse.grocery.grocery_performer_pickup_order import (
    GroceryOrderPickup
)
from tests.model.clickhouse.grocery.grocery_performer_delivering_arrived \
    import (
        GroceryDeliveringArrived
    )
from tests.model.clickhouse.grocery.grocery_order_delivered import (
    GroceryOrderDelivered
)
from tests.model.clickhouse.grocery.grocery_order_closed import (
    GroceryOrderClosed
)
from tests.model.clickhouse.grocery.grocery_performer_return_depot import (
    GroceryReturnDepot
)
from tests.model.clickhouse.grocery.grocery_shift_update import (
    GroceryShiftUpdate
)
from tests.model.clickhouse.grocery.wms_order_status_updated import (
    WmsOrderStatusUpdated
)


async def random_zone():
    if hasattr(random_zone, 'db'):
        db = getattr(random_zone, 'db')
    else:
        with open('scripts/dev/data/geodata.json') as fh:
            db = json_pp.loads(fh.read())
        setattr(random_zone, 'db', db)
    return random.choice(db['stores'])['zone']


async def zone(**kwargs) -> Zone:

    _company = kwargs.pop('company', None)
    _store   = kwargs.pop('store', None)

    kwargs.setdefault('store_id',   _store.store_id)
    kwargs.setdefault(
        'company_id',
        _company.company_id if _company else _store.company_id
    )

    kwargs.setdefault('delivery_type', 'foot')
    kwargs.setdefault('status', 'active')
    kwargs.setdefault('timetable',  TimeTable([
        TimeTableItem({
            'type': 'everyday',
            'begin': '00:00',
            'end': '00:00',
        })
    ]))
    kwargs.setdefault('zone', {
        "type": "Polygon",
        "coordinates": [
            [
                [37.30, 55.60],
                [37.90, 55.60],
                [37.90, 55.80],
                [37.30, 55.80],
                [37.30, 55.60],
            ],
        ]
    })

    return await Zone(kwargs).save()


async def check_project(**kwargs) -> CheckProject:
    kwargs.setdefault(
        'title', f'Тестовый проект расписания локалок - {uuid()}',
    )

    store_id = kwargs.pop('store_id', None)
    if kwargs.get('store'):
        store_id = kwargs['store'].store_id
    company_id = kwargs.pop('company_id', None)
    if kwargs.get('company'):
        company_id = kwargs['company'].company_id
    cluster_id = kwargs.pop('cluster_id', None)
    if kwargs.get('cluster'):
        cluster_id = kwargs['cluster'].cluster_id
    stores = {
        'store_id': store_id,
        'company_id': company_id,
        'cluster_id': cluster_id,
    }
    for k in list(stores):
        v = stores[k]
        if v:
            stores[k] = [v]
        else:
            stores.pop(k)
    kwargs.setdefault('stores', stores)

    product_id = kwargs.pop('product_id', None)
    if kwargs.get('product'):
        product_id = kwargs['product'].product_id
    product_group_id = kwargs.pop('product_group_id', None)
    if kwargs.get('product_group'):
        product_group_id = kwargs['product_group'].group_id
    products = {
        'product_id': product_id,
        'product_group_id': product_group_id,
    }
    for k in list(products):
        v = products[k]
        if v:
            products[k] = [v]
        else:
            products.pop(k)
    kwargs.setdefault('products', products)

    tomorrow = (
        now().replace(hour=0, minute=0, second=0, microsecond=0) +
        datetime.timedelta(days=1)
    )
    timetable = TimeTable([
        {
            'type': 'everyday',
            'begin': datetime.time(4, 20),
            'end': datetime.time(4, 20),
        }
    ])
    schedule = {
        'timetable': timetable.pure_python(),
        'begin': tomorrow,
        'end': (
            tomorrow +
            datetime.timedelta(days=1) -
            datetime.timedelta(seconds=1)
        ),
    }
    kwargs.setdefault('schedule', schedule)

    return await CheckProject(kwargs).save()


async def schet_task(**kwargs) -> SchetTask:
    _company = kwargs.pop('company', None)
    _store = kwargs.pop('store', None)

    _user = kwargs.pop('user', None)
    if _user is None:
        _user = await User.load(kwargs.pop('user_id'))

    kwargs.setdefault(
        'store_id',
        _store.store_id if _store else
        None
    )
    kwargs.setdefault(
        'company_id',
        _company.company_id if _company else
        _store.company_id if _store else
        None
    )

    kwargs.setdefault(
        'created_by', _user.user_id
    )
    kwargs.setdefault(
        'schedule_draft', Schedule({'interval': {'minutes': 1}})
    )
    kwargs.setdefault(
        'handler', next(iter(SCHETS['handlers']))
    )

    return await SchetTask(kwargs).save()


async def store(**kwargs) -> Store:
    if 'assortment' in kwargs:
        kwargs['assortment_id'] = kwargs['assortment'].assortment_id
    if 'kitchen_assortment' in kwargs:
        kwargs['kitchen_assortment_id'] = (
            kwargs['kitchen_assortment'].assortment_id
        )
    if 'markdown_assortment' in kwargs:
        kwargs['markdown_assortment_id'] = (
            kwargs['markdown_assortment'].assortment_id
        )
    if 'price_list' in kwargs:
        kwargs['price_list_id'] = kwargs['price_list'].price_list_id
    if 'company' in kwargs:
        kwargs['company_id'] = kwargs['company'].company_id
    if not kwargs.get('company_id', None):
        kwargs['company_id'] = (await company()).company_id

    _cluster = kwargs.pop('cluster', None)
    if not _cluster:
        _cluster = await cluster()
    elif isinstance(_cluster, str):
        _cluster = await cluster(title=_cluster)

    kwargs.setdefault('cluster', _cluster.title)
    kwargs.setdefault('cluster_id', _cluster.cluster_id)

    kwargs.setdefault('title',      f'Тестовый склад - {keyword.keyword()}')
    kwargs.setdefault('lang',       'ru_RU')
    kwargs.setdefault('currency',   'RUB')
    kwargs.setdefault('timetable',  TimeTable([
        TimeTableItem({
            'type': 'everyday',
            'begin': '00:00',
            'end': '00:00',
        })
    ]))
    kwargs.setdefault('location', (55.70, 37.50))

    store_ = await Store(kwargs).save()
    await zone(store=store_)

    return store_


async def full_store(**kwargs) -> Store:
    '''создаёт склад с набором полок'''
    store_ = await store(**kwargs)

    await asyncio.gather(
        *[shelf(store_id=store_.store_id, type=t) for t in SHELF_TYPES]
    )

    return store_


async def cluster(**kwargs):
    kwargs.setdefault('title', f'Кластер {keyword.keyword()}')
    return await Cluster(kwargs).save()


async def company(**kwargs):
    kwargs.setdefault('title', f'Организация {uuid()}')
    kwargs.setdefault('products_scope', ['russia'])
    return await Company(kwargs).save()


async def product_group(**kwargs):
    kwargs.setdefault('name', f'Тестовая группа товаров - {keyword.keyword()}')
    kwargs.setdefault(
        'timetable',
        TimeTable(
            [
                TimeTableItem(
                    {
                        'type': t,
                        'begin': '00:00',
                        'end': '00:00',
                    }
                ) for t in ('monday', 'wednesday', 'friday', 'sunday')
            ]
        )
    )
    return await ProductGroup(kwargs).save()


async def product_group_lunch(**kwargs):
    # для фронтовых тестов с обедами для курьеров
    lunch = cfg('business.product_group.courier_lunch.testing')
    product_gpoup = await ProductGroup.load(lunch)
    if product_gpoup:
        return product_gpoup
    kwargs.setdefault('group_id', lunch)
    return await product_group(**kwargs)


async def product_links(**kwargs):
    '''
        Используется в тестах фронта. То же что продукт, но со ссылками.

        Возвращает словарь
    '''
    if 'product_id' in kwargs:
        product_ = await Product.load(kwargs['product_id'])
    else:
        product_ = await product(**kwargs)

    res = product_.pure_python()
    res['page'] = str(URL('/').with_path(f'/products/{product_.product_id}'))
    return res


async def product(**kwargs) -> Product:
    kwargs.setdefault('title', f'Тестовый продукт - {keyword.keyword()}')
    kwargs.setdefault(
        'images',
        [
            f'https://via.placeholder.com/{{w}}x{{h}}.png?text={x}'
            for x in range(3)
        ],
    )
    kwargs.setdefault('products_scope', ['russia'])

    if 'true_mark' in kwargs:  # всякая жесть в связи с требованиями к ЧЗ
        kwargs.setdefault(
            'vars', {}
        ).setdefault(
            'imported', {}
        )['true_mark'] = kwargs['true_mark']

        # в случае если передан true_mark (даже False), хочется чтобы
        # сгенерировались нормальные баркоды:
        # 14 символов с нулем в начале и такой же 13 без нуля
        if kwargs.get('barcode'):
            if not any(
                len(b) == 13 and not b.startswith('0')
                for b in kwargs['barcode']
            ):
                bcode = kwargs['barcode'][0].ljust(13, '7')
                if len(bcode) > 13:
                    bcode = bcode[:13]
                if bcode.startswith('0'):
                    bcode = bcode.replace('0', '7', 1)
                kwargs['barcode'].append(bcode)
                kwargs['barcode'].append('0' + bcode)
        else:
            kwargs.pop('barcode', None)

    barcode_with_zero = '0' + str(random.randint(10**12, 10**13 - 1))
    kwargs.setdefault('barcode', [barcode_with_zero, barcode_with_zero[1:]])

    return await Product(kwargs).save()


async def true_mark_value(**kwargs):
    p = kwargs.get('product')
    if 'product_id' in kwargs:
        p = await Product.load(kwargs['product_id'])
    if p:  # генерим по заветам обычной молочной продукции
        for b in p.barcode:
            if len(b) == 14 and b[0] == '0' and b[1:] in p.barcode:
                bcode = '01' + b
                serial = '21' + uuid()[:6]
                separator = chr(29)
                check = '93' + uuid()[:4]
                return bcode+serial+separator+check
    return

true_mark = true_mark_value  # это чтобы полка работала на время переименования


async def shelf(**kwargs):
    shelf_store = kwargs.get('store')

    if not shelf_store:
        store_id = kwargs.get('store_id')
        if store_id:
            del kwargs['store_id']
            shelf_store = await Store.load(store_id)
        else:
            save_type = kwargs.get('type')
            if save_type:
                del kwargs['type']
            shelf_store = await store(**kwargs)
            if save_type:
                kwargs['type'] = save_type

    if not shelf_store:
        raise RuntimeError('Не удалось загрузить склад для создания полки')

    kwargs.setdefault('title', f'Тестовая полка - {keyword.keyword()}')
    kwargs.setdefault('store_id', shelf_store.store_id)
    cur_shelf = await Shelf(kwargs).save()

    if kwargs.get('rack_id'):
        cur_rack = await Rack.load(kwargs['rack_id'])
        cur_shelf.rack_id = None
        result = await cur_rack.do_link_cargo_no_order(cargo=cur_shelf)
        assert result, 'Не смогли привязать груз к стеллажу'
        cur_shelf.rack_id = result.rack_id

    return cur_shelf


async def item(**kwargs):
    store_ = kwargs.get('store')
    if not store_:
        store_id = kwargs.get('store_id')
        if store_id:
            del kwargs['store_id']
            store_ = await Store.load(store_id)
        else:
            type_ = kwargs.get('type')
            if type_:
                del kwargs['type']
            store_ = await store(**kwargs)
            if type_:
                kwargs['type'] = type_
    kwargs.setdefault('store_id', store_.store_id)
    kwargs.setdefault('title', f'Тестовый экземпляр - {keyword.keyword()}')
    kwargs.setdefault('external_id', uuid())
    kwargs.setdefault('type', 'parcel')
    kwargs.setdefault('description', keyword.keyword())
    kwargs.setdefault('barcode', [uuid()])

    return await Item(kwargs).save()


async def user_token(**kwargs):
    '''
        Используется в тестах фронта. То же что юзер, но с токеном.

        Возвращает словарь
    '''
    if 'user_id' in kwargs:
        user_ = await User.load(kwargs['user_id'])
    else:
        user_ = await user(**kwargs)

    res = user_.pure_python()
    res['token'] = user_.token()
    res['url'] = str(URL('/').with_query(token=res['token']))
    res['page'] = str(URL('/').with_path(f'/users/{user_.user_id}'))
    res['qrcode'] = str(user_.qrcode)
    return res


async def user(**kwargs):
    kwargs.setdefault('role', 'admin')
    kwargs.setdefault('fullname', keyword.keyword())
    kwargs.setdefault('nick', keyword.noun())

    if 'company' not in kwargs and 'company_id' not in kwargs:
        kwargs['company'] = await company(**kwargs)

    if 'store' not in kwargs and 'store_id' not in kwargs:
        kwargs['store'] = await store(**kwargs)
    if not kwargs.get('store') and kwargs.get('store_id'):
        store_loaded = await Store.load(kwargs['store_id'])
        if store_loaded:
            kwargs['store'] = store_loaded

    if 'store' in kwargs:
        kwargs.setdefault('company_id', kwargs['store'].company_id)
        kwargs.setdefault('store_id',   kwargs['store'].store_id)

    # UGLY: здесь имена пересекаются, пока так
    if 'provider' in kwargs and isinstance(kwargs['provider'], Provider):
        kwargs.setdefault('provider_id', kwargs['provider'].provider_id)
        del kwargs['provider']

    kwargs.setdefault('device', [uuid()])
    kwargs.setdefault('provider', 'test')
    kwargs.setdefault('provider_user_id', uuid())

    if kwargs['role'] == 'barcode_executer':
        kwargs['role'] = 'executer'
        force_role = 'barcode_executer'
    else:
        force_role = None

    if 'lang' not in kwargs:
        kwargs['lang'] = 'ru_RU'

    result_user = User(kwargs)

    ruser: User = await result_user.save()
    if force_role:
        ruser.force_role = force_role

    if kwargs.get('force_role'):
        ruser.force_role = Role(kwargs.get('force_role'))

    return ruser


# pylint: disable=redefined-outer-name
async def order_links(**kwargs):
    """
        Используется в тестах фронта. То же что order, но со ссылками.
        Возвращает словарь
    """

    _order_id = kwargs.get('order_id')
    if _order_id:
        _order = await Order.load(_order_id)
    else:
        _order = await order(**kwargs)

    res = _order.pure_python()
    res['page'] = str(URL('/').with_path(
        f'/stores/{_order.store_id}/orders/{_order.order_id}'
    ))
    return res


async def order(
        store_job_event: bool = False,
        courier: Union[dict, bool] = None,
        **kwargs
):
    shelf_store = kwargs.get('store')
    _shift = kwargs.pop('courier_shift', None)

    private = {}
    for k in ('status', 'type'):
        if k in kwargs:
            private[k] = kwargs[k]
            del kwargs[k]

    if not shelf_store:
        store_id = kwargs.get('store_id')
        if store_id:
            del kwargs['store_id']
            shelf_store = await Store.load(store_id)
        else:
            estatus = None
            if 'estatus' in kwargs:
                estatus = kwargs['estatus']
                del kwargs['estatus']
            shelf_store = await store(**kwargs)
            if estatus:
                kwargs['estatus'] = estatus

    if not shelf_store:
        raise RuntimeError('Не удалось загрузить склад для создания заказа')

    kwargs = {**private, **kwargs}
    kwargs.setdefault('status', 'reserving')
    kwargs.setdefault('type', 'order')
    kwargs.setdefault('company_id', shelf_store.company_id)
    kwargs.setdefault('store_id', shelf_store.store_id)

    if courier:
        if isinstance(courier, bool):
            courier = {}
        if isinstance(courier, dict):
            courier.setdefault('external_id', uuid())
        kwargs['courier'] = courier

    if _shift:
        kwargs.setdefault('courier_id', _shift.courier_id)
        kwargs.setdefault('courier_shift_id', _shift.courier_shift_id)

    return await Order(kwargs).save(store_job_event=store_job_event)


async def device(**kwargs):
    if 'company' not in kwargs and 'company_id' not in kwargs:
        kwargs['company'] = await company(**kwargs)

    if 'store' not in kwargs and 'store_id' not in kwargs:
        kwargs['store'] = await store(**kwargs)
    if not kwargs.get('store') and kwargs.get('store_id'):
        store_loaded = await Store.load(kwargs['store_id'])
        if store_loaded:
            kwargs['store'] = store_loaded

    if 'store' in kwargs:
        kwargs.setdefault('company_id', kwargs['store'].company_id)
        kwargs.setdefault('store_id',   kwargs['store'].store_id)

    if 'title' not in kwargs:
        kwargs['title'] = keyword.noun()

    if isinstance(kwargs['store'], str):
        _store = await Store.load(kwargs['store'])
        kwargs.setdefault('store_id', _store.store_id)
    else:
        kwargs.setdefault('store_id', kwargs['store'].store_id)

    return await Device(kwargs).save()


async def wait_order_status(
        order,
        fstatus,
        *,
        user_done=None,
        tap=None,
):  # pylint: disable=redefined-outer-name

    await order.reload()
    if order.fstatus == fstatus:
        await order.business.order_changed(store_job_event=False)

    while order.fstatus != fstatus:
        # Если указан пользователь закрытия, то завершим заказ закрыв все
        # саджесты как выполненные
        if user_done and order.fstatus == ('processing', 'waiting'):
            order.user_done = user_done.user_id
            suggests = await Suggest.list_by_order(order, status='request')
            for s in suggests:
                mark_value = None
                if s.conditions.need_true_mark:
                    # для марочных саджестов нагенерим марку
                    mark_value = await true_mark_value(product_id=s.product_id)
                await s.done(
                    'done',
                    store_job_event=False,
                    user=user_done,
                    true_mark=mark_value,
                )

        if not await order.business.order_changed(store_job_event=False):
            break
        await order.reload()

        if order.revision > 100:
            break
    else:
        if tap:
            tap.passed(f'Ожидаем статус {fstatus}')
        return True
    if tap:
        tap.failed(f'Ожидаем статус {fstatus}')
        tap.diag(f'текущий статус: {order.fstatus}')
    return False


async def order_done(**kwargs):
    kwargs_copy = kwargs.copy()
    order_for_done = await order(store_job_event=False, **kwargs)
    if order_for_done.acks:
        user_done = await User.load(order_for_done.acks[0])
    else:
        user_done = await user(store_id=order_for_done.store_id)
        # ждем возможность взятия юзером
        await wait_order_status(order_for_done, ('request', 'waiting'))
        await order_for_done.ack(user_done, store_job_event=False)

    status = await wait_order_status(order_for_done, ('complete', 'done'),
                                     user_done=user_done)
    if status:
        return order_for_done

    raise RuntimeError(f'Что-то не так с order, '
                       f'статус: {order_for_done.fstatus}'
                       f'kwargs = {kwargs_copy}')


async def suggest(order, **kwargs):  # pylint: disable=redefined-outer-name

    kwargs.setdefault('status', 'request')
    kwargs.setdefault('type', 'box2shelf')
    if isinstance(order, str):
        _order = await Order.load(order)
        kwargs.setdefault('order_id', _order.order_id)
        kwargs.setdefault('store_id', _order.store_id)
    else:
        kwargs.setdefault('order_id', order.order_id)
        kwargs.setdefault('store_id', order.store_id)
    kwargs.setdefault(
        'valid',
        (datetime.datetime.now() + datetime.timedelta(days=29)).strftime('%F')
    )

    if 'stock_id' not in kwargs:
        suggest_stock = kwargs.get('stock')
        if suggest_stock:
            kwargs.setdefault('stock_id', suggest_stock.stock_id)
            kwargs.setdefault('shelf_id', suggest_stock.shelf_id)
            kwargs.setdefault('product_id', suggest_stock.product_id)

    if 'shelf_id' not in kwargs:
        suggest_shelf = kwargs.get('shelf')
        if not suggest_shelf:
            shelf_type = kwargs['type']
            del kwargs['type']
            shelf_status = kwargs.pop('status')
            suggest_shelf = await shelf(**kwargs)
            kwargs.setdefault('type', shelf_type)
            kwargs.setdefault('status', shelf_status)
        kwargs.setdefault('shelf_id', suggest_shelf.shelf_id)

    if kwargs['type'] in ('box2shelf', 'shelf2box', 'check'):
        if 'product_id' not in kwargs:
            suggest_product = kwargs.get('product')
            if suggest_product:
                kwargs.setdefault('product_id', suggest_product.product_id)

    if 'suggest_order' in kwargs:
        kwargs['order'] = kwargs['suggest_order']
        del kwargs['suggest_order']

    if kwargs['type'] in ('shelf2box', 'box2shelf', 'check'):
        kwargs.setdefault('count', 27)

    return await Suggest(kwargs).save()


async def printer_task_payload(**kwargs):
    kwargs.setdefault('data', uuid())

    return await PrinterTaskPayload(kwargs).save()


async def printer_task(**kwargs):
    if 'payload_id' not in kwargs:
        if 'store_id' not in kwargs:
            if 'store' not in kwargs:
                store_ = await store(**kwargs)
                kwargs['store'] = store_
            kwargs['store_id'] = kwargs['store'].store_id

        if 'payload' not in kwargs:
            kwargs['payload'] = 'Hello, world'

        if isinstance(kwargs['payload'], (str, int, float)):
            payload = await printer_task_payload(data=str(kwargs['payload']))
        else:
            payload = kwargs['payload']
        kwargs['payload_id'] = payload.payload_id

    task = await PrinterTask(kwargs).save()
    await lp.push_list([{
        'key': ['print', 'store', task.store_id],
        'data': {
            'task': task.task_id
        }
    }])

    return task


async def assortment(**kwargs):

    kwargs.setdefault('title', f'Тестовый ассортимент - {keyword.keyword()}')

    if 'company' in kwargs:
        kwargs.setdefault('company_id', kwargs['company'].company_id)
    elif 'company_id' not in kwargs:
        kwargs['company'] = await company(**kwargs)
        kwargs['company_id'] = kwargs['company'].company_id

    return await Assortment(kwargs).save()


async def assortment_contractor(**kwargs):
    if 'store' in kwargs:
        kwargs.setdefault('store_id', kwargs['store'].store_id)
    elif 'store_id' not in kwargs:
        kwargs['store'] = await store(**kwargs)
        kwargs['store_id'] = kwargs['store'].store_id

    kwargs.setdefault('contractor_id', uuid())
    kwargs.setdefault('instance_erp', None)
    kwargs.setdefault('cursor', uuid())

    return await AssortmentContractor(kwargs).save()


async def kitchen_assortment(**kwargs):

    kwargs.setdefault(
        'title', f'Тестовый ассортимент кухни - {keyword.keyword()}'
    )

    return await Assortment(kwargs).save()


async def assortment_product(**kwargs):

    if 'product_id' not in kwargs:
        if 'product' in kwargs:
            kwargs.setdefault('product_id', kwargs['product'].product_id)
        else:
            p = await product(**kwargs)
            kwargs.setdefault('product_id', p.product_id)

    if 'assortment_id' not in kwargs:
        if 'assortment' in kwargs:
            kwargs.setdefault('assortment_id',
                              kwargs['assortment'].assortment_id)
        else:
            a = await assortment(**kwargs)
            kwargs.setdefault('assortment_id', a.assortment_id)
    kwargs.setdefault('max', 50)

    return await AssortmentProduct(kwargs).save()


async def assortment_contractor_product(**kwargs):
    if 'product' in kwargs:
        kwargs.setdefault('product_id', kwargs['product'].product_id)
    elif 'product_id' not in kwargs:
        p = await product(**kwargs)
        kwargs['product_id'] = p.product_id

    if 'assortment' in kwargs:
        kwargs.setdefault('assortment_id', kwargs['assortment'].assortment_id)
    elif 'assortment_id' not in kwargs:
        a = await assortment_contractor(**kwargs)
        kwargs['assortment_id'] = a.assortment_id

    return await AssortmentContractorProduct(kwargs).save()


async def price_list(**kwargs) -> PriceList:
    kwargs.setdefault('title', f'Тестовый прайс-лист - {keyword.keyword()}')

    if 'user_id' not in kwargs:
        if 'user' in kwargs:
            kwargs.setdefault('user_id', kwargs['user'].user_id)

    if 'company' in kwargs:
        kwargs.setdefault('company_id', kwargs['company'].company_id)
    elif 'company_id' not in kwargs:
        kwargs['company'] = await company(**kwargs)
        kwargs['company_id'] = kwargs['company'].company_id

    return await PriceList(kwargs).save()


async def price_list_product(**kwargs) -> PriceListProduct:
    if 'product_id' not in kwargs:
        if 'product' in kwargs:
            kwargs.setdefault('product_id', kwargs['product'].product_id)
        else:
            p = await product(**kwargs)
            kwargs.setdefault('product_id', p.product_id)

    if 'price_list_id' not in kwargs:
        if 'price_list' in kwargs:
            kwargs.setdefault(
                'price_list_id',
                kwargs['price_list'].price_list_id,
            )
        else:
            pl = await price_list(**kwargs)
            kwargs.setdefault('price_list_id', pl.price_list_id)

    if 'user_id' not in kwargs:
        if 'user' in kwargs:
            kwargs.setdefault('user_id', kwargs['user'].user_id)

    return await PriceListProduct(kwargs).save()


async def draft_price_list(**kwargs) -> PriceList:
    kwargs.setdefault('title', f'Черновик прайс-лист - {keyword.keyword()}')

    if 'user_id' not in kwargs:
        if 'user' in kwargs:
            kwargs.setdefault('user_id', kwargs['user'].user_id)

    if 'company' in kwargs:
        kwargs.setdefault('company_id', kwargs['company'].company_id)
    elif 'company_id' not in kwargs:
        kwargs['company'] = await company(**kwargs)
        kwargs['company_id'] = kwargs['company'].company_id

    return await DraftPriceList(kwargs).save()


async def draft_price_list_product(**kwargs) -> PriceListProduct:
    if 'product_id' not in kwargs:
        if 'product' in kwargs:
            kwargs.setdefault('product_id', kwargs['product'].product_id)
        else:
            p = await product(**kwargs)
            kwargs.setdefault('product_id', p.product_id)

    if 'price_list_id' not in kwargs:
        if 'price_list' in kwargs:
            kwargs.setdefault(
                'price_list_id',
                kwargs['price_list'].price_list_id,
            )
        else:
            pl = await price_list(**kwargs)
            kwargs.setdefault('price_list_id', pl.price_list_id)

    if 'user_id' not in kwargs:
        if 'user' in kwargs:
            kwargs.setdefault('user_id', kwargs['user'].user_id)

    return await DraftPriceListProduct(kwargs).save()


async def sample(**kwargs):
    if 'product_id' not in kwargs:
        if 'product' in kwargs:
            kwargs.setdefault('product_id', kwargs['product'].product_id)
        else:
            p = await product()
            kwargs.setdefault('product_id', p.product_id)
    kwargs.setdefault('mode', 'optional')
    kwargs.setdefault('count', 1)
    kwargs.setdefault('tags', ['sampling'])
    kwargs.setdefault('title', keyword.keyword())
    if 'company' in kwargs:
        kwargs.setdefault('company_id', kwargs['company'].company_id)
    if 'company_id' not in kwargs:
        kwargs['company_id'] = (await company()).company_id

    return await ProductSample(kwargs).save()


async def asset(**kwargs):
    kwargs.setdefault('title', f'Тестовое основное средство'
                               f' - {keyword.keyword()}')
    return await Asset(kwargs).save()


async def stock(**kw):
    # pylint: disable=consider-using-get,too-many-branches,too-many-statements

    valid = None
    if 'valid' in kw:
        valid = kw['valid']
        del kw['valid']

    if 'product' in kw:
        stock_product = kw['product']
        del kw['product']
        kw.setdefault('shelf_type', 'store')
    elif 'item' in kw:
        stock_product = kw['item']
        kw.setdefault('shelf_type', 'parcel')
        del kw['item']
    else:
        if 'product_id' in kw:
            stock_product = await Product.load(kw['product_id'])
            kw.setdefault('shelf_type', 'store')
            if not stock_product:
                stock_product = await Item.load(kw['product_id'])
                kw.setdefault('shelf_type', 'store')
        else:
            saved_order = kw.pop('order', None)
            stock_product = await product(**kw)
            if saved_order is not None:
                kw['order'] = saved_order
            kw.setdefault('shelf_type', 'store')

    if 'shelf' in kw:
        stock_shelf = kw['shelf']
        del kw['shelf']
    else:
        if 'order' in kw:
            otmp = kw['order']
            del kw['order']
            kw.setdefault('store_id', otmp.store_id)
            kw.setdefault('company_id', otmp.company_id)
        else:
            otmp = None
        if 'shelf_id' in kw:
            stock_shelf = await Shelf.load(kw['shelf_id'])
        else:
            save_type = kw.get('type')
            kw['type'] = kw.get('shelf_type', 'store')

            stock_shelf = await shelf(**kw)
            if save_type is None:
                del kw['type']
            else:
                kw['type'] = save_type

        if otmp is not None:
            kw['order'] = otmp

    if 'order' in kw:
        stock_order = kw['order']
        del kw['order']
    else:
        kw.setdefault('store_id', stock_shelf.store_id)

        stock_store = await Store.load(stock_shelf.store_id)
        kw.setdefault('company_id', stock_store.company_id)

        stock_order = await order(**kw)

    if 'count' in kw:
        count = kw['count']
        del kw['count']
    else:
        if isinstance(stock_product, Item):
            count = 1
        else:
            count = 103

    if stock_shelf.type == 'office':
        if stock_product.vars.get('imported', None):
            if not stock_product.vars['imported'].get(
                'nomenclature_type', None
            ):
                stock_product.vars['imported']['nomenclature_type'] =\
                    'consumable'
        else:
            stock_product.vars['imported'] =\
                {'nomenclature_type': 'consumable'}

    sub = getattr(Stock, 'do_write_in') if (
        stock_shelf.type == 'incoming') else getattr(Stock, 'do_put')

    stock_ = await sub(
        stock_order,
        stock_shelf,
        stock_product,
        count or 1,
        valid=valid,
        **kw
    )

    await stock_.reload()
    if count == 0:
        await stock_.do_take(stock_order, 1)
        await stock_.reload()

    return stock_


async def stash(**kwargs) -> Stash:
    return await Stash(kwargs).save()


async def provider(**kwargs):
    if 'store' in kwargs:
        kwargs.setdefault('stores', [kwargs['store'].store_id])
        del kwargs['store']

    kwargs.setdefault('title', f'Поставщик {uuid()}')
    kwargs.setdefault('cluster', f'Кластер - {keyword.keyword()}')
    return await Provider(kwargs).save()


async def gate(**kwargs):
    if 'store' in kwargs:
        kwargs.setdefault('store_id', kwargs['store'].store_id)
    if 'store_id' not in kwargs:
        kwargs['store'] = await store(**kwargs)
        kwargs['store_id'] = kwargs['store'].store_id

    kwargs.setdefault('title', f'Ворота-{uuid()}')
    return await Gate(kwargs).save()


async def gate_slot(**kwargs):
    if 'delivery' in kwargs:
        kwargs.setdefault('store_id',       kwargs['delivery'].store_id)
        kwargs.setdefault('provider_id',    kwargs['delivery'].provider_id)
        kwargs.setdefault('delivery_id',    kwargs['delivery'].delivery_id)
    if 'delivery_id' not in kwargs:
        kwargs['delivery'] = await delivery(**kwargs)
        kwargs['delivery_id']   = kwargs['delivery'].delivery_id
        kwargs['store_id']      = kwargs['delivery'].store_id
        kwargs['provider_id']   = kwargs['delivery'].provider_id

    if 'gate' in kwargs:
        kwargs.setdefault('gate_id',  kwargs['gate'].gate_id)
        kwargs.setdefault('store_id', kwargs['gate'].store_id)
    if 'gate_id' not in kwargs:
        kwargs['gate'] = await gate(**kwargs)
        kwargs['gate_id']  = kwargs['gate'].gate_id
        kwargs['store_id'] = kwargs['gate'].store_id

    if 'store' in kwargs:
        kwargs.setdefault('store_id', kwargs['store'].store_id)
    if 'store_id' not in kwargs:
        kwargs['store'] = await store(**kwargs)
        kwargs['store_id'] = kwargs['store'].store_id

    if 'provider' in kwargs:
        kwargs.setdefault('provider_id', kwargs['provider'].provider_id)
    if 'provider_id' not in kwargs:
        kwargs['provider'] = await provider(**kwargs)
        kwargs['provider_id'] = kwargs['provider'].provider_id

    kwargs.setdefault('title', f'Ворота-{uuid()}')
    kwargs.setdefault('type', 'delivery')
    kwargs.setdefault('begin', now())
    kwargs.setdefault('end', now() + datetime.timedelta(hours=1))
    return await GateSlot(kwargs).save()


async def delivery(**kwargs):

    if 'store' in kwargs:
        kwargs.setdefault('store_id', kwargs['store'].store_id)
    if 'store_id' not in kwargs:
        kwargs['store'] = await store(**kwargs)
        kwargs['store_id'] = kwargs['store'].store_id

    if 'provider' in kwargs:
        kwargs.setdefault('provider_id', kwargs['provider'].provider_id)
    if 'provider_id' not in kwargs:
        kwargs['provider'] = await provider(**kwargs)
        kwargs['provider_id'] = kwargs['provider'].provider_id

    return await Delivery(kwargs).save()


async def courier_shift_tag(**kwargs):
    _cluster = kwargs.pop('cluster', None)
    if _cluster:
        kwargs.setdefault('cluster_id', _cluster.cluster_id)

    # если явно передают название, надо убедиться, что в базе нет такого тега
    if 'title' in kwargs:
        tag = await CourierShiftTag.load(kwargs['title'], by='title')
        if tag:
            return tag

    kwargs.setdefault('title', uuid())
    return await CourierShiftTag(kwargs).save()


async def courier_shift_schedule_links(**kwargs):
    """
        Используется в тестах фронта. То же что schedule, но со ссылками.
        Возвращает словарь
    """

    _schedule_id = kwargs.get('courier_shift_schedule_id')
    if _schedule_id:
        _schedule = await CourierShiftSchedule.load(_schedule_id)
    else:
        _schedule = await courier_shift_schedule(**kwargs)

    res = _schedule.pure_python()
    res['page'] = str(URL('/').with_path(
        f'/shifts/imports/{_schedule.courier_shift_schedule_id}'
    ))
    return res


async def courier_shift_schedule(**kwargs):
    _store = kwargs.pop('store', None)
    if _store:
        kwargs.setdefault('store_id', _store.store_id)
        kwargs.setdefault('company_id', _store.company_id)
    return await CourierShiftSchedule(kwargs).save()


async def courier_shift(**kwargs):
    # pylint: disable=too-many-branches
    _user = kwargs.pop('user', None)
    _courier = kwargs.pop('courier', None)
    _schedule = kwargs.pop('courier_shift_schedule', None)
    _status = kwargs.get('status')

    if kwargs.get('cluster'):
        kwargs['cluster_id'] = kwargs['cluster'].cluster_id

    if kwargs.get('store_id'):
        kwargs['store'] = await Store.load(kwargs['store_id'])

    if kwargs.get('store'):
        kwargs.setdefault('store_id', kwargs['store'].store_id)
        kwargs.setdefault('tz', kwargs['store'].tz)
        kwargs.setdefault('company_id', kwargs['store'].company_id)
        kwargs.setdefault('cluster_id', kwargs['store'].cluster_id)

    if not kwargs.get('company'):
        if kwargs.get('company_id'):
            kwargs['company'] = await Company.load(kwargs['company_id'])
        if kwargs.get('company') is None:
            kwargs['company'] = await company(**kwargs)
        kwargs['company_id'] = kwargs['company'].company_id

    if not kwargs.get('cluster_id'):
        kwargs['cluster'] = await cluster(**kwargs)
        kwargs['cluster_id'] = kwargs['cluster'].cluster_id

    if not kwargs.get('store'):
        kwargs['store'] = await store(
            company_id=kwargs['company_id'],
            cluster_id=kwargs['cluster_id'],
        )
        kwargs['store_id'] = kwargs['store'].store_id
        kwargs['tz'] = kwargs['store'].tz

    courier_required = _status in ('waiting', 'processing', 'complete',
                                   'leave', 'absent', 'released')
    if courier_required and not _courier:
        if kwargs.get('courier_id'):
            _courier = await Courier.load(kwargs['courier_id'])
        if _courier is None:
            _courier = await courier(cluster_id=kwargs['cluster_id'],
                                     tags=kwargs.get('tags', []))

    if _courier:
        kwargs['courier_id'] = _courier.courier_id

    if _schedule:
        kwargs.setdefault('import_id', _schedule.courier_shift_schedule_id)

    if _user:
        kwargs['user_id'] = _user.user_id

    kwargs.setdefault('placement', 'planned')
    kwargs.setdefault('delivery_type', 'foot')
    kwargs.setdefault('status', 'request')

    _now = now()
    kwargs.setdefault('started_at', _now + datetime.timedelta(hours=1))
    kwargs.setdefault('closes_at',  _now + datetime.timedelta(hours=5))

    kwargs.setdefault('source', 'manual')

    return await CourierShift(kwargs).save()


async def courier(**kwargs):
    _cluster = kwargs.pop('cluster', None)
    if 'cluster_id' not in kwargs and not _cluster:
        _cluster = await cluster(**kwargs)
    if _cluster:
        kwargs.setdefault('cluster_id', _cluster.cluster_id)

    park_id = uuid()
    driver_id = uuid()

    kwargs.setdefault('first_name', keyword.noun())
    kwargs.setdefault('last_name', keyword.noun())
    kwargs.setdefault('delivery_type', 'foot')
    kwargs.setdefault('external_id', park_id + '_' + driver_id)
    kwargs.setdefault('vars', {'park_id': park_id, 'uuid': driver_id})
    kwargs['vars'].update(kwargs.pop('extra_vars', {}))

    result_courier = Courier(kwargs)
    res = await result_courier.save(not_sync_underage=True)

    return res


async def courier_scoring(**kwargs):
    _courier: Courier = kwargs.pop('courier', None)
    if 'external_courier_id' not in kwargs and not _courier:
        _courier = typing.cast(Courier, await courier(
            vars={'external_ids': {'eats': uuid()}},
            **kwargs
        ))
    if _courier:
        kwargs.setdefault('external_courier_id', _courier.eda_id)
        kwargs.setdefault('shift_delivery_type', _courier.delivery_type)
        kwargs.setdefault('region_name', _courier.cluster_id)

    today = now().today()
    monday = today - datetime.timedelta(days=today.weekday())
    kwargs.setdefault('statistics_week', monday)

    return await CourierScoring(kwargs).save()


async def coffee(shelves_meta, stocks_meta, **kwargs):
    """
    - Два вида кофе, молока, стаканчиков
    - Три типа кофейных напитков
    """

    _store = kwargs.get('store', await store())

    components = {
        'coffee1': await product(
            title='coffee1', quants=400, quant_unit='gram',
            vars={'imported': {'brutto_weight': 400}},
        ),
        'coffee2': await product(
            title='coffee2', quants=500, quant_unit='gram',
            vars={'imported': {'brutto_weight': 500}},
        ),
        'milk1': await product(
            title='milk1', quants=1200, quant_unit='milliliter',
            vars={'imported': {'brutto_weight': 1200}},
        ),
        'milk2': await product(
            title='milk2', quants=2400, quant_unit='milliliter',
            vars={'imported': {'brutto_weight': 2400}},
        ),
        'glass1': await product(title='glass1'),
        'glass2': await product(title='glass2'),

    }

    products = {
        'cappuccino': await product(
            title='cappuccino',
            components=[
                [
                    {
                        'product_id': components['coffee1'].product_id,
                        'count': 4,
                    },
                    {
                        'product_id': components['coffee2'].product_id,
                        'count': 4,
                    },
                ],
                [
                    {
                        'product_id': components['milk1'].product_id,
                        'count': 80,
                    },
                    {
                        'product_id': components['milk2'].product_id,
                        'count': 80,
                    },
                ],
                [
                    {
                        'product_id': components['glass1'].product_id,
                        'count': 1,
                    },
                    {
                        'product_id': components['glass2'].product_id,
                        'count': 1,
                    },
                ],
            ],
            vars={'imported': {'brutto_weight': 112}},
        ),
        'latte': await product(
            title='latte',
            components=[
                [
                    {
                        'product_id': components['coffee2'].product_id,
                        'count': 4,
                    },
                    {
                        'product_id': components['coffee1'].product_id,
                        'count': 4,
                    },
                ],
                [
                    {
                        'product_id': components['milk2'].product_id,
                        'count': 120,
                    },
                    {
                        'product_id': components['milk1'].product_id,
                        'count': 120,
                    },
                ],
                [
                    {
                        'product_id': components['glass2'].product_id,
                        'count': 1,
                    },
                    {
                        'product_id': components['glass1'].product_id,
                        'count': 1,
                    },
                ],
            ],
            vars={'imported': {'netto_weight': 137}},
        ),
        'lungo': await product(
            title='lungo',
            components=[
                [
                    {
                        'product_id': components['coffee1'].product_id,
                        'count': 4,
                    },
                ],
                [
                    {
                        'product_id': components['glass1'].product_id,
                        'count': 1,
                    },
                ],
            ],
            vars={'imported': {'netto_weight': 223}},
        ),
    }

    shelves = {}
    for shelf_k, shelf_type in shelves_meta:
        shelves[shelf_k] = await shelf(
            store=_store, title=shelf_k, type=shelf_type,
        )

    stocks = {}
    for shelf_k, component_k, count in stocks_meta:
        if shelves[shelf_k].is_components:
            count = count * components[component_k].quants

        stocks[f'{shelf_k}_{component_k}'] = await stock(
            shelf=shelves[shelf_k],
            product=components[component_k],
            count=count,
        )

    return shelves, stocks, components, products


async def inventory_snapshot(**kwargs):
    if 'order' in kwargs:
        kwargs.setdefault('order_id', kwargs['order'].order_id)
    if 'product' in kwargs:
        kwargs.setdefault('product_id', kwargs['product'].product_id)

    kwargs.setdefault('shelf_type', 'store')
    kwargs.setdefault('count', 100)
    kwargs.setdefault('result_count', 200)

    return await InventoryRecord(kwargs).save()


async def weight_parent(**kwargs):
    article = random.randint(0, 999999)
    parent_barcode = barcode.weight_pack(article, 0)

    return await product(barcode=[parent_barcode],
                         type_accounting='weight',
                         **kwargs)


async def weight_products(**kwargs):

    childs_weight = kwargs.pop(
        'children',
        [[100, 200], [200, 300], [300, 800]]
    )
    parent = kwargs.pop('product', await weight_parent(**kwargs))

    article, _, _ = barcode.weight_unpack(parent.barcode[0])
    title_parent = parent.title

    products = [parent]
    i = 1
    for low, upper in childs_weight:
        barcode_child = barcode.weight_pack(article, 0, i)
        child = await product(
            title=f'{title_parent:}_{i:02d}',
            parent_id=parent.product_id,
            barcode=[barcode_child],
            lower_weight_limit=low,
            upper_weight_limit=upper,
            type_accounting='weight',
        )
        products.append(child)
        i += 1

    return products


async def gen_barcode(product_id, weight=None):
    if not product_id:
        return

    _product = await Product.load(product_id)

    article, _, _ = barcode.weight_unpack(_product.barcode[0])

    if not weight:
        weight = random.randint(1000, 2000)

    return {'barcode': barcode.weight_pack(article, weight)}


async def create_refund(**kwargs):
    _user = kwargs.pop('user', None)
    kwargs.setdefault('vars', {}).setdefault('need_sell_true_mark', True)
    _order = await order_done(**kwargs)
    await _order.cancel()
    await wait_order_status(_order,
                            ('canceled', 'done'), user_done=_user)

    child_order = await _order.load(_order.vars('child_order_id'))
    if child_order:
        # только для тестов, сложим марки в рефанд
        child_order.vars['parent_assembled_products'] = _order.vars(
            'assembled_products', None)

    return await child_order.save(store_job_event=False)


async def create_shipment_rollback(**kwargs):
    _order = await order_done(**kwargs)

    external_id = uuid()

    child_order = Order(
        {
            'parent': [_order.order_id],
            'external_id': external_id,
            'type': 'shipment_rollback',
            'required': await _order.business.refund_required(),
            'store_id': _order.store_id,
            'company_id': _order.company_id,
            'status': 'reserving',
            'estatus': 'begin',
            'source': 'dispatcher',
            'approved': now(),
            'attr': {
                'doc_number': (
                    _order.attr.get('doc_number') + '-' + external_id[:4]
                ),
                'doc_date': now().strftime('%F'),
                'reason': 'возврта отмены для тестов',
            },
        }
    )
    await child_order.save()

    return child_order


async def cancel_order(**kwargs):
    order_id = kwargs.pop('order_id', None)

    if order_id:
        _order = await Order.load(order_id)
    else:
        _order = await order(**kwargs)

    await wait_order_status(_order, ('processing', 'waiting'))

    await _order.cancel()
    await wait_order_status(_order, ('processing', 'waiting'))
    return _order


async def briefing_ticket(**kwargs):
    kwargs.setdefault('staff_uid', uuid())
    kwargs.setdefault('staff_login', keyword.noun())

    return await BriefingTickets(kwargs).save()


async def multiset(**kwargs):
    result_dict = {}
    fcs = {
        name: obj
        for name, obj in inspect.getmembers(
            sys.modules[__name__],
        ) if inspect.isfunction(obj)
    }
    for fname, argument in kwargs.items():
        if isinstance(argument, list):
            result = await asyncio.gather(
                *[
                    fcs[fname](
                        **kwgs
                    ) for kwgs in argument
                ]
            )
        else:
            result = await fcs[fname](
                **argument
            )
        result_dict[fname] = result
    return result_dict


async def courier_metric_daily(
        _store: 'Store|str' = None,
        courier_cnt: int = None,
        couriers: typing.List[str]=None,
        period: 'typing.Tuple[datetime.date|str, datetime.date|str]' = None,
        rt_metrics=False,
) -> typing.List[CourierMetric]:
    # pylint: disable=too-many-locals, too-many-statements
    # pylint: disable=import-outside-toplevel
    if rt_metrics:
        from tests.conftest import create_ch_models
        await create_ch_models()

    if _store is None:
        _store = await store()
    elif isinstance(_store, str):
        _store = await Store.load(_store)
    if courier_cnt is None:
        courier_cnt = 1
    if couriers is None:
        couriers = [await courier(store=_store) for _ in range(courier_cnt)]
    else:
        couriers = [await Courier.load(_id) for _id in couriers]
    if period is None:
        _date = now().date()
        period = (_date, _date)
    else:
        period = [
            datetime.date.fromisoformat(day) if isinstance(day, str) else day
            for day
            in period
        ]

    result = []

    processed = now()
    start_date, end_date = period
    for days in range((end_date - start_date).days + 1):
        current_date = start_date + datetime.timedelta(days=days)
        current_time = datetime.datetime(*current_date.timetuple()[:-2])

        store_metric = CourierMetric(
            date=current_date,
            time=current_time,
            store_id=_store.store_id,
            store_cluster=random.randint(1, 9),
            store_factor=random.randint(1, 9),
            grand_total_cnt=0,
            success_delivered_cnt=0,
            success_delivered_cnt_10=0,
            success_delivered_cnt_25=0,
            success_delivered_cnt_40=0,
            cur_dur_sec_plan=0,
            early_leaving_dur_sec=0,
            lateness_dur_sec=0,
            cur_dur_sec_not_start=0,
            fact_shift_dur_sec=0,
            cte_dur_sec=0,
            shift_dur_sec_work_promise=0,
            shift_dur_sec_work_capability=7 * 60 * 60 * len(couriers),
            cpo_orders=0,
            cpo_cost=0.0,
            batch_cnt=0,
            fallback_cnt=0,
            surge_cnt=0,
            complaints_all_cnt=0,
            complaints_10_cnt=0,
            processed=processed,
        )
        await store_metric.save()
        result.append(store_metric)

        for _courier in couriers:
            courier_name = ' '.join(
                it for it in
                [_courier.first_name, _courier.last_name, _courier.middle_name]
                if it
            )
            _grand_total_cnt = random.randrange(10, 100)
            store_metric.grand_total_cnt += _grand_total_cnt

            # Успешно доставленных заказов должно быть меньше, чем всех
            _success_delivered_cnt = random.randrange(
                round(_grand_total_cnt * 0.8),
                _grand_total_cnt
            )
            store_metric.success_delivered_cnt += _success_delivered_cnt

            # 0-20% Успешно доставленных заказов c опоздание более 10 минут
            _success_delivered_cnt_10 = random.randrange(
                0, round(_success_delivered_cnt * 0.2))
            store_metric.success_delivered_cnt_10 += _success_delivered_cnt_10

            # 0-20% Успешно доставленных заказов c опоздание более 25 минут
            _success_delivered_cnt_25 = random.randrange(
                0, round(_success_delivered_cnt * 0.2))
            store_metric.success_delivered_cnt_25 += _success_delivered_cnt_25

            # 0-20% Успешно доставленных заказов c опоздание более 40 минут
            _success_delivered_cnt_40 = random.randrange(
                0, round(_success_delivered_cnt * 0.2))
            store_metric.success_delivered_cnt_40 += _success_delivered_cnt_40

            # Рабочая смена от 4 до 8 часов
            _cur_dur_sec_plan = random.randrange(4, 8) * 60 * 60
            store_metric.cur_dur_sec_plan += _cur_dur_sec_plan

            # Шанс раннего ухода 50%. Максимум 1 час
            _early_leaving_dur_sec = (
                int(random.random() < 0.5)
                * random.randrange(0, 1 * 60 * 60)
            )
            store_metric.early_leaving_dur_sec += _early_leaving_dur_sec

            # Шанс опоздания 50%. Максимум 1 час
            _lateness_dur_sec = (
                int(random.random() < 0.5)
                * random.randrange(0, 1 * 60 * 60)
            )
            store_metric.lateness_dur_sec += _lateness_dur_sec

            # Шанс не выхода на смену 33%. Смена 4-8 часов
            _cur_dur_sec_not_start = (
                int(random.random() < 0.33)
                * random.randrange(4, 8) * 60 * 60
            )
            store_metric.cur_dur_sec_not_start += _cur_dur_sec_not_start

            # Фактически отработанное время + возможная переработка до 1 часа
            _fact_shift_dur_sec = (
                _cur_dur_sec_plan
                - _early_leaving_dur_sec
                - _lateness_dur_sec
                + random.randrange(0, 1) * random.randrange(0, 1 * 60 * 60)
            )
            store_metric.fact_shift_dur_sec += _fact_shift_dur_sec

            # Время доставки заказов. 25%-75% от всего рабочего времени
            _cte_dur_sec = random.randrange(
                round(_fact_shift_dur_sec * 0.25),
                round(_fact_shift_dur_sec * 0.75)
            )
            store_metric.cte_dur_sec += _cte_dur_sec

            _shift_dur_sec_work_promise = _cur_dur_sec_plan
            store_metric.shift_dur_sec_work_promise += \
                _shift_dur_sec_work_promise

            # Норма заполняемости смен 7 часов в день на курьера
            _shift_dur_sec_work_capability = 7 * 60 * 60

            _cpo_orders = _success_delivered_cnt
            store_metric.cpo_orders += _cpo_orders

            _cpo_cost = random.random() * 100 * _success_delivered_cnt
            store_metric.cpo_cost += _cpo_cost

            # Batch 0% - 10% от всех заказов
            _batch_cnt = random.randint(0, round(_success_delivered_cnt * 0.1))
            store_metric.batch_cnt += _batch_cnt

            # Fallback 0% - 10% от всех заказов
            _fallback_cnt = random.randint(0,
                                           round(_success_delivered_cnt * 0.1))
            store_metric.fallback_cnt += _fallback_cnt

            # Surge 0% - 10% от всех заказов
            _surge_cnt = random.randint(0, round(_success_delivered_cnt * 0.1))
            store_metric.surge_cnt += _surge_cnt

            # Жалобы 0% - 10% от всех заказов
            _complaints_all_cnt = (
                random.randint(0, 1)
                * random.randint(0, round(_success_delivered_cnt * 0.1))
            )
            store_metric.complaints_all_cnt += _complaints_all_cnt

            _complaints_10_cnt = random.randint(0, _complaints_all_cnt)
            store_metric.complaints_10_cnt += _complaints_10_cnt

            _courier_metric = CourierMetric(
                date=current_date,
                time=current_time,
                store_id=_store.store_id,
                external_courier_id=_courier.external_id,
                courier_id=_courier.courier_id,
                courier_name=courier_name,
                grand_total_cnt=_grand_total_cnt,
                success_delivered_cnt=_success_delivered_cnt,
                success_delivered_cnt_10=_success_delivered_cnt_10,
                success_delivered_cnt_25=_success_delivered_cnt_25,
                success_delivered_cnt_40=_success_delivered_cnt_40,
                cur_dur_sec_plan=_cur_dur_sec_plan,
                early_leaving_dur_sec=_early_leaving_dur_sec,
                lateness_dur_sec=_lateness_dur_sec,
                cur_dur_sec_not_start=_cur_dur_sec_not_start,
                fact_shift_dur_sec=_fact_shift_dur_sec,
                cte_dur_sec=_cte_dur_sec,
                shift_dur_sec_work_promise=_shift_dur_sec_work_promise,
                shift_dur_sec_work_capability=_shift_dur_sec_work_capability,
                cpo_orders=_cpo_orders,
                cpo_cost=_cpo_cost,
                batch_cnt=_batch_cnt,
                fallback_cnt=_fallback_cnt,
                surge_cnt=_surge_cnt,
                complaints_all_cnt=_complaints_all_cnt,
                complaints_10_cnt=_complaints_10_cnt,
                processed=processed,
            )
            await _courier_metric.save()
            result.append(_courier_metric)

            if not rt_metrics:
                continue
            at_12 = (
                time2time(current_date.isoformat())
                + datetime.timedelta(hours=12)
            )
            _order = await order(store=_store)
            await ch_grocery_order_created(
                timestamp=at_12 + datetime.timedelta(minutes=0),
                order=_order,
                store=_store,
                courier=_courier,
            )

            await ch_grocery_order_matched(
                timestamp=at_12 + datetime.timedelta(minutes=2),
                order=_order,
                store=_store,
                courier=_courier,
            )

            await ch_wms_order_complete(
                timestamp=at_12 + datetime.timedelta(minutes=3),
                order=_order,
                store=_store,
            )

            await ch_grocery_delivering_arrived(
                timestamp=at_12 + datetime.timedelta(minutes=13),
                order=_order,
                store=_store,
                courier=_courier,
            )

            await ch_grocery_return_depot(
                timestamp=at_12 + datetime.timedelta(minutes=25),
                order=_order,
                store=_store,
                courier=_courier,
            )

        await store_metric.save()

    return result


async def writeoff_limit(**kwargs):
    _cluster = kwargs.pop('cluster', None)
    if not _cluster:
        _cluster = await cluster()
    elif isinstance(_cluster, str):
        _cluster = await cluster(title=_cluster)

    _factor = kwargs.pop('factor', random.randrange(0, 10))
    _date = kwargs.pop('date', datetime.date.today())
    _date = (datetime.date.fromisoformat(_date)
             if isinstance(_date, str) else _date)

    return await WriteoffLimit(
        date=datetime.date(_date.year, _date.month, 1),
        cluster_id=_cluster.cluster_id,
        factor=_factor,
        check_valid_max=kwargs.get('check_valid_max', random.random() * 20),
        damage_max=kwargs.get('damage_max', random.random() * 5),
        refund_max=kwargs.get('refund_max', random.random() * 5),
        recount_min=kwargs.get('recount_min', random.random() * 5),
        recount_max=kwargs.get('recount_max', random.random() * 5),
        blind_acceptance_max=kwargs.get('blind_acceptance_max',
                                        random.random() * 5),
    ).save()


async def store_metric_daily(
        _store: 'Store|str' = None,
        executer_cnt: int = None,
        executers: typing.List[str] = None,
        period: 'typing.Tuple[datetime.date|str, datetime.date|str]' = None,
        **kwargs,
) -> typing.List[StoreMetric]:
    # pylint: disable=too-many-locals, too-many-statements
    if _store is None:
        _store = await store()
    elif isinstance(_store, str):
        _store = await Store.load(_store)
    if executer_cnt is None:
        executer_cnt = 1
    if executers is None:
        executers = [
            await user(store=_store, role='executer')
            for _ in range(executer_cnt)
        ]
    else:
        executers = [await User.load(_id) for _id in executers]
    if period is None:
        _date = now().date()
        period = (_date, _date)
    else:
        period = [
            datetime.date.fromisoformat(day) if isinstance(day, str) else day
            for day
            in period
        ]

    _store_factor = kwargs.pop('store_factor', random.randrange(0, 10))
    _store_cluster = kwargs.pop('store_cluster', random.randrange(0, 10))

    result = []

    processed = now()
    start_date, end_date = period
    for days in range((end_date - start_date).days + 1):
        current_date = start_date + datetime.timedelta(days=days)
        current_time = datetime.datetime(*current_date.timetuple()[:-2])

        await MDAudit(
            date=current_date - datetime.timedelta(days=current_date.weekday()),
            store_id=_store.store_id,
            external_store_id=_store.external_id,
            value=random.random() * 100
        ).save()

        store_metric = StoreMetric(
            date=current_date,
            time=current_time,
            store_id=_store.store_id,
            store_factor=_store_factor,
            store_cluster=_store_cluster,
            grand_total_cnt=0,
            success_delivered_cnt=0,
            recount_writeoffs_cost_lcy=random.random() * 10000,
            damage_writeoffs_cost_lcy=random.random() * 10000,
            refund_writeoffs_cost_lcy=random.random() * 10000,
            check_valid_writeoffs_cost_lcy=random.random() * 100000,
            gross_revenue_w_pur_cost_lcy = 100000 + random.random() * 100000,
            processed=processed,
            compensations={
                "not_delivered": random.randint(1, 5),
                "wrong_product": random.randint(1, 5),
                "wrong_order": random.randint(1, 5),
                "bad_product": random.randint(1, 5),
                "overripe_product": random.randint(1, 5),
                "freeze_product": random.randint(1, 5),
                "unfreeze_product": random.randint(1, 5),
                "lifetime_limit": random.randint(1, 5),
                "damaged_product": random.randint(1, 5),
                "overcooked": random.randint(1, 5),
                "others": random.randint(1, 5),
            }
        )
        await store_metric.save()
        result.append(store_metric)

        for _executer in executers:
            _grand_total_cnt = random.randrange(10, 100)
            store_metric.grand_total_cnt += _grand_total_cnt

            # Успешно доставленных заказов должно быть меньше, чем всех
            _success_delivered_cnt = random.randrange(
                round(_grand_total_cnt * 0.8),
                _grand_total_cnt
            )
            store_metric.success_delivered_cnt += _success_delivered_cnt

            # Собранных товаров, должно быть не меньше чем заказов
            _overall_items = random.randrange(_grand_total_cnt,
                                              _grand_total_cnt * 2)
            store_metric.overall_items += _overall_items

            # Время затраченное на сборку 1 штуки от 10 до 100 секунд
            _overall_time = random.randrange(
                10 * _overall_items,
                100 * _overall_items
            )
            store_metric.overall_time += _overall_time

            # Количетсво заказов, которые ждали сборки
            _waiting_orders = _grand_total_cnt - 1
            store_metric.waiting_orders += _waiting_orders

            # Время ожидание 1 заказа в очереди от 60 до 120 секунд
            _waiting_sec = random.randrange(
                60 * _waiting_orders,
                120 * _waiting_orders
            )
            store_metric.waiting_sec += _waiting_sec

            # Рабочая смена 4-8 часов
            _cur_dur_sec_plan = random.randrange(4, 8) * 60 * 60
            store_metric.cur_dur_sec_plan += _cur_dur_sec_plan

            # Шанс раннего ухода 50%. Максимум 1 час
            _early_leaving_dur_sec = (
                int(random.random() < 0.5)
                * random.randrange(0, 1 * 60 * 60)
            )
            store_metric.early_leaving_dur_sec += _early_leaving_dur_sec

            # Шанс опоздания 50%. Максимум 1 час
            _lateness_dur_sec = (
                int(random.random() < 0.5)
                * random.randrange(0, 1 * 60 * 60)
            )
            store_metric.lateness_dur_sec += _lateness_dur_sec

            # Шанс не выхода на смену 33%. Смена 4-8 часов
            _cur_dur_sec_not_start = (
                int(random.random() < 0.33)
                * random.randrange(4, 8) * 60 * 60
            )
            store_metric.cur_dur_sec_not_start += _cur_dur_sec_not_start

            # Фактически отработанное время + возможная переработка до 1 часа
            _fact_shift_dur_sec = (
                _cur_dur_sec_plan
                - _early_leaving_dur_sec
                - _lateness_dur_sec
                + random.randrange(0, 1) * random.randrange(0, 1 * 60 * 60)
            )
            store_metric.fact_shift_dur_sec += _fact_shift_dur_sec

            # Жалобы не больше 10% от числа заказов
            _complaints_all_cnt = (
                random.randint(0, 1)
                * random.randint(0, round(_success_delivered_cnt * 0.1))
            )
            store_metric.complaints_all_cnt += _complaints_all_cnt

            # Жалоб с компенсаций не больше всех жалоб
            _complaints_10_cnt = random.randint(0, _complaints_all_cnt)
            store_metric.complaints_10_cnt += _complaints_10_cnt

            _store_metric = StoreMetric(
                date=current_date,
                time=current_time,
                store_id=_store.store_id,
                external_executer_id=_executer.fullname,
                executer_id=_executer.fullname,
                executer_name=_executer.fullname,
                grand_total_cnt=_grand_total_cnt,
                success_delivered_cnt=_success_delivered_cnt,
                overall_items=_overall_items,
                overall_time=_overall_time,
                waiting_orders=_waiting_orders,
                waiting_sec=_waiting_sec,
                cur_dur_sec_plan=_cur_dur_sec_plan,
                early_leaving_dur_sec=_early_leaving_dur_sec,
                lateness_dur_sec=_lateness_dur_sec,
                cur_dur_sec_not_start=_cur_dur_sec_not_start,
                fact_shift_dur_sec=_fact_shift_dur_sec,
                complaints_all_cnt=_complaints_all_cnt,
                complaints_10_cnt=_complaints_10_cnt,
                processed=processed,
            )
            await _store_metric.save()
            result.append(_store_metric)
        await store_metric.save()

    return result


async def order_log(**kwargs):
    _order_id = kwargs.pop('order_id', None)
    if _order_id:
        _order = await Order.load(_order_id)
    else:
        _order_kwargs = kwargs.pop('order', {})
        _order = await order(**_order_kwargs)

    return await _order.save(
        order_logs=[
            dict(
                source=kwargs.pop('source', 'save'),
                **kwargs
            )
        ],
    )


async def time(**kwargs):
    """Для фронтовых тестов можно сгенерировать дату со смещением"""

    tz = None
    if 'tz' in kwargs:
        tz = tzone(kwargs['tz'])

    _now = now(tz=tz).replace(microsecond=0)

    # Отступить от текущего
    _delta = {k: v for k, v in kwargs.items() if k in {
        'days', 'seconds', 'microseconds', 'milliseconds', 'minutes',
        'hours', 'weeks',
    }}
    if _delta:
        _now = _now + datetime.timedelta(**_delta)

    # Перезаписать параметры
    _replace = {k: v for k, v in kwargs.items() if k in {
        'year', 'month', 'day', 'hour', 'minute', 'second',
        'microsecond', 'fold'
    }}
    if _replace:
        _now = _now.replace(**_replace)

    # Если передан конкретный формат
    if 'format' in kwargs:
        return _now.strftime(kwargs['format'])

    return _now.isoformat()


async def suggests_done(order_id, **kwargs):
    _order = await Order.load(order_id)
    await wait_order_status(_order, ('processing', 'waiting'))
    suggests = await Suggest.list_by_order(order_id)
    for _suggest in suggests:
        if _suggest.status != 'done':
            await _suggest.done(**kwargs)
    return _order


async def repair_task(**kwargs):
    _company = kwargs.pop('company', None)
    _store = kwargs.pop('store', None)

    if 'store_id' not in kwargs:
        if _store:
            kwargs['store_id'] = _store.store_id
        elif _company:
            kwargs['store_id'] = (await store(company=_company)).store_id
        elif 'company_id' in kwargs:
            kwargs['store_id'] = (
                await store(company_id=kwargs['company_id'])).store_id
        else:
            kwargs['store_id'] = (await store()).store_id

    if 'company_id' not in kwargs:
        if _company:
            kwargs['company_id'] = _company.company_id
        elif _store:
            kwargs['company_id'] = _store.company_id
        else:
            kwargs['company_id'] = (await company()).company_id

    kwargs.setdefault('external_id', uuid())
    kwargs.setdefault('type', 'assets')
    kwargs.setdefault('source', 'lavkach')
    kwargs.setdefault('status', 'IN_PROGRESS')
    kwargs.setdefault('vars', {'lavkach_type': 'REPAIR'})

    return await RepairTask(**kwargs).save()


# pylint: disable=unused-argument
async def tsd_order_check_qr_action(
        user_id: str, order_id: str, **kwargs
):
    _user = await User.load(user_id)
    _order = await Order.load(order_id)
    return await get_qr_action_data(
        cur_user=_user,
        qr_action_type='tsd_order_check',
        generator_params={'order': _order},
    )


# pylint: disable=unused-argument
async def trusted_acceptance_qr_action(
        user_id: str, order_id: str, **kwargs
):
    _user = await User.load(user_id)
    _order = await Order.load(order_id)
    return await get_qr_action_data(
        cur_user=_user,
        qr_action_type='trusted_acceptance',
        generator_params={'order': _order},
    )


# pylint: disable=unused-argument
async def store_checkin_qr_action(
        user_id: str, store_id: str, **kwargs
):
    _user = await User.load(user_id)
    _store = await Store.load(store_id)
    return await get_qr_action_data(
        cur_user=_user,
        qr_action_type='store_checkin',
        generator_params={'store': _store},
    )

async def ch_order_store(has_performer=False, save_store_id=False, **kwargs):
    kwargs.setdefault('timestamp',  now())
    if 'store' in kwargs:
        kwargs['depot_id'] = kwargs['store'].external_id
    if not kwargs.get('depot_id', None):
        _store = None
        if 'order' in kwargs:
            _store = await Store.load(kwargs['order'].store_id)
        if _store is None:
            _store = await store()
        kwargs['depot_id'] = _store.external_id

    if 'order' in kwargs:
        kwargs['order_id'] = kwargs['order'].external_id
    if not kwargs.get('order_id', None):
        _store = await Store.load(kwargs['depot_id'], by='external')
        _order = await order(store_id=_store.store_id)
        kwargs['order_id'] = _order.external_id

    if has_performer:
        if 'courier' in kwargs:
            kwargs['performer_id'] = kwargs['courier'].external_id
        if not kwargs.get('performer_id', None):
            _courier = await courier()
            kwargs['performer_id'] = _courier.external_id

    if save_store_id:
        _store = await Store.load(kwargs['depot_id'], by='external')
        kwargs['store_id'] = _store.store_id
    return kwargs

async def ch_grocery_order_created(**kwargs):
    kwargs = await ch_order_store(**kwargs)
    kwargs.setdefault('max_eta',  3600)
    kwargs.setdefault('delivery_type',  'dispatch')

    topic = GroceryOrderCreated(**kwargs)
    client = ClickHouseClient('grocery')

    await client.request_query(
        query=topic.insert_query(),
        response_format=None
    )
    return topic

async def ch_grocery_order_assemble_ready(**kwargs):
    kwargs = await ch_order_store(**kwargs)

    topic = GroceryOrderAssembleReady(**kwargs)
    client = ClickHouseClient('grocery')

    await client.request_query(
        query=topic.insert_query(),
        response_format=None
    )
    return topic

async def ch_wms_order_processing(**kwargs):
    kwargs = await ch_order_store(**kwargs, save_store_id=True)

    topic = WmsOrderProcessing(**kwargs)
    client = ClickHouseClient('grocery')

    await client.request_query(
        query=topic.insert_query(),
        response_format=None
    )
    return topic

async def ch_wms_order_complete(**kwargs):
    kwargs = await ch_order_store(**kwargs, save_store_id=True)

    topic = WmsOrderComplete(**kwargs)
    client = ClickHouseClient('grocery')

    await client.request_query(
        query=topic.insert_query(),
        response_format=None
    )
    return topic

async def ch_grocery_order_matched(**kwargs):
    kwargs = await ch_order_store(**kwargs, has_performer=True)
    kwargs.setdefault('claim_id',  uuid())
    kwargs.setdefault('delivery_type',  'courier')

    topic = GroceryOrderMatched(**kwargs)
    client = ClickHouseClient('grocery')

    await client.request_query(
        query=topic.insert_query(),
        response_format=None
    )
    return topic

async def ch_grocery_order_pickup(**kwargs):
    kwargs = await ch_order_store(**kwargs, has_performer=True)

    topic = GroceryOrderPickup(**kwargs)
    client = ClickHouseClient('grocery')

    await client.request_query(
        query=topic.insert_query(),
        response_format=None
    )
    return topic

async def ch_grocery_order_delivered(**kwargs):
    kwargs = await ch_order_store(**kwargs, has_performer=True)

    topic = GroceryOrderDelivered(**kwargs)
    client = ClickHouseClient('grocery')

    await client.request_query(
        query=topic.insert_query(),
        response_format=None
    )
    return topic

async def ch_grocery_order_closed(**kwargs):
    kwargs = await ch_order_store(**kwargs)
    kwargs.setdefault('is_canceled', 0)

    topic = GroceryOrderClosed(**kwargs)
    client = ClickHouseClient('grocery')

    await client.request_query(
        query=topic.insert_query(),
        response_format=None
    )
    return topic

async def ch_grocery_delivering_arrived(**kwargs):
    kwargs = await ch_order_store(**kwargs, has_performer=True)

    topic = GroceryDeliveringArrived(**kwargs)
    client = ClickHouseClient('grocery')

    await client.request_query(
        query=topic.insert_query(),
        response_format=None
    )
    return topic

async def ch_grocery_return_depot(**kwargs):
    kwargs = await ch_order_store(**kwargs, has_performer=True)

    topic = GroceryReturnDepot(**kwargs)
    client = ClickHouseClient('grocery')

    await client.request_query(
        query=topic.insert_query(),
        response_format=None
    )
    return topic


async def ch_grocery_shift_update(**kwargs):
    kwargs = await ch_order_store(**kwargs, has_performer=True)
    if not '_timestamp' in kwargs:
        kwargs['_timestamp'] = kwargs['timestamp']

    topic = GroceryShiftUpdate(**kwargs)
    client = ClickHouseClient('grocery')

    await client.request_query(
        query=topic.insert_query(),
        response_format=None
    )
    return topic

async def ch_wms_order_status_update(**kwargs):
    kwargs.setdefault('timestamp',  now())
    if kwargs.get('order_id'):
        kwargs['order'] = await Order.load(kwargs['order_id'])

    assert kwargs.get('order'), 'order or order_id is required'
    _order: Order = kwargs['order']

    _store = await Store.load(_order.store_id)
    kwargs['company_id'] = _store.company_id
    kwargs['cluster_id'] = _store.cluster_id

    kwargs['store_id'] = _store.store_id
    kwargs.setdefault('type', _order.type)
    kwargs['order_id'] = _order.order_id

    kwargs.setdefault('status', _order.status)
    kwargs.setdefault('estatus', _order.estatus)
    kwargs.setdefault('eda_status', _order.eda_status)

    kwargs['order_external_id'] = _order.external_id
    kwargs['store_external_id'] = _store.external_id

    kwargs['created_timestamp'] = _order.created

    topic = WmsOrderStatusUpdated(**kwargs)
    client = ClickHouseClient('grocery')

    await client.request_query(
        query=topic.insert_query(),
        response_format=None
    )
    return topic

async def true_mark_object(**kwargs):
    cur_order = kwargs.get('order')
    if 'order_id' in kwargs:
        cur_order = await Order.load(kwargs['order_id'])
    if not cur_order:
        cur_order = await order(**kwargs)

    cur_product = kwargs.get('product')
    if 'product_id' in kwargs:
        cur_product = await Product.load(kwargs['product_id'])
    if not cur_product:
        cur_product = await product(true_mark=True)

    if 'suggest' in kwargs:
        cur_suggest = kwargs.pop('suggest')
        kwargs['suggest_id'] = cur_suggest.suggest_id

    if 'suggest_id' not in kwargs:
        cur_suggest = await suggest(
            order=cur_order,
            product_id=cur_product.product_id,
        )
        kwargs['suggest_id'] = cur_suggest.suggest_id

    if 'value' not in kwargs:
        kwargs['value'] = await true_mark_value(product=cur_product)

    true_mark_params = {
        'company_id': cur_order.company_id,
        'store_id': cur_order.store_id,
        'order_id': cur_order.order_id,
        'product_id': cur_product.product_id,
    }
    true_mark_params.update(kwargs)

    return await TrueMark(**true_mark_params).save()


async def default_store_config(**kwargs):
    if 'object_id' not in kwargs:
        if 'cluster' in kwargs:
            level = 'cluster'
            _cluster = kwargs.pop('cluster')
            object_id = _cluster.cluster_id
        else:
            level = 'company'
            if 'company' in kwargs:
                _company = kwargs.pop('company')
            else:
                _company = await company()
            object_id = _company.company_id

        kwargs['object_id'] = object_id
        kwargs['level'] = level

    return await DefaultStoreConfig(kwargs).save()


async def set_pause(**kwargs):
    _order = await Order.load(kwargs['order_id'])
    duration = kwargs.get('duration', 30)
    _order.set_paused_until(duration)
    await _order.save()
    return _order


async def store_problem(**kwargs):
    _store = kwargs.get('store')
    if 'store_id' in kwargs:
        _store = await Store.load(kwargs['store_id'])
    if not _store:
        _store = await store()

    kwargs['company_id'] = _store.company_id
    kwargs['cluster_id'] = _store.cluster_id
    kwargs['store_id'] = _store.store_id

    kwargs.setdefault(
        'timestamp_group',
        StoreProblem.calculate_timestamp_group(_store)
    )
    kwargs.setdefault('head_supervisor_id', None)
    kwargs.setdefault('supervisor_id', None)
    kwargs.setdefault('reason', 'count')
    kwargs.setdefault('order_type', 'order')
    kwargs.setdefault('order_status', 'processing')
    kwargs.setdefault('is_resolved', False)
    kwargs.setdefault('details', [])

    return await StoreProblem(kwargs).save()


async def store_health(recalculate=False, **kwargs):
    _store = kwargs.get('store')
    if not _store and 'store_id' in kwargs:
        _store = await Store.load(kwargs['store_id'])
    if not _store:
        _store = await store()

    kwargs.setdefault('company_id', _store.company_id)
    kwargs.setdefault('cluster_id', _store.cluster_id)
    kwargs.setdefault('store_id', _store.store_id)
    kwargs.setdefault('head_supervisor_id', None)
    kwargs.setdefault('supervisor_id', None)
    kwargs.setdefault('problems_count', 1)

    kwargs['entity'] = 'store'
    kwargs['entity_id'] = _store.store_id
    kwargs['has_problem'] = False
    kwargs['stores_total'] = 1
    kwargs['stores_with_problems'] = 0
    kwargs['children_total'] = 1
    kwargs['children_with_problems'] = 0
    if kwargs['problems_count'] > 0:
        kwargs.setdefault('reason', 'document')
        kwargs['has_problem'] = True
        kwargs['stores_with_problems'] = 1
        kwargs['children_with_problems'] = 1

    _store_health = StoreHealth(kwargs)
    _store_health.rehashed(
        reason=True,
        problems_count=True,
        has_problem=True,
        stores_total=True,
        stores_with_problems=True,
        children_total=True,
        children_with_problems=True,
        supervisor_id=True,
        head_supervisor_id=True,
    )
    await _store_health.save()

    if recalculate:
        await StoreHealth.recalculate(
            [_store.company_id], [_store.cluster_id]
        )
    return _store_health


async def file_meta(**kwargs):
    user_: 'User|None' = None
    if 'user' in kwargs:
        user_ = kwargs.pop('user')
        kwargs['user_id'] = user_.user_id
    elif 'user_id' in kwargs:
        user_ = await User.load(kwargs['user_id'])

    store_: 'Store|None' = None
    if 'store' in kwargs:
        store_ = kwargs.pop('store')
        kwargs['store_id'] = store_.store_id
    elif 'store_id' in kwargs:
        store_ = await Store.load(kwargs['store_id'])

    company_: 'Company|None' = None
    if 'company' in kwargs:
        company_ = kwargs.pop('company')
        kwargs['company_id'] = company_.company_id
    elif 'company_id' in kwargs:
        company_ = await Company.load(kwargs['company_id'])

    if user_ is None:
        user_ = await user(
            company_id=getattr(company_, 'company_id'),
            store_id=getattr(store_, 'store_id'),
        )

    kwargs['company_id'] = user_.company_id
    kwargs['store_id'] = user_.store_id

    kwargs.setdefault('filename', uuid())
    kwargs.setdefault('storage', 's3')

    return await FileMeta(kwargs).save()


async def tablo_metric(recalculate=False, **kwargs):
    _store = kwargs.get('store')
    if not _store and 'store_id' in kwargs:
        _store = await Store.load(kwargs['store_id'])
    if not _store:
        _store = await store()

    kwargs.setdefault('calculated', now())
    kwargs.setdefault('slice', '1h')
    kwargs.setdefault('company_id', _store.company_id)
    kwargs.setdefault('cluster_id', _store.cluster_id)
    kwargs.setdefault('store_id', _store.store_id)
    kwargs.setdefault('head_supervisor_id', None)
    kwargs.setdefault('supervisor_id', None)

    kwargs['entity'] = 'store'
    kwargs['entity_id'] = _store.store_id

    _tablo_metric = TabloMetric(kwargs)
    _tablo_metric.rehashed(
        metrics=True,
        supervisor_id=True,
        head_supervisor_id=True,
    )
    await _tablo_metric.save()

    if recalculate:
        await TabloMetric.recalculate(
            [_store.company_id], [_store.cluster_id]
        )
    return _tablo_metric


async def rack_zone(**kwargs):
    cur_store = None
    if kwargs.get('store'):
        cur_store = kwargs.pop('store')
    if kwargs.get('store_id'):
        cur_store = await Store.load(kwargs.pop('store_id'))
    if cur_store is None:
        cur_store = await store(company_id=kwargs.get('company_id'))

    kwargs['store_id'] = cur_store.store_id
    kwargs['company_id'] = cur_store.company_id
    kwargs.setdefault('title', f'Тестовая зона стеллажа - {keyword.keyword()}')

    return await RackZone(kwargs).save()


async def rack(**kwargs):
    cur_zone = None
    if kwargs.get('rack_zone'):
        cur_zone = kwargs.pop('rack_zone')
    if kwargs.get('rack_zone_id'):
        cur_zone = await RackZone.load(kwargs.pop('rack_zone_id'))
    if cur_zone is None:
        cur_zone = await rack_zone(
            store_id=kwargs.get('store_id'),
            company_id=kwargs.get('company_id')
        )
    kwargs['rack_zone_id'] = cur_zone.rack_zone_id
    kwargs['rack_zone_type'] = cur_zone.type
    kwargs['company_id'] = cur_zone.company_id
    kwargs['store_id'] = cur_zone.store_id
    kwargs.setdefault('title', f'Тестовый стеллаж - {keyword.keyword()}')

    return await Rack(kwargs).save()
