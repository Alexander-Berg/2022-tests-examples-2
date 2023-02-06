const PAGE_NAME = 'adblock-test-page';

BEM.blocks['i-router'].define('GET', new RegExp(`^/${PAGE_NAME}/?$`), PAGE_NAME);

BEM.decl({block: PAGE_NAME, baseBlock: 'i-page'}, null, {
    init () {
        return this.__base(...arguments)
            .then(() => {
                return this.setTitle('Adblock testing').out();
            });
    },

    getPageJson (json) {
        return this.__base(json, PAGE_NAME);
    },
});
