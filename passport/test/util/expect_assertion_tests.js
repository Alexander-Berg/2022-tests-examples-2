describe('Extra expect.js assertions', function() {
    describe('aJqueryDeferredPromise', function() {
        it('should pass given the jquery deferred promise', function() {
            var deferred = new $.Deferred();

            expect(deferred.promise()).to.be.aJqueryDeferredPromise();
        });

        it('should fail when given not a promise', function() {
            expect({}).to.not.be.aJqueryDeferredPromise();
        });
    });
});
