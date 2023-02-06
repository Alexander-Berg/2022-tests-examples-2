var tools = require('../server/tools');

exports.host = 'postcards-dev.wdevx.yandex.net';
exports.url = 'http://postcards-dev.wdevx.yandex.net';

exports.test_uids = [3000365164, 3000368113];

exports.example_event = 'ny2019'; // Тестовый праздник - новый год

exports.result = function result(module, err, res){
    return function result(err, res){
        if (err === null){
            tools.logger.info(module, ': OK!', res);
        }
        else{
            tools.logger.error(module, ': ERROR!', err);
        }
    };
};