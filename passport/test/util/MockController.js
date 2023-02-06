var express = require('express');
var FakeExpressRequest = function() {
    this.headers = {};
};
FakeExpressRequest.prototype = express.request;

var FakeExpressResponse = function() {};
FakeExpressResponse.prototype = express.response;

module.exports = require('inherit')(require('../../controller/Controller'), {
    __constructor: function() {
        this.__base(
            this.__self.getReq(),
            this.__self.getRes(),
            'ooPhoogaithoog5aid1Aiw3uop3jitho'
        );
    }
}, {
    getReq: function() {
        return new FakeExpressRequest();
    },

    getRes: function() {
        return new FakeExpressResponse();
    }
});

