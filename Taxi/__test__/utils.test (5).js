import {
    getCallDuration,
    hasOneOf,
    convertCallToEvent,
    convertHiddenCommentToEvent,
    sortEventsByDate,
    mergeCallsWithEvents,
    mergeHiddenCommentsWithEvents,
    createView,
    prepareTask,
    createLinksForMessages,
    convertMessageToEvent,
    convertHistoryItemToEvent,
    ordersLinksIsTheSame
} from '../utils';

import {EVENT_TYPE, MESSAGE_CONTENT_TYPE} from '../consts';

const createMessageEvent = created => ({
    id: created,
    type: EVENT_TYPE.MESSAGE,
    created,
    data: {
        id: created,
        sender: {
            id: 'login',
            role: 'support'
        },
        content: [
            {
                type: MESSAGE_CONTENT_TYPE.HTML,
                text: 'text'
            }
        ],
        metadata: {
            created
        }
    }
});

describe('services/tasks/utils', () => {
    describe('getCallDuration', () => {
        test('one of arguments is undefined or null', () => {
            expect(getCallDuration(null, '2019-09-15 00:00:00')).toEqual(undefined);
            expect(getCallDuration(undefined, '2019-09-15 00:00:00')).toEqual(undefined);
            expect(getCallDuration('2019-09-15 00:00:00', null)).toEqual(undefined);
            expect(getCallDuration('2019-09-15 00:00:00', undefined)).toEqual(undefined);
        });

        test('seconds, minutes, hours length', () => {
            expect(getCallDuration('2019-09-15 00:00:00', '2019-09-15 00:00:15')).toEqual('00:15');
            expect(getCallDuration('2019-09-15 00:00:00', '2019-09-15 00:20:05')).toEqual('20:05');
            expect(getCallDuration('2019-09-15 00:00:00', '2019-09-15 05:05:05')).toEqual('5:05:05');
        });
    });

    test('hasOneOf', () => {
        const tags = ['lang_he', 'lang_tk', 'test'];

        expect(hasOneOf(tags, ['not in list'])).toBeFalsy();
        expect(hasOneOf(tags, ['lang_he'])).toBeTruthy();
        expect(hasOneOf(tags, ['lang_he', 'lang_tk'])).toBeTruthy();
        expect(hasOneOf(tags, ['lang_he', 'not_in_list'])).toBeTruthy();
    });

    test('convertCallToEvent', () => {
        const call = {
            user_id: 'user_id',
            id: 1,
            created_at: '2019-09-15 00:00:00',
            completed_at: '2019-09-15 00:01:00',
            answered_at: '2019-09-15 00:00:00',
            some_meta_data: 'some_meta_data',
            num_to: '+7977',
            status_completed: 'ok',
            direction: 'in',
            record_urls: ['1', '2']
        };
        const event = {
            id: 1,
            type: EVENT_TYPE.CALL,
            created: '2019-09-15 00:00:00',
            search: 'user_id +7977',
            data: {
                login: 'user_id',
                duration: '01:00',
                phone: '+7977',
                status: 'ok',
                direction: 'in',
                records: ['1', '2']
            }
        };

        expect(convertCallToEvent(call)).toEqual(event);
    });

    test('convertHiddenCommentToEvent', () => {
        const hiddenComment = {
            login: 'login',
            created: '2019-09-15 00:00:00',
            comment: 'comment'
        };
        const event = {
            id: 'login-2019-09-15 00:00:00-hidden-comment',
            type: EVENT_TYPE.HIDDEN_COMMENT,
            created: '2019-09-15 00:00:00',
            search: 'login comment',
            data: {
                login: 'login',
                text: 'comment',
                content: {
                    type: MESSAGE_CONTENT_TYPE.HTML,
                    text: 'comment'
                }
            }
        };

        expect(convertHiddenCommentToEvent(hiddenComment)).toEqual(event);
    });

    test('convertHistoryItemToEvent', () => {
        const historyItemDismiss = {
            login: 'login',
            created: '2019-09-15 00:00:00',
            action: 'dismiss'
        };
        const eventDismiss = {
            id: 'login-2019-09-15 00:00:00-history-item',
            type: EVENT_TYPE.ACTION,
            created: '2019-09-15 00:00:00',
            links: [],
            search: 'login',
            data: historyItemDismiss
        };

        const historyItemManualUpdateMeta = {
            login: 'login',
            created: '2019-09-15 00:00:00',
            action: 'manual_update_meta',
            meta_changes: [
                {
                    change_type: 'set',
                    field_name: 'order_id',
                    value: 123
                },
                {
                    change_type: 'set',
                    field_name: 'phone_number',
                    value: 456
                }
            ]
        };
        const eventManualUpdateMeta = {
            id: 'login-2019-09-15 00:00:00-history-item',
            type: EVENT_TYPE.ACTION,
            created: '2019-09-15 00:00:00',
            links: [],
            search: 'login',
            data: historyItemManualUpdateMeta
        };
        const taskData = {};

        expect(convertHistoryItemToEvent({item: historyItemDismiss, task: taskData})).toEqual(eventDismiss);
        expect(convertHistoryItemToEvent({item: historyItemManualUpdateMeta, task: taskData})).toEqual(eventManualUpdateMeta);
    });

    test('sortEventsByDate', () => {
        const data = {
            $view: {
                events: [
                    createMessageEvent('2019-09-17 00:00:00'),
                    createMessageEvent('2019-09-15 00:00:00'),
                    createMessageEvent('2019-09-16 00:00:00')
                ],
                other_view_param: 'other_view_param'
            },
            other_data_param: 'other_data_param'
        };
        const sortedEvents = [
            createMessageEvent('2019-09-15 00:00:00'),
            createMessageEvent('2019-09-16 00:00:00'),
            createMessageEvent('2019-09-17 00:00:00')
        ];

        const {task: result} = sortEventsByDate({task: data});

        expect(result.$view.events).toEqual(sortedEvents);
        expect(result.$view.other_view_param).toEqual(result.$view.other_view_param);
        expect(result.other_data_param).toEqual(result.other_data_param);
    });

    test('mergeCallsWithEvents', () => {
        const message = createMessageEvent('2019-09-17 00:00:00');
        const call = {
            user_id: 'user_id',
            id: 1,
            created_at: '2019-09-15 00:00:00',
            completed_at: '2019-09-15 00:01:00',
            answered_at: '2019-09-15 00:00:00',
            some_meta_data: 'some_meta_data',
            num_to: '+7977',
            status_completed: 'ok',
            direction: 'in',
            record_urls: ['1', '2']
        };
        const metaInfo = {
            calls: [call]
        };

        const original = {
            $view: {
                events: [message]
            },
            meta_info: metaInfo
        };
        const merged = {
            $view: {
                events: [message, convertCallToEvent(call)]
            },
            meta_info: metaInfo
        };

        expect(mergeCallsWithEvents({task: original}).task).toEqual(merged);
    });

    test('mergeHiddenCommentsWithEvents', () => {
        const message = createMessageEvent('2019-09-17 00:00:00');
        const hiddenComment = {
            login: 'login',
            created: '2019-09-15 00:00:00',
            comment: 'comment'
        };

        const original = {
            $view: {
                events: [message]
            },
            hidden_comments: [hiddenComment]
        };
        const merged = {
            $view: {
                events: [message, convertHiddenCommentToEvent(hiddenComment)]
            },
            hidden_comments: [hiddenComment]
        };

        expect(mergeHiddenCommentsWithEvents({task: original}).task).toEqual(merged);
    });

    test('createView', () => {
        const message = {
            id: '2019-09-17 00:00:00',
            sender: {
                id: 'login',
                role: 'support'
            },
            text: 'text',
            metadata: {
                created: '2019-09-17 00:00:00'
            }
        };
        const original = {
            chat_messages: {
                messages: [message]
            },
            tags: ['lang_he']
        };
        const withView = {
            ...original,
            $view: {
                events: [convertMessageToEvent(message)],
                languageIsRtl: true
            }
        };

        expect(createView({task: original}).task).toEqual(withView);
    });

    test('prepareTask', () => {
        const message = {
            id: '2019-09-17 00:00:00',
            sender: {
                id: 'login',
                role: 'support',
                name: 'login'
            },
            text: 'text',
            metadata: {
                created: '2019-09-17 00:00:00'
            }
        };
        const call = {
            user_id: 'user_id',
            id: 1,
            created_at: '2019-09-15 00:00:00',
            completed_at: '2019-09-15 00:01:00',
            answered_at: '2019-09-15 00:00:00',
            some_meta_data: 'some_meta_data',
            num_to: '+7977',
            status_completed: 'ok',
            direction: 'in',
            record_urls: ['1', '2']
        };
        const hiddenComment = {
            login: 'login',
            created: '2019-09-16 00:00:00',
            comment: 'comment'
        };
        const original = {
            chat_messages: {
                messages: [message]
            },
            hidden_comments: [hiddenComment],
            meta_info: {
                calls: [call]
            },
            tags: ['lang_he']
        };

        const preparedEvents = [
            convertCallToEvent(call),
            convertHiddenCommentToEvent(hiddenComment),
            convertMessageToEvent(message)
        ];

        const prepared = {
            ...original,
            $view: {
                events: preparedEvents,
                unfilteredEvents: preparedEvents,
                languageIsRtl: true
            }
        };

        expect(prepareTask({task: original})).toEqual(prepared);
    });

    describe('createLinksForMessages', () => {
        test('create links', () => {
            const messages = [
                {
                    id: '1',
                    text: 'сообщение без ссылок',
                    metadata: {
                        reply_to: [],
                        created: '2019-07-04T14:37:26+0000'
                    },
                    sender: {
                        id: 'bizarre',
                        role: 'support'
                    }
                },
                {
                    id: '2',
                    text: 'сообщение на которое ответили 2 раза',
                    metadata: {
                        reply_to: [],
                        created: '2019-07-04T14:37:26+0000'
                    },
                    sender: {
                        id: '5c3f2366254e5eb96a2b056c',
                        role: 'driver'
                    }
                },
                {
                    id: '3',
                    text: 'первый ответ на сообщение 2',
                    metadata: {
                        reply_to: ['2'],
                        created: '2019-07-04T14:37:26+0000'
                    },
                    sender: {
                        id: 'bizarre',
                        role: 'support'
                    }
                },
                {
                    id: '4',
                    text: 'второй ответ на сообщение 2',
                    metadata: {
                        reply_to: ['2'],
                        created: '2019-07-04T14:37:26+0000'
                    },
                    sender: {
                        id: 'bizarre',
                        role: 'support'
                    }
                }
            ];

            const config = {
                chatTypes: [
                    {
                        id: 'driver',
                        names: [
                            'meta_info.driver_license'
                        ],
                        default: 'driver'
                    }
                ]
            };

            const chatMeta = {
                driver_license: 'Лицензия'
            };

            expect(createLinksForMessages({task: {chat_messages: {messages}, meta_info: chatMeta, chat_type: 'driver'}, config})).toEqual({
                1: {
                    replyTo: []
                },
                2: {
                    replyTo: [],
                    repliedBy: [
                        {
                            id: '3',
                            text: 'первый ответ на сообщение 2',
                            sender: 'bizarre'
                        },
                        {
                            id: '4',
                            text: 'второй ответ на сообщение 2',
                            sender: 'bizarre'
                        }
                    ]
                },
                3: {
                    replyTo: [
                        {
                            id: '2',
                            text: 'сообщение на которое ответили 2 раза',
                            sender: 'Лицензия'
                        }
                    ]
                },
                4: {
                    replyTo: [
                        {
                            id: '2',
                            text: 'сообщение на которое ответили 2 раза',
                            sender: 'Лицензия'
                        }
                    ]
                }
            });
        });
    });

    describe('ordersLinksIsTheSame', () => {
        const LINKS_A = [
            {
                links: [
                    [
                        {
                            url: 'https://admin.eda.yandex-team.ru/couriers/3114133/edit',
                            label: '\u041a\u0443\u0440\u044c\u0435\u0440 \u0432 \u0415\u0434\u0435',
                            iframe_url: 'https://admin.eda.yandex-team.ru/couriers/3114133/edit?hide_sidebar'
                        }
                    ],
                    [
                        {
                            url:
                                'https://external-admin-proxy.taxi.yandex-team.ru/show-driver/400000306208_bf6eaf9f6a7ad1e33de5642a8d9dcb08',
                            label: '\u0412\u043e\u0434\u0438\u0442\u0435\u043b\u044c',
                            iframe_url:
                                'https://external-admin-proxy.taxi.yandex-team.ru/show-driver/iframe/400000306208_bf6eaf9f6a7ad1e33de5642a8d9dcb08?interface=lavka_couriers_other'
                        }
                    ],
                    [
                        {
                            url:
                                'https://supchat.taxi.yandex-team.ru/chat?driver_license=COURIER3DA17E6BEFEF59273DA17E6BEFEF5927',
                            label: '\u041e\u0431\u0440\u0430\u0449\u0435\u043d\u0438\u044f \u043f\u043e \u0412/\u0423'
                        }
                    ],
                    [
                        {
                            url: 'https://forms.yandex-team.ru/surveys/66871/?id=60f1438b9008ca0a73930c15',
                            label: '\u0411\u0430\u0433\u0445\u0430\u043d\u0442\u0435\u0440\u044b',
                            iframe_url: 'https://forms.yandex-team.ru/surveys/66871/?id=60f1438b9008ca0a73930c15'
                        }
                    ],
                    [
                        {
                            url: 'https://admin.eda.yandex-team.ru/couriers',
                            label: '\u041a\u0443\u0440\u044c\u0435\u0440\u044b'
                        },
                        {
                            url: 'https://admin.eda.yandex-team.ru/couriers1',
                            label: '\u041a\u0443\u0440\u044c\u0435\u0440\u044b'
                        }
                    ],
                    [
                        {
                            url: 'https://ctt.eda.yandex-team.ru/courier-totals-report',
                            label:
                                '\u0413\u0440\u0430\u0444\u0438\u043a\u0438 \u043f\u043e \u043a\u0443\u0440\u044c\u0435\u0440\u0430\u043c'
                        }
                    ],
                    [
                        {
                            url: 'https://ctt.eda.yandex-team.ru/courier-shifts',
                            label:
                                '\u041a\u0443\u0440\u044c\u0435\u0440\u044b (\u0440\u0430\u0441\u043f\u0438\u0441\u0430\u043d\u0438\u0435)'
                        }
                    ],
                    [
                        {
                            url:
                                'https://docs.google.com/forms/d/e/1FAIpQLSefsF5mylJYoHkqkGslwzjKREF1x4h8ErzZYiCZ3Yw2zhlN4A/viewform',
                            label: '\u041d\u0435\u0442 \u0422\u0421 \u0443 \u043a\u0443\u0440\u044c\u0435\u0440\u0430'
                        }
                    ],
                    [
                        {
                            url: 'https://lavka-support.daas.yandex-team.ru/podderzhka-kurerov/index.html',
                            label: '\u041b\u043e\u0433\u0438\u043a\u0430'
                        }
                    ],
                    [
                        {
                            url: 'https://forms.yandex-team.ru/surveys/63159/',
                            label:
                                '\u041a\u0426 - \u0421\u0443\u043f\u0435\u0440\u0432\u0430\u0439\u0437\u0435\u0440\u044b 2.0',
                            iframe_url: 'https://forms.yandex-team.ru/surveys/63159/'
                        }
                    ]
                ]
            }
        ];

        const LINKS_B = [
            {
                links: [
                    [
                        {
                            url: 'https://admin.eda.yandex-team.ru/couriers/3114133/edit',
                            label: '\u041a\u0443\u0440\u044c\u0435\u0440 \u0432 \u0415\u0434\u0435',
                            iframe_url: 'https://admin.eda.yandex-team.ru/couriers/3114133/edit?hide_sidebar'
                        }
                    ],
                    [
                        {
                            url:
                                'https://external-admin-proxy.taxi.yandex-team.ru/show-driver/400000306208_bf6eaf9f6a7ad1e33de5642a8d9dcb08',
                            label: '\u0412\u043e\u0434\u0438\u0442\u0435\u043b\u044c',
                            iframe_url:
                                'https://external-admin-proxy.taxi.yandex-team.ru/show-driver/iframe/400000306208_bf6eaf9f6a7ad1e33de5642a8d9dcb08?interface=lavka_couriers_other'
                        }
                    ],
                    [
                        {
                            url:
                                'https://supchat.taxi.yandex-team.ru/chat?driver_license=COURIER3DA17E6BEFEF59273DA17E6BEFEF5927',
                            label: '\u041e\u0431\u0440\u0430\u0449\u0435\u043d\u0438\u044f \u043f\u043e \u0412/\u0423'
                        }
                    ],
                    [
                        {
                            url: 'https://forms.yandex-team.ru/surveys/66871/?id=60f1438b9008ca0a73930c15',
                            label: '\u0411\u0430\u0433\u0445\u0430\u043d\u0442\u0435\u0440\u044b',
                            iframe_url: 'https://forms.yandex-team.ru/surveys/66871/?id=60f1438b9008ca0a73930c15'
                        }
                    ],
                    [
                        {
                            url: 'https://admin.eda.yandex-team.ru/couriers',
                            label: '\u041a\u0443\u0440\u044c\u0435\u0440\u044b'
                        }
                    ],
                    [
                        {
                            url: 'https://ctt.eda.yandex-team.ru/courier-totals-report',
                            label:
                                '\u0413\u0440\u0430\u0444\u0438\u043a\u0438 \u043f\u043e \u043a\u0443\u0440\u044c\u0435\u0440\u0430\u043c'
                        }
                    ],
                    [
                        {
                            url: 'https://ctt.eda.yandex-team.ru/courier-shifts',
                            label:
                                '\u041a\u0443\u0440\u044c\u0435\u0440\u044b (\u0440\u0430\u0441\u043f\u0438\u0441\u0430\u043d\u0438\u0435)'
                        }
                    ]
                ]
            }
        ];

        const LINKS_C = [
            {
                links: [
                    [
                        {
                            url: 'https://admin.eda.yandex-team.ru/couriers/3114133/edit',
                            label: '\u041a\u0443\u0440\u044c\u0435\u0440 \u0432 \u0415\u0434\u0435',
                            iframe_url: 'https://admin.eda.yandex-team.ru/couriers/3114133/edit?hide_sidebar'
                        }
                    ],
                    [
                        {
                            url:
                                'https://external-admin-proxy.taxi.yandex-team.ru/show-driver/400000306208_bf6eaf9f6a7ad1e33de5642a8d9dcb08',
                            label: '\u0412\u043e\u0434\u0438\u0442\u0435\u043b\u044c',
                            iframe_url:
                                'https://external-admin-proxy.taxi.yandex-team.ru/show-driver/iframe/400000306208_bf6eaf9f6a7ad1e33de5642a8d9dcb08?interface=lavka_couriers_other'
                        }
                    ],
                    [
                        {
                            url:
                                'https://supchat.taxi.yandex-team.ru/chat?driver_license=COURIER3DA17E6BEFEF59273DA17E6BEFEF5927',
                            label: '\u041e\u0431\u0440\u0430\u0449\u0435\u043d\u0438\u044f \u043f\u043e \u0412/\u0423'
                        }
                    ],
                    [
                        {
                            url: 'https://forms.yandex-team.ru/surveys/66871/?id=60f1438b9008ca0a73930c15',
                            label: '\u0411\u0430\u0433\u0445\u0430\u043d\u0442\u0435\u0440\u044b',
                            iframe_url: 'https://forms.yandex-team.ru/surveys/66871/?id=60f1438b9008ca0a73930c15'
                        }
                    ],
                    [
                        {
                            url: 'https://admin.eda.yandex-team.ru/couriers',
                            label: '\u041a\u0443\u0440\u044c\u0435\u0440\u044b'
                        }
                    ],
                    [
                        {
                            url: 'https://ctt.eda.yandex-team.ru/courier-totals-report',
                            label:
                                '\u0413\u0440\u0430\u0444\u0438\u043a\u0438 \u043f\u043e \u043a\u0443\u0440\u044c\u0435\u0440\u0430\u043c'
                        }
                    ],
                    [
                        {
                            url: 'https://ctt.eda.yandex-team.ru/courier-shifts',
                            label:
                                '\u041a\u0443\u0440\u044c\u0435\u0440\u044b (\u0440\u0430\u0441\u043f\u0438\u0441\u0430\u043d\u0438\u0435)'
                        }
                    ]
                ]
            },
            {
                links: [
                    [
                        {
                            url: 'https://admin.eda.yandex-team.ru/couriers/3114133/edit',
                            label: '\u041a\u0443\u0440\u044c\u0435\u0440 \u0432 \u0415\u0434\u0435',
                            iframe_url: 'https://admin.eda.yandex-team.ru/couriers/3114133/edit?hide_sidebar'
                        }
                    ]
                ]
            }
        ];

        const LINKS_D = [
            {
                default_url: '1',
                links: [
                    [
                        {
                            url: 'https://admin.eda.yandex-team.ru/couriers/3114133/edit',
                            label: '\u041a\u0443\u0440\u044c\u0435\u0440 \u0432 \u0415\u0434\u0435',
                            iframe_url: 'https://admin.eda.yandex-team.ru/couriers/3114133/edit?hide_sidebar'
                        }
                    ]
                ]
            }
        ];

        const LINKS_E = [
            {
                default_url: '2',
                links: [
                    [
                        {
                            url: 'https://admin.eda.yandex-team.ru/couriers/3114133/edit',
                            label: '\u041a\u0443\u0440\u044c\u0435\u0440 \u0432 \u0415\u0434\u0435',
                            iframe_url: 'https://admin.eda.yandex-team.ru/couriers/3114133/edit?hide_sidebar'
                        }
                    ]
                ]
            }
        ];

        test('same', () => {
            expect(ordersLinksIsTheSame(LINKS_A, LINKS_A)).toBeTruthy();
            expect(ordersLinksIsTheSame(LINKS_B, LINKS_B)).toBeTruthy();
            expect(ordersLinksIsTheSame(LINKS_C, LINKS_C)).toBeTruthy();
            expect(ordersLinksIsTheSame(LINKS_D, LINKS_D)).toBeTruthy();
            expect(ordersLinksIsTheSame(LINKS_E, LINKS_E)).toBeTruthy();
        });

        test('different', () => {
            expect(ordersLinksIsTheSame(LINKS_A, LINKS_B)).toBeFalsy();
            expect(ordersLinksIsTheSame(LINKS_A, LINKS_C)).toBeFalsy();
            expect(ordersLinksIsTheSame(LINKS_A, LINKS_D)).toBeFalsy();
            expect(ordersLinksIsTheSame(LINKS_A, LINKS_E)).toBeFalsy();

            expect(ordersLinksIsTheSame(LINKS_B, LINKS_C)).toBeFalsy();
            expect(ordersLinksIsTheSame(LINKS_B, LINKS_D)).toBeFalsy();
            expect(ordersLinksIsTheSame(LINKS_B, LINKS_E)).toBeFalsy();

            expect(ordersLinksIsTheSame(LINKS_C, LINKS_D)).toBeFalsy();
            expect(ordersLinksIsTheSame(LINKS_C, LINKS_E)).toBeFalsy();

            expect(ordersLinksIsTheSame(LINKS_D, LINKS_E)).toBeFalsy();

            expect(ordersLinksIsTheSame(LINKS_A, undefined)).toBeFalsy();
            expect(ordersLinksIsTheSame(LINKS_A, [])).toBeFalsy();
        });
    });
});
