'use strict';

var zlib = require('zlib');
var mongoclient = require('mongodb').MongoClient;
var tools = require('../tools');
var config = require('../config.js');
var censor = require('../censor');
var feeds = require('../feeds');

var feed_collection;
var db_obj;
var feeds_array = [];

mongoclient.connect(config.mongo_connect_string, {}, function (error, db) {
    db_obj = db;
    feed_collection = db.collection('feeds');
    var stream = feed_collection.find({url: 'http://www.malina-mix.com/export/anekdots/widget.xml'}).stream();
    //var stream = feed_collection.find({}).stream();
    stream.on('data', function (feed) {
        feeds_array.push(feed);
        url_checker();
    });
    stream.on('end', function () {
    });
});

function close() {
    db_obj.close();
}

function url_checker() {
    var feed = feeds_array.pop();
    zlib.unzip(feed.feed.buffer, function (err, feed) {
        //tools.logger.info(feed.toString());
        censor.check_feed(feed).then(function (result) {
            tools.logger.info('results: good:', result.good, 'bad:', result.bad);
            tools.logger.warning(feeds.add_feed_info(result.feed, [
                {name: 'censored', value: result.bad}]).slice(0, 400));
        }, function (error) {
            tools.logger.error('error on check feed:', error);
        });
        close();
    });
}
