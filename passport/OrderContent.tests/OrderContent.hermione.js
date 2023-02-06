describe('Component', function () {
    describe('OrderContent', function () {
        const storyNames = [
            'default',
            'with-card-and-plus',
            'google-pay',
            'apple-pay',
            'with-buttons',
            'unknown-payment-card',
            'push-view',
            'with-edadeal-cashback',
            'advance-status',
        ];

        for (const storyName of storyNames) {
            it(storyName, function () {
                return this.browser
                    .openComponent(`component-orderinfo--${storyName}`)
                    .assertView(storyName, '#root');
            });
        }
    });
});
