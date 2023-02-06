var tools = require('../tools');

exports.host = 'postcards.wdevx.yandex.net';
exports.url = 'http://postcards.wdevx.yandex.net';

exports.test_uids = [3000365164, 3000368113];

exports.example_event = 140958863406241; // Тестовый праздник - новый год

exports.result = function result(module, err, res){
    return function result(err, res){
        if (err === null){
            tools.log(module, ': OK!', res);
        }
        else{
            tools.log(module, ': ERROR!', err);
        }
    };
};