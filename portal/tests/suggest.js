var common = require('./common.js');
var config = require('../config.js');
var tools = require('../tools.js');
var http = require('http');
var util = require('util');

function test_suggest(result){
    var suggest_url = common.url + 'suggest/get?token=' + common.token + '&data=%D0%9B%D1%8C%D0%B2%D0%B0+%D0%A2%D0%BE%D0%BB%D1%81%D1%82%D0%BE%D0%B3%D0%BE+16';

    tools.http_get(suggest_url, function(err, data) {
        if (err) {
            result(err, data);
        } else {
            try {
                var status = JSON.parse(data);
            } catch (e) {
                return result(e.toString(), null);
            }
            result(null, 'Data length: ' + data.length.toString());
        }
    });
}

function test_bad_suggest_with_coordinates(result){
    var suggest_url = common.url + 'suggest/get_coordinates?token=' + common.token + '&data=%D0%9B%D1%8C%D0%B2%D0%B0+%D0%A2%D0%BE%D0%BB%D1%81%D1%82%D0%BE%D0%B3%D0%BE+16';

    tools.http_get(suggest_url, function(err, data, statusCode) {
        if (err) {
            if (statusCode === 406){
                result(null, 'Erorr 406 - is expected');
            }
            else{
                result(err, data);
            }
        } else {
            try {
                var status = JSON.parse(data);
            } catch (e) {
                return result(e.toString(), null);
            }
            result('we got data, but error 406 is expected', 'Data: ' + data.toString().trim());
        }
    });
}

function test_suggest_with_coordinates(result){
    var suggest_url = common.url + 'suggest/get_coordinates?token=' + common.token + '&data=%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%2C+%D0%9B%D1%8C%D0%B2%D0%B0+%D0%A2%D0%BE%D0%BB%D1%81%D1%82%D0%BE%D0%B3%D0%BE+16';
    tools.http_get(suggest_url, function(err, data) {
        if (err) {
            result(err, data);
        } else {
            try {
                var status = JSON.parse(data);
            } catch (e) {
                return result(e.toString(), null);
            }
            result(null, 'Data: ' + data.toString().trim());
        }
    });
}

function test_reverse_suggest(result){
    var suggest_url = common.url + 'suggest/get_address?token=' + common.token + '&coordinates=[55.733771,37.587937]';

    tools.http_get(suggest_url, function(err, data) {
        if (err) {
            result(err, data);
        } else {
            try {
                var status = JSON.parse(data);
            } catch (e) {
                return result(e.toString(), null);
            }
            result(null, 'Data length: ' + data.length.toString());
        }
    });
}

test_suggest(common.result('Simple suggest: '));
test_reverse_suggest(common.result('Reverse suggest: '));
test_suggest_with_coordinates(common.result('Suggest with coordinates: '));
test_bad_suggest_with_coordinates(common.result('Bad suggest: '));