import dataclasses
import datetime
from typing import List
from typing import Optional


@dataclasses.dataclass
class SharedOrders:
    order_id: str
    sharing_key: str
    finished_at: Optional[datetime.datetime]
    phone_ids: Optional[List[str]]
    application: Optional[str]
    tariff_class: Optional[str]
    user_exists: Optional[List[bool]]
    admin_name: Optional[str]
    sharing_on: Optional[bool]


def select_by_order_id(pgsql, order_id) -> Optional[SharedOrders]:
    cursor = pgsql['order_route_sharing'].cursor()
    cursor.execute(
        f'SELECT '
        f'  order_id, sharing_key, finished_at, application, tariff_class '
        f'FROM '
        f'order_route_sharing.sharing_keys WHERE '
        f'order_id=\'{order_id}\'',
    )
    result = cursor.fetchone()
    if not result:
        return None
    order_id, sharing_key, finished_at, application, tariff_class = result

    cursor.execute(
        f'SELECT phone_id, is_user_exists FROM '
        f'order_route_sharing.phone_ids WHERE '
        f'sharing_key=\'{sharing_key}\'',
    )
    result = cursor.fetchall()
    phone_ids = None
    user_exists = None
    if result:
        phone_ids = [item[0] for item in result]
        user_exists = [item[1] for item in result]

    cursor.execute(
        f'SELECT sharing_key, admin_name, sharing_on FROM '
        f'order_route_sharing.family_rides WHERE '
        f'sharing_key=\'{sharing_key}\'',
    )
    result = cursor.fetchone()
    admin_name = None
    sharing_on = None
    if result:
        sharing_key, admin_name, sharing_on = result

    return SharedOrders(
        order_id=order_id,
        sharing_key=sharing_key,
        finished_at=finished_at,
        application=application,
        tariff_class=tariff_class,
        phone_ids=phone_ids,
        user_exists=user_exists,
        admin_name=admin_name,
        sharing_on=sharing_on,
    )
