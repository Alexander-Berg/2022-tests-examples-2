describe('Component', function () {
    describe('PenaltyCard', function () {
        const storyNames = [
            'default',
            'with-discount',
            'with-plus',
            'negative',
            'with-checkbox',
            'with-checked-checkbox',
        ];

        for (const storyName of storyNames) {
            it(storyName, function () {
                return this.browser
                    .openComponent(`component-penaltycard--${storyName}`)
                    .assertView(storyName, '#root');
            });
        }
    });
});
