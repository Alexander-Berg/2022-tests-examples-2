import bson


def get_bson_order_data(db, request):
    assert request.json['lookup_yt']

    order_id = request.json['id']
    for order_data in db:
        if order_data['_id'] == order_id:
            return bson.BSON.encode({'doc': order_data})
    return None
