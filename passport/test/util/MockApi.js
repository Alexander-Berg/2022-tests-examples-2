var DAO = require('pdao/Http');

module.exports = require('inherit')(require('papi/OAuth'), {
    __constructor: function() {
        var dao = new DAO(
            'hooxohVeeraigh3ohqu2jiethaezoh9i',
            'http://api/base/url',
            0, 0, 1, 100
        );

        this.__base('zae4eo8ohtheeshee7oFaiJuacha4oht', dao, 'oauth_frontend', {}, 'ru', '123123123');
    }
});
