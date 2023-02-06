import offersYD_new as yd

source_chili = {
    "platform_station": {
        "platform_id": "b8c60a35-9b5b-452b-a1cc-f437c9482f32"  # ПВЗ в чили
    }
}
destination_chili = {
    "type": 2,
    "custom_location": {
        "details": {
            "full_address": "Чили, коммуна Сантьяго, проспект Либертадор Бернардо О Игхинс, 2004"
        }
    },
    "interval": {
        "from": yd.TimeInFuture,
        "to": yd.TimeInFuture + 86400 * 4
    }
}

yd.PAYLOAD['destination'] = destination_chili
yd.PAYLOAD['source'] = source_chili
yd.PAYLOAD['last_mile_policy'] = 0
yd.AUTHORIZATION = 'hotpaper'

yd.makeOrder()


