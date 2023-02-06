/* global dform, QUnit */
/* eslint no-console: 0 */
(function (q) {

    q.module('widgets.settings');

    var mock = {
        init: function () {
            // Setup
            dform.clear();
            dform.fillStateByJSON({
                'ok': 1,
                'widget_settings': {
                    'direction': 'gowork',
                    'homeGeo': '37.56322177831994,55.7667698175648',
                    'workTransit': '37.55999300000001,55.75498900000001|37.574201,55.763389000000004',
                    'homeLabel': 'ТыкТык',
                    'homeTransit': '37.585492000000016,55.769400999999995',
                    'workGeo': '37.59721080957026,55.761555664475814'
                },
                'route': {
                    'direction': 'direct',
                    'finish': {
                        'longitude': '37.59721080957026',
                        'data_key': 'work',
                        'latitude': '55.761555664475814',
                        'type': 'work',
                        'title': 'Домой',
                        'tags': {
                            'work': 1
                        }
                    },
                    'transit': {
                        'direct': [
                            {
                                'longitude': '37.55999300000001',
                                'latitude': '55.75498900000001',
                                'data_key': 'work=tiktik=0'
                            },
                            {
                                'longitude': '37.574201',
                                'latitude': '55.763389000000004',
                                'data_key': 'work=tiktik=1'
                            }
                        ],
                        'reverse': [
                            {
                                'longitude': '37.585492000000016',
                                'latitude': '55.769400999999995',
                                'data_key': 'tiktik=work=0'
                            }
                        ]
                    },
                    'start': {
                        'longitude': '37.56322177831994',
                        'data_key': 'tiktik',
                        'latitude': '55.7667698175648',
                        'title': 'На работу',
                        'tags': {
                            'home': 1
                        }
                    }
                }
            });
        },
        showDiff: function (obj1, obj2) {
            if (typeof console !== 'undefined' && console.log) {
                console.log('result: ' + JSON.stringify(obj1));
                console.log('expect: ' + JSON.stringify(obj2));
            }
            return '';
        }
    };
    // Тест на конверсию для https://wiki.yandex-team.ru/mellior/traffic-widget-settings#h-7
    q.test('b-traffic: dform.getState', function () {
        mock.init();

        q.deepEqual(
            dform.getState(),
            {
                'direction': 'direct',
                'finish': {
                    'longitude': '37.59721080957026',
                    'data_key': 'work',
                    'latitude': '55.761555664475814',
                    'type': 'work',
                    'title': 'Домой',
                    'tags': {
                        'work': 1
                    }
                },
                'transit': {
                    'direct': [
                        {
                            'longitude': '37.55999300000001',
                            'latitude': '55.75498900000001',
                            'data_key': 'work=tiktik=0'
                        },
                        {
                            'longitude': '37.574201',
                            'latitude': '55.763389000000004',
                            'data_key': 'work=tiktik=1'
                        }
                    ],
                    'reverse': [
                        {
                            'longitude': '37.585492000000016',
                            'latitude': '55.769400999999995',
                            'data_key': 'tiktik=work=0'
                        }
                    ]
                },
                'start': {
                    'longitude': '37.56322177831994',
                    'data_key': 'tiktik',
                    'latitude': '55.7667698175648',
                    'title': 'На работу',
                    'tags': {
                        'home': 1
                    }
                }
            },
            'State conversion from JSON failed'
        );
    });

    q.test('b-traffic: dform.update', function () {
        dform.clear();
        dform.update('start', {
            'longitude': '37.59721080957026',
            'address_line': 'Олонецкий проезд',
            'latitude': '55.761555664475814',
            'title': 'Дом'
        });
        var expectedObj = {
            start: {
                'longitude': '37.59721080957026',
                'address_line': 'Олонецкий проезд',
                'latitude': '55.761555664475814',
                'type': 'home',
                'title': 'Дом'
            }
        };
        //mock.showDiff(dform.getState(), expectedObj);
        q.deepEqual(
            dform.getState(),
            expectedObj,
            "dform.update: start point hasn't updated"
        );

        dform.update('finish', {
            'longitude': '37.59721080957026,', //
            'address_line': 'Льва Толстого',
            'latitude': '55.761555664475814',
            'title': 'Работа'
        });

        q.deepEqual(
            dform.getState(),
            {
                start: {
                    'longitude': '37.59721080957026',
                    'address_line': 'Олонецкий проезд',
                    'latitude': '55.761555664475814',
                    'type': 'home',
                    'title': 'Дом'
                },
                finish: {
                    'longitude': '37.59721080957026,',
                    'address_line': 'Льва Толстого',
                    'latitude': '55.761555664475814',
                    'type': 'work',
                    'title': 'Работа'
                }
            },
            "dform.update: finish point hasn't updated"
        );

        dform.update('finish', {
            'title': 'Работа не волк'
        });

        q.deepEqual(
            dform.getState(),
            {
                start: {
                    'longitude': '37.59721080957026',
                    'address_line': 'Олонецкий проезд',
                    'latitude': '55.761555664475814',
                    'type': 'home',
                    'title': 'Дом'
                },
                finish: {
                    'longitude': '37.59721080957026,',
                    'address_line': 'Льва Толстого',
                    'latitude': '55.761555664475814',
                    'title': 'Работа не волк',
                    'type': 'work',
                    'titleUpdated': true
                }
            },
            'dform.update: update point title has failed'
        );
    });

    q.test('b-traffic: check persistent state', function () {
        mock.init();
        dform.update('start', {
            'title': 'Ашан'
        });
        dform.update('finish', {
            'longitude': '37.59721080957024',
            'latitude': '55.761555664475812',
            'address_line': 'Ондатровая улица'
        });
        q.deepEqual(
            dform.getState(),
            {
                'direction': 'direct',
                'finish': {
                    'address_line': 'Ондатровая улица',
                    'longitude': '37.59721080957024',
                    'data_key': 'work',
                    'latitude': '55.761555664475812',
                    'type': 'work',
                    'title': 'Домой',
                    'tags': {
                        'work': 1
                    }
                },
                'transit': {
                    'direct': [
                        {
                            'longitude': '37.55999300000001',
                            'latitude': '55.75498900000001',
                            'data_key': 'work=tiktik=0'
                        },
                        {
                            'longitude': '37.574201',
                            'latitude': '55.763389000000004',
                            'data_key': 'work=tiktik=1'
                        }
                    ],
                    'reverse': [
                        {
                            'longitude': '37.585492000000016',
                            'latitude': '55.769400999999995',
                            'data_key': 'tiktik=work=0'
                        }
                    ]
                },
                'start': {
                    'longitude': '37.56322177831994',
                    'data_key': 'tiktik',
                    'latitude': '55.7667698175648',
                    'title': 'Ашан',
                    'titleUpdated': true,
                    'tags': {
                        'home': 1
                    }
                }
            },
            "dform doesn't keep state for unchanged data"
        );
    });

    q.test('b-traffic: get', function () {
        mock.init();

        dform.update('finish', {
            latitude: '55.761555664475812',
            longitude: '37.59721080957024'
        });
        q.deepEqual(
            dform.getCoords('finish'),
            ['55.761555664475812', '37.59721080957024'],
            "Can't get finish coordinates"
        );
        q.deepEqual(
            dform.getCoords('start'),
            ['55.7667698175648', '37.56322177831994'],
            "Can't get start coordinates"
        );
        q.deepEqual(
            dform.getCoordsTransit('direct'),
            [
                {
                    type: 'viaPoint',
                    point: ['55.75498900000001', '37.55999300000001']
                },
                {
                    type: 'viaPoint',
                    point: ['55.763389000000004', '37.574201']
                }
            ],
            'getCoordsTransit direct coordinates has failed'
        );

        q.deepEqual(
            dform.getCoordsTransit('reverse'),
            [
                {
                    type: 'viaPoint',
                    point: ['55.769400999999995', '37.585492000000016']
                }
            ],
            'getCoordsTransit reverse coordinates has failed'
        );
    });
}(QUnit));
