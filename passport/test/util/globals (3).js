var inNode = typeof GLOBAL === 'object';

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
})(inNode ? GLOBAL : window); //GLOBAL for node and window for browser

if (inNode) {
    //Turning off logging in tests

    var intel = require('intel');

    intel.getLogger('passport').setLevel(intel.CRITICAL);

    require('putils').csrf.setSalt('Ophah3ean3feaw2uv5rinoo5udee1oongei2phieZ3ohpie3bier3Eth8ohghoos');
    require('putils')
        .i18n.setAllowedLangs(require('../../configs/current').langs)
        .setKeysets(['Common', 'EULA', 'Frontend', 'SimpleReg'])
        .setLocDir(__dirname + '/../../loc');
}
