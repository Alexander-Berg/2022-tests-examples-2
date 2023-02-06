#!/opt/nodejs/6/bin/node
'use strict';
const tools = require('./tools');
const feeds = require('./feeds');
const config = require('./config');
const Promise = require('bluebird');
const Logger = require('portal-node-logger');
const got = require('got');
const os = require('os');
// const db = require("./db");


function check_feed(url, error_texts) {
    try {
        if (!feeds.validate_url(url)) {
            return Promise.resolve({result: false, reason: "bad url"});
        }
        if (error_texts.indexOf("disabled in robots.txt") !== -1) {
            return Promise.resolve({result: false, reason: "disabled in robots.txt"})
        }
        return got(url)
            .then(({body}) => body)
            .then(result => {
                if (result.length < 30) {
                    return {
                        result: false,
                        reason: 'empty page'
                    };
                }
                if (result.slice(0, 200).toUpperCase().indexOf('<!DOCTYPE HTML') !== -1) {
                    return {
                        result: false,
                        reason: 'html page (doctype)'
                    };
                }
                if (result.slice(0, 200).toUpperCase().indexOf('<HTML') !== -1) {
                    return {
                        result: false,
                        reason: 'html page (<html...)'
                    };
                }
                if (result.slice(0, 200).toUpperCase().indexOf('You have an error in your SQL syntax') !== -1) {
                    return {
                        result: false,
                        reason: 'SQL Database error message'
                    };
                }
                // tools.logger.red(result.slice(0, 200));
                return {
                    result: true
                };
            })
            .catch(error => {
                if (error.statusCode >= 400) {
                    return {result: false, reason: `${error.statusCode} server status`}
                }
                if (error.code === 'ENOTFOUND') {
                    return {result: false, reason: 'DNS name not found'}
                }
                if (error.code === 'ECONNREFUSED') {
                    return {result: false, reason: 'connection refused'}
                }
                if (error.code === 'ETIMEDOUT') {
                    return {result: false, reason: 'connection timeout'}
                }
                if (error.code === 'ENETUNREACH') {
                    return {result: false, reason: 'network is unreachable'}
                }
                if (error.message === 'Redirected 10 times. Aborting.') {
                    return {result: false, reason: 'Redirected 10 times'}
                }
                else {
                    tools.logger.error(url);
                    tools.logger.error(error);
                    return {result: true};
                }
            })
    }
    catch (error) {
        tools.logger.error('failed testing url', url);
        tools.logger.error(error);
        return {result: true};
    }
}


let counter = 0;
let bad_counter = 0;


/**
 * Запускается, когда fetcher запускается как сервис
 */
function main() {
    db.connect()
        .then(function (db) {
            let res = db.collection('feeds', {slaveOk: true})
                .find({disabled: {$ne: true}, errors: {$gt: 200}}, {url: 1, errors: 1, error_texts: 1})
                .skip(300)
                .limit(100)
                // .count({errors: {$gt: 200}}, {url: 1, errors: 1, error_text: 1})
                .toArray();
            res.then((data) => {
                tools.logger.blue(`got ${data.length} feeds`);
                data.forEach(feed => {
                    // tools.logger.blue(feed.error_texts);
                    check_feed(feed.url, feed.error_texts).then(result => {
                        if (!result.result) {
                            // tools.logger.debug(feed.url, result.result, '|', result.reason);
                            // console.log(
                            //     `db.feeds.update({url: '${feed.url}'}, {$set: {disabled: true, error_texts: ['${result.reason}']}})`
                            // );

                            bad_counter++;
                            tools.logger.blue(`${bad_counter}: ${feed.url} reason: ${result.reason}`);
                            // db.collection('feeds').updateOne(
                            //     {url: feed.url},
                            //     {$set: {disabled: true, error_texts: [result.reason]}}
                            // )
                            //     .then((up) => {
                            //         tools.logger.info(`updated: ${feed.url}, reason: ${result.reason}`);
                            //     });
                        }
                        else {
                            counter++;
                            tools.logger.success(`${counter}, ${feed.url}`);
                        }
                    })
                })
            })
                .catch(error => {
                    tools.logger.error(error);
                })
        })
        .catch(error => {
            tools.logger.error('error on connecting to db', error);
            process.exit(0);
        });
}


if (require.main === module) {
    main();
}
