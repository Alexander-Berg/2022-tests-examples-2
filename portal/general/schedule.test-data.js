exports.simple = function(execView) {
    return execView('Schedule', {
        Rasp: {
            'aero': 1,
            'bus': 1,
            'el': 1,
            'list': [
                {
                    'id': 'plane',
                    'tanker_key': 'plane',
                    'url': 'https://t.rasp.yandex.ru/stations/plane?city_geo_id=213'
                },
                {
                    'id': 'train',
                    'tanker_key': 'train',
                    'url': 'https://t.rasp.yandex.ru/stations/train?city_geo_id=213'
                },
                {
                    'id': 'bus',
                    'tanker_key': 'bus',
                    'url': 'https://t.rasp.yandex.ru/stations/bus?city_geo_id=213'
                },
                {
                    'id': 'suburban',
                    'tanker_key': 'suburban',
                    'url': 'https://t.rasp.yandex.ru/suburban-directions?city_geo_id=213'
                }
            ],
            'processed': 1,
            'ship': 0,
            'show': 1,
            'train': 1
        },
        skin: {}
    });
};
