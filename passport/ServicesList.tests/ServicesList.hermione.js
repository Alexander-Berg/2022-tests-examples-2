describe('Component', function () {
    describe('PayServicesList', function () {
        it('default', function () {
            return this.browser
                .openComponent('component-payserviceslist--default')
                .assertView('default', '#root');
        });
    });
});
