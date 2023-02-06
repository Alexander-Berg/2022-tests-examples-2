describe('Component', function () {
    describe('Card', function () {
        const storyNames = [
            'default',
            'without-description',
            'without-plus',
            'paid-plus',
            'without-price',
            'with-status-refunded',
            'refunded-plus',
            'refunded-negative-plus',
            'with-status-cancelled',
            'long-text',
            'family-payment',
            'with-cashback',
            'with-status-advance',
        ];

        for (const storyName of storyNames) {
            it(storyName, function () {
                return this.browser
                    .openComponent(`component-card--${storyName}`)
                    .assertView(storyName, '#root');
            });
        }
    });
});
