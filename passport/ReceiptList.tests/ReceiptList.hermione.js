describe('Component', function () {
    describe('ReceiptList', function () {
        const storyNames = [
            'default',
        ];

        for (const storyName of storyNames) {
            it(storyName, function () {
                return this.browser
                    .openComponent(`component-receiptlist--${storyName}`)
                    .assertView(storyName, '#root');
            });
        }
    });
});
