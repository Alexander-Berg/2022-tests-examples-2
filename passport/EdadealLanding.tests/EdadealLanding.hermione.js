describe('Component', function () {
    describe('EdadealLanding', function () {
        const storyNames = [
            'default',
        ];

        for (const storyName of storyNames) {
            it(storyName, function () {
                return this.browser
                    .openComponent(`component-edadeallanding--${storyName}`)
                    .assertView(storyName, '#root');
            });
        }
    });
});
