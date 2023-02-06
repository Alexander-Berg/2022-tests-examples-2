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

    var logger = require('plog');
    logger.configure().minLevel('critical');
} else {
    //Multiauth vars
    var uid = undefined;
    var login = undefined;
    var passportHost = undefined;
}
