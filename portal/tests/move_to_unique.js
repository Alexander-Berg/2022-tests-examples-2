'use strict';

var promise = require('bluebird');
var config = require('./../config');
var db = require("./../db");
var tools = require('./../tools');
var Logger = require('./../logger').Logger;


var logger = new Logger(null, true);

db.connect().then(function () {
    //db.feeds.group({key: {url: 1}, initial: {count: 0}, reduce: function(obj, prev) {prev.count++;}})

    //db.feeds.aggregate([ {$match: {}}, {$group: {_id: "$url", count: {$sum: 1}}}]);

    var feeds = db.get_collection();
    feeds.aggregate({$group: {_id: "$url", count: {$sum: 1}}}, function (error, result) {
        if (error) {
            logger.error('error on aggregate:', error);
        }
        else {
            logger.debug('result:', result.length);
            for (var i = 0; i < result.length; i++) {
                if (result[i].count > 1) {
                    (function (res) {
                        if (res._id) {
                            feeds.find({url: res._id}).toArray(function (error, data) {
                                if (error) {
                                    logger.error('error on aggregate:', error);
                                }
                                else {
                                    if (data && data[0] && data[0]._id) {
                                        var ids = [];
                                        for (var j = 0; j < data.length; j++) {
                                            ids.push(data[j].id);
                                        }
                                        logger.info('count:', res.count, 'url:', res._id, 'ids:', ids);
                                        feeds.update({_id: data[0]._id}, {$set: {ids: ids}}, {}, function (error, data) {
                                            if (error) {
                                                logger.error('error on updating:', error);
                                                process.exit(-1);
                                            }
                                        });
                                        //logger.debug(JSON.stringify({$and: [{url: data[0].url}, {_id: {$ne: data[0]._id}}]}));
                                        feeds.remove({$and: [{url: data[0].url}, {_id: {$ne: data[0]._id}}]}, function (error, data) {
                                            if (error) {
                                                logger.error('error on removing:', error);
                                                process.exit(-1);
                                            }
                                        });
                                    }
                                }
                            });
                        }
                    })(result[i]);
                }
            }
        }
    });
});

