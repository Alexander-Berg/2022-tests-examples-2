var common = require('./common');
var config = require('../config');
var tools = require('../tools');
var http = require('http');
var querystring = require('querystring');
var util = require('util');
var passport = require('../passport');

/**
 * Тестируем сохранение адресов в паспорт
 * Алгоритм такой (тестовый юзер mordauser2):
 *     1) читаем адреса, запоминаем
 *     2) пишем левые адреса
 *     3) проверяем напрямую из паспорта - что туда записалось
 *     4) записываем обратно запомненное
 */

var addresses = '';
var src_data = '{"work":"Москва, улица Льва Толстого, 16","home":"Москва, Сумской проезд, 12к1"}';

function test_get(result) {
    auth_url = common.url + 'addresses/get?token=' + common.tokens[1];

    // Set up the request
    http.get(auth_url, function(res) {
        if (res.statusCode == 200) {
            var recv_buffer = '';
            res.on('data', function(data) {
                recv_buffer += data;
            });
            res.on('end', function() {
                var data = recv_buffer.trim();
                addresses = data;
                result(null, data);
            });
        } else {
            result('Some http error:' + res.statusCode.toString().trim(), null);
        }
    }).on('error', function(e) {
        result(e.message, null);
    });
}

function test_save(result) {
    var post_data = '';

    tools.http_post(post_data,
        common.host,
        '/addresses/save?token=' + common.tokens[1] + '&type=work&address=Москва+Варшавское+Шоссе+125+ст18',
        // '/addresses/save?token=' + common.tokens[0] + '&type=work&address=Москва+Варшавское+Шоссе+125',
        'POST',
        function(err, data) {
            if (err) {
                result(err, data);
            } else {
                result(null, 'Data: ' + data.toString().trim());
            }
        });
}

function test_check(result) {
    var post_data = querystring.stringify({
        method: 'userinfo',
        format: 'json',
        getlocation: 'postal',
        userip: '0.0.0.0',
        uid: common.users[1]
    });

    var post_options = {
        host: 'pass-test.yandex.ru',
        port: '80',
        path: '/blackbox',
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': post_data.length
        }
    };

    // Set up the request
    var post_req = http.request(post_options, function(res) {
        res.setEncoding('utf8');

        // TODO: потенциально опасное место, пожалуй надо переписать
        res.on('data', function(chunk) {
            var res;
            try {
                res = JSON.parse(chunk);
            } catch (err) {
                callback(err, null);
            }
            if (res && res.users[0] && res.users[0].locations && res.users[0].locations.postal[0]) {
                var addresses = JSON.parse(res.users[0].locations.postal[0]).addresses;
                if (!addresses) {
                    return callback(null, []);
                }
                var parsed = [];

                function __get_coordinates(address_text, index) {
                    maps.getCoordinates(address_text, function(err, points) {
                        parsed[index].readable_address = points[0].text;
                        parsed[index].coordinates = points[0].coordinates;
                        for (var i in addresses) {
                            if (!parsed[i] || !parsed[i].coordinates)
                                return;
                        }
                    });
                }
                for (var ind in addresses) {
                    var addr = addresses[ind];
                    var address_text = addr.city + ' ' + addr.street + ' ' + addr.building + ((addr.suite === '') ? '' : (' к' + addr.suite));
                    parsed.push({
                        id: addr.id,
                        title: addr.title,
                        city: addr.city,
                        street: addr.street,
                        building: addr.building,
                        suite: addr.suite,
                        readable_address: address_text
                    });
                }
                result(null, parsed);
            } else {
                callback(null, []);
            }
        });
    });

    // post the data
    post_req.write(post_data);
    post_req.end();
}

function test_back(result) {

    var source_json = {
        addresses: [{
            'phone-extra': '',
            street: 'Сумской проезд',
            suite: '1',
            floor: '',
            email: '',
            fathersname: '',
            city: 'Москва',
            id: '138626314825465',
            intercom: '',
            country: 'Россия',
            recipient: 'mordauser2 mordauser2',
            entrance: '',
            phone: '',
            zip: '',
            comment: '',
            building: '12',
            title: 'Дом',
            flat: ''
        }, {
            street: 'Льва Толстого',
            'phone-extra': '',
            floor: '',
            suite: '',
            email: '',
            fathersname: '',
            city: 'Москва',
            id: '138626326389169',
            intercom: '',
            country: 'Россия',
            recipient: 'mordauser2 mordauser2',
            entrance: '',
            phone: '',
            zip: '',
            comment: '',
            building: '16',
            title: 'Work',
            flat: ''
        }]
    };


    var post_data = querystring.stringify({
        userip: '0.0.0.0',
        access_token: common.tokens[1],
        mode: 'location',
        type: 'postal',
        text: JSON.stringify(source_json)
    });

    var post_options = {
        host: config.passport_host,
        port: '80',
        path: '/passport?mode=location',
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': post_data.length
        }
    };

    // Set up the request
    var post_req = http.request(post_options, function(res) {
        res.setEncoding('utf8');
        res.on('data', function(chunk) {
            tools.log('in save: ', chunk);
        });
        res.on('end', function() {
            result(null, 'OK');
        });
    });

    // post the data
    post_req.write(post_data);
    post_req.end();
}


test_get(function(error, data) {
    if (error) {
        tools.log('Ошибка при получении адреса:', error);
    } else {
        tools.log('Получение адреса: OK!', data);
        test_save(function(error, data) {
            if (error) {
                tools.log('Ошибка при записи адреса', error);
            } else {
                tools.log('Сохранение адреса: OK! Полсекунды до следующего теста');
                setTimeout(function() {
                    test_check(function(error, data) {
                        if (error) {
                            tools.log('Ошибка при проверке результата записи', error);
                        } else {
                            tools.log('Проверка адреса: OK!', util.inspect(data));
                            test_back(function(error, data) {
                                if (error) {
                                    tools.log('Ошибка при откате изменений', error);
                                } else {
                                    tools.log('Тесты прошли, изменения откатили');
                                }
                            });
                        }
                    });
                }, 500);
            }
        });
    }
});