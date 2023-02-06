'use strict';

var fs = require('fs');
var tools = require('../tools');
var subscriber = require('../subscriber');
var db = require("../db");

// db.connect().then(function () {
    // var decode_content = fs.readFileSync('./decode_test.feed');
    var decode_content = fs.readFileSync('./test111.xml');
    // var decode_content = fs.readFileSync('./news.xml');
    // var decode_content = fs.readFileSync('./news.rss.11072016');
    // var decode_content = fs.readFileSync('./news_backup.xml');

    // decode_content = decode_content.toString().replace(/\\(\d{3})/g, function (part, part2) {
    //     // return part;
    //     return '\\x' + parseInt(part2, 8).toString(16);
    // });

    // tools.logger.debug('file content:', decode_content);

    // subscriber.parseFeed('http://www.f1news.ru/export/news.xml', decode_content.toString());
    decode_content = subscriber.decode_feed(decode_content);
    // tools.logger.debug('file content:', decode_content.toString());
    // tools.logger.debug('decoded:', subscriber.decode_feed(decode_content));
// });
