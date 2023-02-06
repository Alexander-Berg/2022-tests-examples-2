var common = require('./common.js');
var config = require('../config.js');
var tools = require('../tools.js');
// var http = require('http');
var util = require('util');

function test_get_route(direction, result) {
    var url = common.url + 'route/get?to=' + direction + '&token=' + common.token;

    tools.http_get(url, function(err, data) {
        if (err) {
            result(err, data);
        } else {
            var status;
            try {
                status = check_route_fields(JSON.parse(data));
            } catch (e) {
                return result(e.toString(), null);
            }
            result(null, 'Data test status: ' + status.toString());
        }
    });
}

function check_route_fields(route) {
    if (typeof(route) !== 'object') return false;
    // tools.log(util.inspect(route.routes));
    return route.hasOwnProperty('from') &&
        route.hasOwnProperty('to') &&
        route.hasOwnProperty('information') &&
        route.hasOwnProperty('routes') &&
        // route.hasOwnProperty('name') &&
        route.information.hasOwnProperty('icon') &&
        route.information.hasOwnProperty('text') &&
        route.information.hasOwnProperty('url');
}

function test_refine_route(result) {
    var url = common.url + 'route/refine?to=home&relays=[[55.738381,37.585824],[55.738396,37.586114]]&token=' + common.token;

    tools.http_get(url, function(err, data) {
        if (err) {
            result(err, data);
        } else {
            try {
                var status = check_route_fields(JSON.parse(data));
            } catch (e) {
                return result(e.toString(), null);
            }
            result(null, 'Data length: ' + data.length.toString());
        }
    });
}

function test_save_route(id, result) {
    var post_data = JSON.stringify({
        'name': 'мой любимый маршрут',
        'from': 'home',
        'to': 'work',
        'relays': [
            [55.738381, 37.585824]
        ]
    });

    tools.http_post(post_data,
        common.host,
        '/route/save?id=' + id.toString() + '&token=' + common.token,
        'POST',
        function(err, data) {
            if (err) {
                result(err, data);
            } else {
                result(null, data);
            }
        });
}

function test_create_route(result) {
    var post_data = JSON.stringify({
        'name': 'мой любимый маршрут',
        'from': 'home',
        'to': 'work',
        'relays': [
            [55.738381, 37.585824],
            [55.738396, 37.586114]
        ]
    });

    tools.http_post(post_data,
        common.host,
        '/route/save?&token=' + common.token,
        'POST',
        function(err, data) {
            if (err) {
                result(err, data);
            } else {
                result(null, data);
            }
        });
}

function test_delete_route(id, result) {
    tools.http_post('',
        common.host,
        '/route/delete?id=' + id + '&token=' + common.token,
        'DELETE',
        function(err, data) {
            if (err) {
                result(err, data);
            } else {
                result(null, 'Data: ' + data.toString().trim());
            }
        });
}

test_get_route('home', common.result('Getting home route: '));
test_get_route('work', common.result('Getting work route: '));
test_refine_route(common.result('Refine route: '));
test_create_route(function(err, id) {
    if (err) {
        tools.log('Creating route: ERROR!', err.trim());
    } else {
        tools.log('Creating route: OK! id is', parseInt(id));
        test_save_route(parseInt(id), function(err, saved_id) {
            if (err) {
                tools.log('Saving route: ERROR!', err.trim());
            } else {
                tools.log('Saving route: OK! id is', parseInt(saved_id));
                test_delete_route(parseInt(saved_id), common.result('Deleting route'));
            }
        });
    }
});
