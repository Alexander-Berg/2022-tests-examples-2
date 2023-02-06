var init_auth = require('../libs/auth.js').init_auth,
    validOneUser = {
        "error": "OK",
        "status": "VALID",
        "age": 767,
        "ttl": "5",
        "raw": {
            "status": {
                "value": "VALID",
                "id": 0
            },
            "error": "OK",
            "age": 767,
            "expires_in": 7775233,
            "ttl": "5",
            "default_uid": "13458412",
            "users": [{
                "id": "13458412",
                "status": {
                    "value": "VALID",
                    "id": 0
                },
                "uid": {
                    "value": "13458412",
                    "lite": false,
                    "hosted": false
                },
                "login": "jstester",
                "regname": "jstester",
                "display_name": {
                    "name": "Display Name",
                    "avatar": {
                        "default": "21377/13458412-16067829",
                        "empty": false
                    }
                },
                "dbfields": {
                    "subscription.suid.669": ""
                },
                "attributes": {
                    "29": "m",
                    "31": "ru",
                    "34": "uk",
                    "98": "21377/13458412-16067829",
                    "1007": "Pupkin Vasily",
                    "1008": "jstester"
                },
                "address-list": [{
                    "address": "jstester@yandex.ru"
                }]
            }],
            "allow_more_users": true
        }
    },
    validOneSocial = {
        "error": "OK",
        "status": "VALID",
        "age": 1,
        "ttl": "5",
        "raw": {
            "status": {
                "value": "VALID",
                "id": 0
            },
            "error": "OK",
            "age": 1,
            "expires_in": 7775999,
            "ttl": "5",
            "session_fraud": 0,
            "default_uid": "322786201",
            "users": [{
                "id": "322786201",
                "status": {
                    "value": "VALID",
                    "id": 0
                },
                "uid": {
                    "value": "322786201",
                    "lite": false,
                    "hosted": false
                },
                "login": "",
                "regname": "uid-sbi3m6y7",
                "display_name": {
                    "name": "Вася Социальный",
                    "avatar": {
                        "default": "0/0-0",
                        "empty": true
                    },
                    "social": {
                        "profile_id": "58344836",
                        "provider": "mr",
                        "redirect_target": "1472205343.89817.58344836.df251f4f8c14134e22ffeedd77fcba51"
                    }
                },
                "dbfields": {
                    "subscription.suid.669": ""
                },
                "attributes": {
                    "29": "m",
                    "31": "ru",
                    "34": "ru",
                    "1007": "Pupkin Vasily",
                    "1008": "uid-sbi3m6y7"
                },
                "address-list": [{
                    "address": "s4mobile@fake1.yandex.ru"
                }]
            }],
            "allow_more_users": true
        }
    },
    validMultiSocUser = {
        "error": "OK",
        "status": "VALID",
        "age": 1,
        "ttl": "5",
        "raw": {
            "status": {
                "value": "VALID",
                "id": 0
            },
            "error": "OK",
            "age": 1,
            "expires_in": 7775999,
            "ttl": "5",
            "session_fraud": 0,
            "default_uid": "13458412",
            "users": [{
                "id": "322786201",
                "status": {
                    "value": "VALID",
                    "id": 0
                },
                "uid": {
                    "value": "322786201",
                    "lite": false,
                    "hosted": false
                },
                "login": "",
                "regname": "uid-sbi3m6y7",
                "display_name": {
                    "name": "Вася Социальный",
                    "avatar": {
                        "default": "0/0-0",
                        "empty": true
                    },
                    "social": {
                        "profile_id": "58344836",
                        "provider": "mr",
                        "redirect_target": "1472205671.69088.58344836.e56ca9c608ee7067c033e6dac4d7aad4"
                    }
                },
                "dbfields": {
                    "subscription.suid.669": ""
                },
                "attributes": {
                    "29": "m",
                    "31": "ru",
                    "34": "ru",
                    "1007": "Pupkin Vasily",
                    "1008": "uid-sbi3m6y7"
                },
                "address-list": [{
                    "address": "s4mobile@fake1.yandex.ru"
                }]
            }, {
                "id": "13458412",
                "status": {
                    "value": "VALID",
                    "id": 0
                },
                "uid": {
                    "value": "13458412",
                    "lite": false,
                    "hosted": false
                },
                "login": "jstester",
                "regname": "jstester",
                "display_name": {
                    "name": "Display Name",
                    "avatar": {
                        "default": "21377/13458412-16067829",
                        "empty": false
                    }
                },
                "dbfields": {
                    "subscription.suid.669": ""
                },
                "attributes": {
                    "29": "m",
                    "31": "ru",
                    "34": "uk",
                    "98": "21377/13458412-16067829",
                    "1007": "Pupkin Vasily",
                    "1008": "jstester"
                },
                "address-list": [{
                    "address": "jstester@yandex.ru"
                }]
            }],
            "allow_more_users": true
        }
    },
    staleMultiUser = {
        "error": "OK",
        "status": "VALID",
        "age": 1,
        "ttl": "5",
        "raw": {
            "status": {
                "value": "VALID",
                "id": 0
            },
            "error": "OK",
            "age": 1,
            "expires_in": 7775999,
            "ttl": "5",
            "session_fraud": 0,
            "default_uid": "322786201",
            "users": [{
                "id": "322786201",
                "status": {
                    "value": "INVALID",
                    "id": 0
                }
            }, {
                "id": "13458412",
                "status": {
                    "value": "VALID",
                    "id": 0
                },
                "uid": {
                    "value": "13458412",
                    "lite": false,
                    "hosted": false
                },
                "login": "jstester",
                "regname": "jstester",
                "display_name": {
                    "name": "Display Name",
                    "avatar": {
                        "default": "21377/13458412-16067829",
                        "empty": false
                    }
                },
                "dbfields": {
                    "subscription.suid.669": ""
                },
                "attributes": {
                    "29": "m",
                    "31": "ru",
                    "34": "uk",
                    "98": "21377/13458412-16067829",
                    "1007": "Pupkin Vasily",
                    "1008": "jstester"
                },
                "address-list": [{
                    "address": "jstester@yandex.ru"
                }]
            }],
            "allow_more_users": true
        }
    },
    childOneUser = {
        "error": "OK",
        "status": "VALID",
        "age": 767,
        "ttl": "5",
        "raw": {
            "status": {
                "value": "VALID",
                "id": 0
            },
            "error": "OK",
            "age": 767,
            "expires_in": 7775233,
            "ttl": "5",
            "default_uid": "13458412",
            "users": [{
                "id": "13458412",
                "status": {
                    "value": "VALID",
                    "id": 0
                },
                "uid": {
                    "value": "13458412",
                    "lite": false,
                    "hosted": false
                },
                "login": "child",
                "regname": "child",
                "display_name": {
                    "name": "Child Account",
                    "avatar": {
                        "default": "21377/13458412-16067829",
                        "empty": false
                    }
                },
                "dbfields": {
                    "subscription.suid.669": ""
                },
                "attributes": {
                    "29": "m",
                    "31": "ru",
                    "34": "uk",
                    "98": "21377/13458412-16067829",
                    "1007": "Pupkin Vasily",
                    "1008": "child",
                    "210": "1"
                },
                "address-list": [{
                    "address": "jstester@yandex.ru"
                }]
            }],
            "allow_more_users": true
        }
    };

describe('auth_init', function() {
    var req;
    beforeEach(() => {
        req = {
            yandexuid: 'testyandexuid',
            logger: {
                warn: function noop() {
                },
                error: function noop() {
                }
            }
        };
    });

    it('корректно обрабатывает ошибку blackbox', function() {
        req.blackbox = {
            status: {
                value: "INVALID",
                id: 5
            },
            error: "signature has bad format or is broken",
            session_fraud: 0
        };
        init_auth(req).should.deep.equal({
            yuid: req.yandexuid,
            auth: false
        });
    });

    it('возвращает информацию об обычном пользователе', function() {
        req.blackbox = validOneUser;
        init_auth(req).should.deep.equal({
            auth: true,
            yuid: req.yandexuid,
            default_uid: '13458412',
            allow_more_users: true,
            users: [{
                auth: true,
                uid: '13458412',
                login: 'jstester',
                displayName: 'Display Name',
                isChildAccount: false,
                avatar: {
                    'default': '21377/13458412-16067829',
                    empty: false
                },
                staff: false,
                address: 'jstester@yandex.ru'
            }],
            current: {
                auth: true,
                uid: '13458412',
                login: 'jstester',
                displayName: 'Display Name',
                isChildAccount: false,
                avatar: {
                    'default': '21377/13458412-16067829',
                    empty: false
                },
                staff: false,
                address: 'jstester@yandex.ru'
            }
        });
    });

    it('возвращает информацию о социальном пользователе', function() {
        req.blackbox = validOneSocial;
        init_auth(req).should.deep.equal({
            auth: true,
            yuid: req.yandexuid,
            default_uid: '322786201',
            allow_more_users: true,
            users: [{
                auth: true,
                uid: '322786201',
                login: '',
                displayName: 'Вася Социальный',
                isChildAccount: false,
                avatar: {
                    'default': '0/0-0',
                    'empty': true
                },
                staff: false,
                address: 's4mobile@fake1.yandex.ru'
            }],
            current: {
                auth: true,
                uid: '322786201',
                login: '',
                displayName: 'Вася Социальный',
                isChildAccount: false,
                avatar: {
                    'default': '0/0-0',
                    'empty': true
                },
                staff: false,
                address: 's4mobile@fake1.yandex.ru'
            }
        });
    });

    it('возвращает информацию о мультиавторизованном обычном + социальном пользователе', function() {
        req.blackbox = validMultiSocUser;
        init_auth(req).should.deep.equal({
            auth: true,
            yuid: req.yandexuid,
            default_uid: '13458412',
            allow_more_users: true,
            users: [{
                auth: true,
                uid: '322786201',
                login: '',
                displayName: 'Вася Социальный',
                isChildAccount: false,
                avatar: {
                    'default': '0/0-0',
                    'empty': true
                },
                staff: false,
                address: 's4mobile@fake1.yandex.ru'
            }, {
                auth: true,
                uid: '13458412',
                login: 'jstester',
                displayName: 'Display Name',
                isChildAccount: false,
                avatar: {
                    'default': '21377/13458412-16067829',
                    empty: false
                },
                staff: false,
                address: 'jstester@yandex.ru'
            }],
            current: {
                auth: true,
                uid: '13458412',
                login: 'jstester',
                displayName: 'Display Name',
                isChildAccount: false,
                avatar: {
                    'default': '21377/13458412-16067829',
                    empty: false
                },
                staff: false,
                address: 'jstester@yandex.ru'
            }
        });
    });

    it('возвращает информацию с протухшим мультиавторизованном пользователем', function() {
        req.blackbox = staleMultiUser;
        init_auth(req).should.deep.equal({
            auth: false,
            yuid: req.yandexuid,
            default_uid: '322786201',
            allow_more_users: true,
            users: [{
                auth: true,
                uid: '13458412',
                login: 'jstester',
                displayName: 'Display Name',
                isChildAccount: false,
                avatar: {
                    'default': '21377/13458412-16067829',
                    empty: false
                },
                staff: false,
                address: 'jstester@yandex.ru'
            }],
            current: {
                auth: false
            }
        });
    });

    it('возвращает информацию о пользователе с детским аккаунтом', function() {
        req.blackbox = childOneUser;
        init_auth(req).should.deep.equal({
            auth: true,
            yuid: req.yandexuid,
            default_uid: '13458412',
            allow_more_users: true,
            users: [{
                auth: true,
                uid: '13458412',
                login: 'child',
                displayName: 'Child Account',
                isChildAccount: true,
                avatar: {
                    'default': '21377/13458412-16067829',
                    empty: false
                },
                staff: false,
                address: 'jstester@yandex.ru'
            }],
            current: {
                auth: true,
                uid: '13458412',
                login: 'child',
                displayName: 'Child Account',
                isChildAccount: true,
                avatar: {
                    'default': '21377/13458412-16067829',
                    empty: false
                },
                staff: false,
                address: 'jstester@yandex.ru'
            }
        });
    });

});
