var common = require('./common.js');
var config = require('../config.js');
var tools = require('../tools.js');
var http = require('http');

function test_auth(result){
    auth_url = common.url + 'auth?token=' + common.token;

    // Set up the request
    http.get(auth_url, function(res) {
        if (res.statusCode == 200){
            var recv_buffer = '';
            res.on('data', function(data){
                recv_buffer += data;
            });
            res.on('end', function() {
                result(null, recv_buffer.trim());
            });
        }
        else{
            result('Some http error:' + res.statusCode.toString(), null);
        }
    }).on('error', function(e) {
        result(e.message, null);
    });
}

test_auth(common.result('Authentication'));