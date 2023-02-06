require('plog')
    .configure()
    .minLevel('critical');

GLOBAL.asyncFail = function(done, message) {
    message = message || 'Failed';
    return function(error) {
        if (error) {
            done(error);
        } else {
            done(message);
        }
    };
};
