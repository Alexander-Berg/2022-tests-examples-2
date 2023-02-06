var common = require('./common.js');
var config = require('../config.js');
var tools = require('../tools.js');
var http = require('http');

function test_get(result){
    var auth_url = common.url + 'addresses/get?token=' + common.token;

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
            result('Some http error:' + res.statusCode.toString().trim(), null);
        }
    }).on('error', function(e) {
        result(e.message, null);
    });
}

function test_save(result){
    var post_data = '';

    tools.http_post(post_data,
        common.host,
        '/addresses/save?token=' + common.token + '&type=home&name=Дом&address=Москва+9-й+проезд+Марьиной+Рощи,+6а',
        function(err, data){
            if(err){
                result(err, data);
            }
            else{
                result(null, 'Data length: ' + data.toString().trim().length);
            }
        });
}


function address_reset(){
    tools.http_post('',
        common.host,
        '/addresses/save?token=' + common.token + '&type=home&name=Дом&address=Москва+Сумской+Проезд,+12к1',
        function(err, data){
            if(err){
                //(err, data);
            }
            else{
                //result(null, 'Data length: ' + data.toString().trim().length);
            }
        });
}


function test_save_fail(result){
    var post_data = '';

    tools.http_post(post_data,
        common.host,
        '/addresses/save?token=' + common.token + '&type=work&name=Работа&address=Подольск+Улица+Мира+55',
        function(err, data, statusCode) {
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

test_get(common.result('Getting address: '));
test_save(function(error, data){
    tools.log(error, data);
    test_get(common.result('Getting address: '));
});
//test_save_fail(common.result('Saving address: '));

setTimeout(address_reset, 3000);