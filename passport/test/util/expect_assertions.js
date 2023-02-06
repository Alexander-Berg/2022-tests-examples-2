if (!expect && typeof require === 'function') {
    var expect = require('expect.js');
}

expect.Assertion.prototype.aJqueryDeferredPromise = function() {
    /*
     How do I know if an object is indeed a jquery deferred promise?

     Promise exposes [then, done, fail, always, pipe, progress, state],
     but not [resolve, reject, notify, resolveWith, rejectWith, notifyWith].
     @see http://api.jquery.com/deferred.promise/

     Go-go duck typing.
     */

    var obj = this.obj;
    var not = this.flags.not;

    ['then', 'done', 'fail', 'always', 'pipe', 'progress', 'state'].forEach(function(method) {
        var assertion = expect(obj[method]).to;

        if (not) {
            assertion = assertion.not;
        }
        assertion.be.a('function');
    });

    if (!not) {
        ['resolve', 'reject', 'notify', 'resolveWith', 'rejectWith', 'notifyWith'].forEach(function(method) {
            expect(obj[method]).to.be(undefined);
        });
    }
};
