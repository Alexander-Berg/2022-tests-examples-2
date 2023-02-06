var common = require('./common.js');
var config = require('../config.js');
var tools = require('../tools.js');
// var http = require('http');
var util = require('util');

function test_get_notification(result) {
    var url = common.url + 'notifications/get?&token=' + common.token;

    tools.http_get(url, function(err, data) {
        if (err) {
            result(err, data);
        } else {
            var status;
            try {
                status = JSON.parse(data);
//                tools.log(status);
            } catch (e) {
                return result(e.toString(), null);
            }
            result(null, 'Data test status: ' + (typeof(status) === 'object'), status);
        }
    });
}

function test_save_notification(id, result) {
    var post_data = JSON.stringify({
        'from_place': 'work',
        'to_place': 'home',
        'days': ['mo', 'we', 'th', 'fr'],
        'from_time': '18:00',
        'to_time': '20:00',
        'jams': 6,
        'enabled': true
    });

    tools.http_post(post_data,
        common.host,
        '/notifications/save?id=' + id.toString() + '&token=' + common.token,
        function(err, data) {
            if (err) {
                result(err, data);
            } else {
                result(null, data);
            }
        });
}

function test_create_notification(result) {
    var post_data = JSON.stringify({
        'from_place': 'home',
        'to_place': 'work',
        'days': ['mo', 'tu', 'we', 'th', 'fr'],
        'from_time': '10:00',
        'to_time': '22:00',
        'jams': 6,
        'enabled': true
    });

    tools.http_post(post_data,
        common.host,
        '/notifications/save?&token=' + common.token,
        function(err, data) {
            if (err) {
                result(err, data);
            } else {
                result(null, data);
            }
        });
}

function test_delete_notification(id, result) {
    tools.http_request('',
        common.host,
        80,
        '/notifications/delete?id=' + id + '&token=' + common.token,
        'DELETE',
        'application/json',
        function(err, data) {
            if (err) {
                result(err, data);
            } else {
                result(null, 'Data: ' + data.toString().trim());
            }
        });
}

test_get_notification(common.result('Getting notification: '));
test_create_notification(function(err, id) {
    if (err) {
        tools.log('Creating notification: ERROR!', err.trim());
    } else {
        tools.log('Creating notification: OK! id is', parseInt(id));
        test_get_notification(function(error, status, notifications){
            tools.log('created:', id, 'status:', status, 'got ids', notifications);

            test_save_notification(parseInt(id), function(err, saved_id) {
                if (err) {
                    tools.log('Saving notification: ERROR!', err.trim());
                } else {
                    tools.log('Saving notification: OK! id is', parseInt(saved_id));
                    test_get_notification(function(error, status, notifications){
                        tools.log('2nd:: created:', id, 'status:', status, 'got ids', notifications);
                        test_delete_notification(parseInt(saved_id), common.result('Deleting notification'));
                    });
                }
            });
        });
    }
});
