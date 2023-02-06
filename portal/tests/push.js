var common = require('./common');
var config = require('../config');
var tools = require('../tools');
var pushkin = require('../pushkin');
var util = require('util');

function test_save_push(callback){
    pushkin.send_notify(common.test_user, 'hmhmhmhm', {}, function(error, data){
        callback(error, data);
    })
}

test_save_push(function(err, answer) {
    if (err) {
        tools.log('Send push notify: ERROR!', err.trim());
    } else {
        tools.log('Send push notify: OK! answer is', answer.trim());
    }
});
