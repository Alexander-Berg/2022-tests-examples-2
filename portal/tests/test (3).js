'use strict';
const qs = require('querystring');
const util = require('util');
const Promise = require('bluebird');
const _ = require('lodash');
const got = require('got');
const common = require('./common.js');
const config = require('../config.js');
const tools = require('../server/tools.js');

function test_get_cards_uid(uid) {
    const get_url = `${common.url}/cards/uid?uid=${uid}`; //;
    return got(get_url)
        .then(({body}) => body)
        .then(data => data.toString().trim());
}

function test_get_cards_email(mail) {
    const get_url = `${common.url}/cards/mail?mail=${mail}`;
    return got(get_url)
        .then(({body}) => body)
        .then(data => data.toString().trim());
}


function test_get_card_hash(hash) {
    const get_url = `${common.url}/cards/id?id=${hash}`;
    return got(get_url)
        .then(({body}) => body)
        .then(data => {
            const card = JSON.parse(data.toString());
            try {
                if (_.isArray(card) && card[0].id == hash) {
                    return card;
                } else {
                    return Promise.reject(`bad answer - ${util.inspect(card)}`);
                }
            } catch (error) {
                return Promise.reject(`some exception: ${error}`);
            }
        });
}

function test_send_card() {
    const post_data = {
        Locale: 'be',
        design_id: 'bear',
        event_id: common.example_event,
        text: 'поздравляшки',
        to_email: 'firej@ya.ru',
        from_uid: common.test_uids[1],
        from_name: 'Пупкин Василий',
        from_email: 'fjplus@ya.ru',
        to_uid: common.test_uids[0],
        date_until: 'до 15 марта'
    };
    const options = {
        method: 'POST',
        body: qs.stringify(post_data)
    };
    return got(`${common.url}/cards/send`, options)
        .then(({body}) => body);
}

function test_view_card(hash) {
    const get_url = `${common.url}/cards/counter/header?id=${hash}`;
    return got(get_url)
        .then(({body}) => body)
        .then(data => data.toString().trim());
}

function test_popup_card(hash) {
    const get_url = `${common.url}/cards/counter/read?id=${hash}`;
    return got(get_url)
        .then(({body}) => body)
        .then(data => data.toString().trim());
}

function test_ban_card(hash) {
    const get_url = `${common.url}/card/ban/id?id=${hash}`;
    return got(get_url)
        .then(({body}) => body)
        .then(data => data.toString().trim());
}

function test_delete_card(hash) {
    tools.logger.info(`cleanup card #${hash}`);
    return got(`${common.url}/cards/id?id=${hash.toString()}`, {method: 'DELETE',})
        .then(({body}) => body);
}

const cards_hashes = [];

function test_cleanup() {
    tools.logger.info('testing done, cleanup <<<========');
    cards_hashes.forEach(test_delete_card);
}

// Само тестирование
// test_get_card(common.result('Getting cards'));
tools.logger.info('=======>>> starting testing cards');
test_send_card()
    .then(
        result => {
            tools.logger.info('[  OK  ] sending cards:', result.trim());
            const answer = JSON.parse(result);
            cards_hashes.push(answer.hash);
            // Следующие тесты
            const t1 = test_get_cards_uid(common.test_uids[0])
                .then(card => tools.logger.info('[  OK  ] fetching card by UID:', 'OK'))
                .catch(error => tools.logger.error('[ERROR!] fetching card by UID:', error));
            const t15 = test_get_cards_email('firej@ya.ru').then(
                card => {
                    tools.logger.info('[  OK  ] fetching card by mail:', 'OK');
                }, error => {
                    tools.logger.error('[ERROR!] fetching card by mail:', error);
                }
            );
            const t2 = test_view_card(answer.hash).then(
                answer => {
                    tools.logger.info('[  OK  ] view card:', answer);
                }, error => {
                    tools.logger.error('[ERROR!] view card:', error);
                }
            );
            const t3 = test_popup_card(answer.hash).then(
                answer => {
                    tools.logger.info('[  OK  ] read card:', answer);
                }, error => {
                    tools.logger.error('[ERROR!] read card:', error);
                }
            );

            const t4 = new Promise((resolve, reject) => {
                Promise.all([t2, t3]).then(() => {
                    test_get_card_hash(answer.hash).then(card => {
                        tools.logger.info('[  OK  ] fetching card by HASH:', 'OK');
                        if (card && card[0] && card[0].views > 0 && card[0].read) {
                            resolve('OK');
                        } else {
                            tools.logger.error('bad card data after increment views (', card[0].views, ') and read (', card[0].read, ')');
                            reject('bad card!');
                        }
                    });
                });
            });

            const t5 = test_ban_card(answer.hash).then(
                answer => {
                    tools.logger.info('[  OK  ] ban card:', answer);
                }, error => {
                    tools.logger.error('[ERROR!] ban card:', error);
                }
            );

            Promise.all([t1, t2, t3, t4, t15, t5]).then(res => {
                test_cleanup();
            }).catch(errors => {
                tools.logger.error('some errors in result', errors);
                test_cleanup();
            });
        }
    )
    .catch(error => tools.logger.error('[ERROR!] sending cards:', error));
