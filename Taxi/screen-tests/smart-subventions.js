const auth = require('../support/auth');
const checkAdminElement = require('../support/checkAdminElement');

describe('/smart-subventions', () => {
    before(async () => {
        await auth();
    });

    it('Блок с фильтрами', async () => {
        await checkAdminElement(
            {'subventions-filters': '.SmartSubventionsFilter__container'},
            '/smart-subventions',
            async () => {
                // ожидание пока появятся и пропадут лоадеры в инпутах
                await browser.$('.Select-loading').waitForDisplayed();
                await browser.$('.Select-loading').waitForExist({reverse: true});
            }
        );
    });

    it('Список субсидий в зоне. Действующие/ненаступившие', async () => {
        await checkAdminElement(
            {'subventions-list-actual': '.SmartSubventionsTableWrapper'},
            '/smart-subventions?tariff_zones=br_root%2Fbr_russia%2Fbr_tsentralnyj_fo%2Fbr_moskovskaja_obl%2Fbr_moscow%2Fbr_moscow_adm%2Fmoscow',
            async () => {
                // ожидание пока появятся заголовок в таблице
                await browser.$('//*[text()="Тариф заказа"]').waitForDisplayed({timeout: 15000});
            }
        );
    });

    it('Список субсидий в зоне. Истекшие', async () => {
        await checkAdminElement(
            {'subventions-list-old': '.SmartSubventionsTableWrapper'},
            '/smart-subventions?tariff_zones=br_root%2Fbr_russia%2Fbr_tsentralnyj_fo%2Fbr_moskovskaja_obl%2Fbr_moscow%2Fbr_moscow_adm%2Fmoscow&tab=old&defaultPeriod=&__',
            async () => {
                // ожидание пока появятся заголовок в таблице
                await browser.$('//*[text()="Тариф заказа"]').waitForDisplayed({timeout: 15000});
            }
        );
    });
});
