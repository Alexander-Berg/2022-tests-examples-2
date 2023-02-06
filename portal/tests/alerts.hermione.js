'use strict';

const {alertBlocks} = require('../alerts/alert-handles');
const {geoblock} = require('../alerts/geoblock');
const {geoblock2} = require('../alerts/geoblock2');
const {getCases, grouping} = require('./helper');

geoblock.testConfig.cases = geoblock.testConfig.cases.concat(geoblock2.testConfig.cases);
alertBlocks[geoblock.id] = geoblock;

const alerts = getCases(alertBlocks);
const darkAlerts = alerts.filter(card => !card.skipDarkMode);

specs('alerts', function () {
    // светлая тема
    grouping(alerts).forEach(group=>{
        it(`light#${group.id}`, async function () {
            let order = -2;
            await this.browser.yaOpenPP({cards: group.items, type: 'alert'});
            await this.browser.yaScrollPP(-1, 12000);

            for (let alert of group.items) {
                const position = order += 2; // после каждого тестируемого блока стоит псевдоблок, которую не нужно снимать

                await this.browser.yaScrollPP(position, 8000);
                await this.browser.assertViewPP(alert);
            }
        });
    });

    // темная тема
    it('dark', async function () {
        await this.browser.yaOpenPP({cards: darkAlerts, isDark: true, type: 'alert'});
        await this.browser.yaScrollPP(-1, 12000);

        let order = -2;
        for (let card of darkAlerts) {
            let position = order += 2;

            await this.browser.yaScrollPP(position, 8000);
            await this.browser.assertViewPP(card);
        }
    });
});

specs('shortcuts', function () {
    it('all', async function () {
        await this.browser.yaOpenPP({
            cardId: 'all',
            type: 'shortcut'
        });
        await this.browser.yaScrollPP(0);
        await this.browser.assertViewPP({name: 'all'});

        await this.browser.yaOpenPP({
            cardId: 'all',
            type: 'shortcut',
            isDark: true
        });
        await this.browser.yaScrollPP(0);
        await this.browser.assertViewPP({name: 'all-dark'});
    });

    it('all-wide', async function () {
        await this.browser.yaOpenPP({
            cardId: 'all',
            type: 'shortcut-wide'
        });
        await this.browser.yaScrollPP(-1, 10000);
        await this.browser.yaScrollPP(0);
        await this.browser.assertViewPP({name: 'all-wide'});
    });
});
