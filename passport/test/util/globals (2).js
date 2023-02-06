/* eslint-disable no-unused-vars */

var inNode = typeof GLOBAL === 'object' || typeof global === 'object';

(function(global) {
    global.asyncFail = function(done, message) {
        message = message || 'Failed';
        return function(error) {
            if (error) {
                done(error);
            } else {
                done(message);
            }
        };
    };
})(inNode ? GLOBAL || global : window); //GLOBAL for node and window for browser

if (inNode) {
    require('putils').csrf.setSalt('Ophah3ean3feaw2uv5rinoo5udee1oongei2phieZ3ohpie3bier3Eth8ohghoos');
    require('putils')
        .i18n.setAllowedLangs(require('../../configs/production').langs)
        .setKeysets(['Common', 'EULA', 'Frontend', 'SimpleReg'])
        .loadFromDir(`${__dirname}/../../loc`);

    require('plog')
        .configure()
        .minLevel('critical');
}

var uid = undefined;
var login = undefined;
var passportHost = undefined;
var yr = {
    run: function() {}
};
