'use strict';
const qs = require('querystring');
const util = require('util');
const Promise = require('bluebird');
const _ = require('lodash');
const common = require('./common.js');
const config = require('../config.js');
const tools = require('../server/tools.js');


function test_send_card() {
    const post_data = {
        Locale: 'be',
        design_id: 'box',
        event_id: common.example_event,
        text: 'поздравляшки',
        to_email: 'firej@ya.ru',
        from_uid: common.test_uids[1],
        from_name: 'Пупкин Василий',
        from_email: 'fjplus@ya.ru',
        to_uid: common.test_uids[0],
        date_until: 'До такой-то даты'
    };
    return tools.http_post(qs.stringify(post_data), common.host, '/cards/send')
}

tools.logger.info('=======>>> starting testing cards');
test_send_card()
    .catch(error => {
            tools.logger.error('[ERROR!] sending cards:', error);
        }
    )
    .then(result => {
            tools.logger.info('[  OK  ] sending cards:', result.trim());
        }
    );
