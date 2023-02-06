var db = require('../mongodbconnector.js');

var token_mordauser = '7d65e79f37c44f3594b342ad9d695ae6';
var token_mordauser2 = '4f0578757da54ad4b4bc2c7e2e259550';
var test_users = [3000365164, 3000368113];
var test_tokents = ['7d65e79f37c44f3594b342ad9d695ae6',
                    '4f0578757da54ad4b4bc2c7e2e259550'];
var user_login = 'mordauser';
var user_pass = '1234567890';

exports.test_user = test_users[0];
exports.token = token_mordauser;
exports.host = 'jamsonmyway.wdevx.yandex.net';
// exports.host = 'jomw.wdevx.yandex.net';
exports.url = 'http://'+exports.host+'/';
exports.tokens = test_tokents;
exports.users = test_users;

var tools = require('../tools.js');
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

exports.clean_test_data = function(){
    db.connect();
    db.deleteRouteByUid(test_users[0], function(err,data){
        db.deleteRouteByUid(test_users[1], function(err,data){
            db.deleteUser(test_users[0], function(err,data){
                db.deleteUser(test_users[1], function(err,data){
                    db.disconnect();
                });
            });
        });
    });
}