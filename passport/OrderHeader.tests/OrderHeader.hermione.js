describe('Component', function () {
    describe('OrderHeader', function () {
        const storyNames = [
            'default',
            'plus',
            'plus-deducting',
            'cancelled',
            'refunded',
            'family-payment',
            'push-view-en',
            'push-view-ru',
            'advance',
        ];

        for (const storyName of storyNames) {
            it(storyName, function () {
                return this.browser
                    .openComponent(`component-orderheader--${storyName}`)
                    .assertView(storyName, '#root');
            });
        }
    });
});
