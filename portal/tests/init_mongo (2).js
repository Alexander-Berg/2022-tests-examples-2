var config = require('../config');
var tools = require('../server/tools');
var db = require('../server/db');
var promise = require('bluebird');

db.connect(function (res){
    tools.logger.info('connected to db');
});

function get_domain(){
    return [ 'ya.ru',
    'yandex.ru',
    'narod.ru',
    'yandex.com.tr',
    'yandex.ua'][Math.round((Math.random() * 4))];
}

function get_text(){
    const lorem = '';
    var start = Math.round(Math.random() * lorem.length);
    var end = start + Math.round(Math.random() * 160);
    return lorem.slice(start, end);
}

function add_card(callback){
    var card_id = tools.gen_id();
    var card = {
        id: card_id,
        uid_from: Math.round(Math.random()*100000),
        uid_to: Math.round(Math.random()*100000),
        email_from: 'some@' + get_domain(),
        email_to: 'rcpt@' + get_domain(),
        from_name: '',
        to_name: '',
        hash: card_id,
        ip: '2a02:6b8:0:40c:5499:cc2a:12b8:7019', // - ip отправителя
        text: get_text(), // - сам мессадж
        design_id: Math.round(Math.random()*15), // - id дизайна
        event_id: 7645234465767 // - флаг праздника
    };
    db.insertCards(card).then(function(res){
            callback();
        },
        function(error){
            tools.logger.error('not inserted', error);
            callback();
        }
    );
}

var i = 0;

function add_card_cycle() {
    return add_card(function () {
        tools.logger.info('inserted', i);
        if (++i < 100000) {
            return add_card_cycle();
        }
        else {
            return db.disconnect();
        }
    });
}
setTimeout(function() {
    add_card_cycle()
}, 1000);
