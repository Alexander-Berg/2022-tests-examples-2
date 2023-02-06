from . import models

ALL_RECEIPTS = {
    'order': [
        models.Item(item_id='333', price='500', quantity='1'),
        models.Item(item_id='444', price='100', quantity='2'),
    ],
    'delivery': [
        models.Item(
            item_id='item_delivery',
            price='300',
            quantity='1',
            item_type=models.ItemType.delivery,
        ),
    ],
    'tips': [
        models.Item(
            item_id='item_tips',
            price='200',
            quantity='1',
            item_type=models.ItemType.tips,
        ),
    ],
}

ORDER_AND_TIPS_RECEIPTS = {
    'order': [
        models.Item(item_id='333', price='500', quantity='1'),
        models.Item(item_id='444', price='100', quantity='2'),
        models.Item(
            item_id='item_delivery',
            price='300',
            quantity='1',
            item_type=models.ItemType.delivery,
        ),
    ],
    'tips': [
        models.Item(
            item_id='item_tips',
            price='200',
            quantity='1',
            item_type=models.ItemType.tips,
        ),
    ],
}

ORDER_RECEIPT = {
    'order': [
        models.Item(item_id='333', price='500', quantity='1'),
        models.Item(item_id='444', price='100', quantity='2'),
        models.Item(
            item_id='item_delivery',
            price='300',
            quantity='1',
            item_type=models.ItemType.delivery,
        ),
        models.Item(
            item_id='item_tips',
            price='200',
            quantity='1',
            item_type=models.ItemType.tips,
        ),
    ],
}

MISSING_DELIVERY_RECEIPT = {
    'order': [
        models.Item(item_id='333', price='500', quantity='1'),
        models.Item(item_id='444', price='100', quantity='2'),
    ],
    'delivery': [],
    'tips': [
        models.Item(
            item_id='item_tips',
            price='200',
            quantity='1',
            item_type=models.ItemType.tips,
        ),
    ],
}
