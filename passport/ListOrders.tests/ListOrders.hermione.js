describe('Component', function () {
    describe('ListOrders', function () {
        it('default', function () {
            return this.browser
                .openComponent('component-listorders--default')
                .assertView('default', '#root');
        });
    });
});
