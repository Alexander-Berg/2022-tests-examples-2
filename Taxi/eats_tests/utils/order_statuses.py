import enum


# from https://bb.yandex-team.ru/projects/EDA/repos/
# backend_service_core/browse/src/App/Entity/Order.php
class EatsOrderStatus(enum.Enum):
    AWAITING_CARD_PAYMENT = 8
    UNCONFIRMED = 0
    CALL_CENTER_CONFIRMED = 1
    PLACE_CONFIRMED = 2
    READY_FOR_DELIVERY = 3
    ORDER_TAKEN = 9
    ARRIVED_TO_CUSTOMER = 6
    DELIVERED = 4
    CANCELLED = 5
    CUSTOMER_NO_SHOW = 7
