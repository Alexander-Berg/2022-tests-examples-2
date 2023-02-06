'use strict';

var tools = require('../tools');
var config = require('../config.js');
var mongoclient = require('mongodb').MongoClient;


var peedster_url = "http://peedster.feeds.yandex.net/get?fields=rssLink&id={0}";

var finder = /<rssLink>(.*)<\/rssLink>/;


var ids = [];
var read_finished = false;
var write_finished = false;
var feed_collection;
var db_obj;

mongoclient.connect(config.mongo.connect_string, {}, function (error, db) {
    db_obj = db;
    feed_collection = db.collection('feeds');
    // var stream = feed_collection.find({"url": {$exists: false}}).stream();
    var stream = feed_collection.find({}).stream();
    stream.on('data', function (feed) {
        if (feed.url) {
            return;
        }
        if (feed.ids) {
            ids.push(feed.ids[0]);
        }
        else if (feed.id) {
            ids.push(feed.id);
        }
    });
    stream.on('end', function () {
        read_finished = true;
    });
});

function maybe_close() {
    if (read_finished && write_finished) {
        setTimeout(function () {
            db_obj.close();
        }, 1500);
    }
}

function url_finder() {
    if (ids.length > 0) {
        var feed_id = ids.pop();
        var url = tools.format(peedster_url, feed_id);
        tools.http_get(url).then(function (data) {
            var feed_url = finder.exec(data.toString())[1];
            tools.logger.info('updating for', feed_url, 'id:', feed_id);
            try {
                feed_collection.updateMany({ids: {$elemMatch: {$eq: feed_id}}}, {$set: {url: feed_url}}, function (error, data) {
                    if (!error) {
                        tools.logger.success('update ok', data && data.result && data.result.ok);
                    }
                    else {
                        tools.logger.error('update failed', error);
                    }
                });
            }
            catch (error) {
                tools.logger.error(error);
            }
        });
        setTimeout(url_finder, 50);
    }
    else {
        if (read_finished) {
            write_finished = true;
            maybe_close();
        }
        else {
            setTimeout(url_finder, 50);
        }
    }
}

url_finder();
