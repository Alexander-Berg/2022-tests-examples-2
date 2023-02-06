'use strict';
const {blocks} = require('../index');
const {getCases, grouping} = require('./helper');

let cards = getCases(blocks);

const darkCards = cards.filter(card => !card.skipDarkMode);

specs('cards', function () {
    // светлая тема, группировка по 20 ассертов/кейсов на 1 тест
    grouping(cards).forEach(group=>{
        it(`light#${group.id}`, async function () {
            let order = -2;
            const cards = group.items;
            await this.browser.yaOpenPP({cards});
            await this.browser.yaScrollPP(-1, 12000);

            for (let card of cards) {
                const position = order += 2; // после каждого тестируемого блока стоит псевдоблок, которую не нужно снимать

                await this.browser.yaScrollPP(position, 8000);
                await this.browser.assertViewPP(card);
            }
        });
    });

    // темная тема
    it('dark', async function () {
        let order = -2;
        await this.browser.yaOpenPP({cards: darkCards, isDark: true});
        await this.browser.yaScrollPP(-1, 12000);

        for (let card of darkCards) {
            let position = order += 2;

            await this.browser.yaScrollPP(position, 8000);
            await this.browser.assertViewPP(card);
        }
    });
});
