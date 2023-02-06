var common = require('./common.js');
var config = require('../config.js');
var tools = require('../tools.js');

var promise = require('promise');

tools.log_init(true);

function test_get_cards_uid(uid) {
    return new promise(function (resolve, reject) {
        var get_url = common.url + '/cards/uid?uid=' + uid; //;
        tools.http_get(get_url, function (error, data) {
            if (error) {
                reject(error);
            } else {
                resolve(data.toString().trim());
            }
        });
    });
}

function test_get_cards_email(mail) {
    return new promise(function (resolve, reject) {
        var get_url = common.url + '/cards/mail?mail=' + mail;
        tools.http_get(get_url, function (error, data) {
            if (error) {
                reject(error);
            } else {
                resolve(data.toString().trim());
            }
        });
    });
}


function test_get_card_hash(hash) {
    return new promise(function (resolve, reject) {
        var get_url = common.url + '/cards/id?id=' + hash;
        tools.http_get(get_url, function (error, data) {
            if (error) {
                reject(error);
            } else {
                var card = JSON.parse(data.toString());
                try {
                    if (typeof(card) === 'object' &&
                        card.id == hash) {
                        resolve(card);
                    }
                    else {
                        reject('bad answer - ' + card.toString());
                    }
                }
                catch (error) {
                    reject('some exception: ' + error);
                }
            }
        });
    });
}

function test_send_card() {
    return new promise(function (resolve, reject) {
        var post_data = {
            design_id: 0,
            event_id: common.example_event,
            text: 'поздравляшки',
            to_email: 'firej@ya.ru',
            from_uid: common.test_uids[1],
            from_email: 'fjplus@ya.ru',
            to_uid: common.test_uids[0]
        };
        tools.http_post(JSON.stringify(post_data),
            common.host,
            '/cards/send',
            tools.callback_to_promise(resolve, reject)
        );
    });
}

function test_view_card(hash) {
    return new promise(function (resolve, reject) {
        var get_url = common.url + '/cards/counter/header?id=' + hash;
        tools.http_get(get_url, function (error, data) {
            if (error) {
                reject(error);
            } else {
                resolve(data.toString().trim());
            }
        });
    });
}

function test_popup_card(hash) {
    return new promise(function (resolve, reject) {
        var get_url = common.url + '/cards/counter/read?id=' + hash;
        tools.http_get(get_url, function (error, data) {
            if (error) {
                reject(error);
            } else {
                resolve(data.toString().trim());
            }
        });
    });
}

function test_ban_card(hash){
    return new promise(function (resolve, reject) {
        var get_url = common.url + '/card/ban/id?id=' + hash;
        tools.http_get(get_url, function (error, data) {
            if (error) {
                reject(error);
            } else {
                resolve(data.toString().trim());
            }
        });
    });
}

function test_delete_card(hash) {
    return new promise(function (resolve, reject) {
        tools.log('cleanup card #' + hash);
//        tools.http_request('',
//            common.host,
//            80,
//            '/cards/id?id=' + hash.toString(),
//            'DELETE',
//            '',
//            tools.callback_to_promise(resolve, reject)
//        );
        resolve()
    });
}

var cards_hashes = [];
function test_cleanup() {
    tools.log('testing done, cleanup <<<========');
    cards_hashes.forEach(test_delete_card);
}

// Само тестирование
// test_get_card(common.result('Getting cards'));
tools.log('=======>>> starting testing cards');
test_send_card().catch(
    function (error) {
        tools.log('[ERROR!] sending cards:', error);
    }
).then(
    function (result) {
        tools.log('[  OK  ] sending cards:', result.trim());
        var answer = JSON.parse(result);
        cards_hashes.push(answer.hash);
        // Следующие тесты
        var t1 = test_get_cards_uid(common.test_uids[0]).then(
            function (card) {
                tools.log('[  OK  ] fetching card by UID:', 'OK');
            }, function (error) {
                tools.log('[ERROR!] fetching card by UID:', error);
            }
        );
        var t15 = test_get_cards_email('firej@ya.ru').then(
            function (card) {
                tools.log('[  OK  ] fetching card by mail:', 'OK');
            }, function (error) {
                tools.log('[ERROR!] fetching card by mail:', error);
            }
        );
        var t2 = test_view_card(answer.hash).then(
            function (answer) {
                tools.log('[  OK  ] view card:', answer);
            }, function (error) {
                tools.log('[ERROR!] view card:', error);
            }
        );
        var t3 = test_popup_card(answer.hash).then(
            function (answer) {
                tools.log('[  OK  ] read card:', answer);
            }, function (error) {
                tools.log('[ERROR!] read card:', error);
            }
        );

        var t4 = new promise(function(resolve, reject){
            promise.all([t2, t3]).then(function(){
                test_get_card_hash(answer.hash).then(function(card){
                    tools.log('[  OK  ] fetching card by HASH:', 'OK');
                    if (card.views > 0 && card.read) {
                        resolve('OK');
                    }
                    else {
                        tools.log('bad card data after increment views (', card.views, ') and read (', card.read, ')' );
                        reject('bad card!');
                    }
                });
            });
        });

        var t5 = test_ban_card(answer.hash).then(
            function (answer) {
                tools.log('[  OK  ] ban card:', answer);
            }, function (error) {
                tools.log('[ERROR!] ban card:', error);
            }
        );

        promise.all([t1, t2, t3, t4, t15, t5]).then(function (res) {
            test_cleanup();
        }, function(errors){
            tools.log('some errors in result', errors);
            test_cleanup();
        });
    }
);

//test_get_card_uid().then(function (result) {
//    tools.log('testing getting cards success:', result);
//}, function (error) {
//    tools.log('testing getting cards error:', error);
//});