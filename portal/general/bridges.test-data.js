const data = {
    'bridges': {
        '0': [
            {
                'bridge_id': 'bridges.bridgeName.blagoveschensky',
                'bridge_lower1': '2:45',
                'bridge_lower2': '5:00',
                'bridge_name': 'Благовещенский',
                'bridge_raise1': '1:25',
                'bridge_raise2': '3:10',
                'from': '2019-04-23',
                'geo': '2',
                'n': 2,
                'till': '2029-11-01'
            },
            {
                'bridge_id': 'bridges.bridgeName.nevskogo',
                'bridge_lower1': '5:10',
                'bridge_name': 'А. Невского',
                'bridge_raise1': '2:20',
                'from': '2019-04-23',
                'geo': '2',
                'n': 7,
                'till': '2029-11-01'
            },
            {
                'bridge_id': 'bridges.bridgeName.volodarskiy',
                'bridge_lower1': '3:45',
                'bridge_name': 'Володарский',
                'bridge_raise1': '2:00',
                'from': '2019-04-23',
                'geo': '2',
                'n': 8,
                'till': '2029-11-01'
            }
        ],
        '1': [
            {
                'bridge_id': 'bridges.bridgeName.birzhevoy',
                'bridge_lower1': '4:55',
                'bridge_name': 'Биржевой',
                'bridge_raise1': '2:00',
                'from': '2019-04-23',
                'geo': '2',
                'n': 0,
                'till': '2029-11-01'
            },
            {
                'bridge_id': 'bridges.bridgeName.dvortsoviy',
                'bridge_lower1': '2:50',
                'bridge_lower2': '4:55',
                'bridge_name': 'Дворцовый',
                'bridge_raise1': '1:10',
                'bridge_raise2': '3:10',
                'from': '2019-04-23',
                'geo': '2',
                'n': 1,
                'till': '2029-11-01'
            },
            {
                'bridge_id': 'bridges.bridgeName.tuchkov',
                'bridge_lower1': '4:55',
                'bridge_name': 'Тучков',
                'bridge_raise1': '3:35',
                'from': '2019-04-23',
                'geo': '2',
                'n': 3,
                'till': '2029-11-01'
            },
            {
                'bridge_id': 'bridges.bridgeName.troitskiy',
                'bridge_lower1': '4:50',
                'bridge_name': 'Троицкий',
                'bridge_raise1': '1:20',
                'from': '2019-04-23',
                'geo': '2',
                'n': 4,
                'till': '2029-12-01'
            },
            {
                'bridge_id': 'bridges.bridgeName.liteinyi',
                'bridge_lower1': '4:45',
                'bridge_name': 'Литейный',
                'bridge_raise1': '1:40',
                'from': '2019-04-23',
                'geo': '2',
                'n': 5,
                'till': '2029-11-01'
            },
            {
                'bridge_id': 'bridges.bridgeName.bolsheohtinskiy',
                'bridge_lower1': '5:00',
                'bridge_name': 'Большеохтинский',
                'bridge_raise1': '2:00',
                'from': '2019-04-23',
                'geo': '2',
                'n': 6,
                'till': '2029-11-01'
            }
        ],
        'collapse': 1,
        'dayMode': 1,
        'processed': 1,
        'show': 1
    },
    Local: {
        hour: 20,
        min: 20
    },
    cookie_set_gif: '/empty?'
};

exports.collapsed = execView => execView('Bridges', data);

exports.expanded = execView => execView('Bridges', {...data, bridges: {...data.bridges, collapse: 0}});

exports.alert = execView => execView('Bridges', {
    bridges: {
        show: 1,
        alert: 'Мосты-мосты'
    }
});
