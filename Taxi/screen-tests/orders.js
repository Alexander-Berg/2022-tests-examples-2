const auth = require('../support/auth');
const checkAdminElement = require('../support/checkAdminElement');

describe.skip('/orders', () => {
    before(async () => {
        await auth();
    });

    // TODO Штрафы, репозишн, модалки, платежи для доставки, разные хедеры для разных заказов, корп

    it('Фильтры', async () => {
        await checkAdminElement({orderFilters: '.OrdersFilter'}, '/orders', async () => {
            await browser.$('[title="Показать все фильтры"]').click();
            await browser.$('//*[text()="Способ оплаты"]').waitForDisplayed();
        });
    });

    it('Блоки на странице заказа', async () => {
        await checkAdminElement(
            {
                orderPanel: '.Order__panel-badge',
                orderHeader: '.OrderHeader',
                orderInfo: '(//*[@class="order-information-block"])[1]',
                orderFareAndPayments: '(//*[@class="order-information-block"])[2]',
                orderPassenger: '(//*[@class="order-information-block"])[3]',
                orderRating: '(//*[@class="order-information-block"])[4]',
                orderDriver: '(//*[@class="order-information-block"])[5]',
                orderCandidates: '(//*[@class="order-information-block"])[6]',
                orderOther: '(//*[@class="order-information-block"])[7]',
                orderPaymentEvents: '(//*[@class="order-information-block"])[8]',
                orderButtons: '.order-information__buttons'
            },
            '/orders/34a2a7afd7dddada8766dbd7c7b9248a',
            async () => {
                await browser
                    .$('.OrderInformationCostPaymentsTransactions__make-debt')
                    .waitForDisplayed({timeout: 25000});
            }
        );
    });

    // часто валится из-за подгрузки дынных из YT
    it.skip('Детализация стоимости', async () => {
        await checkAdminElement(
            {orderOfferTab: '.OfferTab'},
            '/orders/34a2a7afd7dddada8766dbd7c7b9248a/offer',
            async () => {
                await browser.$('//*[text()="Trip details"]').waitForDisplayed();
                await browser.$('.amber-tumbler_checked').waitForExist();
            }
        );
    });

    it('Трек', async () => {
        await checkAdminElement(
            {orderTrack: '.OrderTrack'},
            '/orders/34a2a7afd7dddada8766dbd7c7b9248a/track',
            async () => {
                await browser.$('//*[contains(@class, "ymaps")]').waitForDisplayed();
                // Подождать ресайз карты
                await browser.pause(4000);
            }
        );
    });

    it('Чат', async () => {
        await checkAdminElement(
            {orderChat: '.OrderChat'},
            '/orders/34a2a7afd7dddada8766dbd7c7b9248a/chat',
            async () => {
                await browser.$('.OrderChat__text').waitForDisplayed();
            }
        );
    });

    it('Документы биллинга', async () => {
        await checkAdminElement(
            {orderBillingDocs: '.BillingDocs'},
            '/orders/34a2a7afd7dddada8766dbd7c7b9248a/billing-docs',
            async () => {
                // развернуть один документ
                await browser.$('(//*[@class="panel__header"])[1]').click();
                await browser.$('.Pre__wrapper').waitForDisplayed();
                // подождать анимацию
                await browser.pause(500);
            }
        );
    });

    it('Звонки', async () => {
        await checkAdminElement(
            {calls: '.order-information-block'},
            '/orders/34a2a7afd7dddada8766dbd7c7b9248a/calls'
        );
    });

    it('raw-objects', async () => {
        await checkAdminElement(
            {orderRawObjects: '.RawObjects'},
            '/orders/34a2a7afd7dddada8766dbd7c7b9248a/raw-objects'
        );
    });

    it.skip('Чеки', async () => {
        await checkAdminElement(
            {orderReceipts: '.OrderReceipts'},
            '/orders/3fe2dc278fbc3042aa2997d935bc7dc2/receipts',
            async () => {
                await browser.$('//*[text()="pdf"]').waitForDisplayed({timeout: 25000});
            }
        );
    });
});
