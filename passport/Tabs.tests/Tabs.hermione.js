describe('Component', function () {
    describe('Tabs', function () {
        const storyNames = [
            'default',
            'receipts',
        ];

        for (const storyName of storyNames) {
            it(storyName, function () {
                return this.browser
                    .openComponent(`component-tabs--${storyName}`)
                    .assertView(storyName, '#root');
            });
        }
    });
});
