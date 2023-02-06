const neoPhonish = require('../../../routes/common/getCustomConfig')('customs.neophonish.config.json');
const pages = require('../utils/passportPages');
const utils = require('../utils/utils');

const TEST_ID = 231589;

describe('neoPhonish', function() {
    const {origins = [], originsMask = [], originsAB = [], originsMaskAB = [], excludedOrigins = []} = neoPhonish;

    origins.forEach((origin) => {
        const invalidTestId = 1;

        it(`Должен быть редирект с экспериментом ${TEST_ID} и ориджином ${origin}`, async function() {
            await this.browser.url(`${pages.REGISTRATION}?origin=${origin}&test-id=${TEST_ID}`);
            await this.browser.yaShouldBeAtUrl(`${pages.AUTH_REG}?origin=${origin}&test-id=${TEST_ID}`);
        });

        it(`Не должно быть редиректа с валидным ориджином ${origin} и без эксперимента ${TEST_ID}`, async function() {
            await this.browser.url(`${pages.REGISTRATION}?origin=${origin}&test-id=${invalidTestId}`);
            await this.browser.yaShouldBeAtUrl(`${pages.REGISTRATION}?origin=${origin}&test-id=${invalidTestId}`);
        });
    });

    excludedOrigins.forEach((origin) => {
        it(`Не должно быть редиректа для ориджина ${origin} из спика исключений`, async function() {
            await this.browser.url(`${pages.REGISTRATION}?origin=${origin}&test-id=${TEST_ID}`);
            await this.browser.yaShouldBeAtUrl(`${pages.REGISTRATION}?origin=${origin}&test-id=${TEST_ID}`);
        });
    });

    originsMask.forEach((mask) => {
        const origin = `${mask}_mask`;
        const invalidTestId = 1;

        it(`Должен быть редирект с экспериментом ${TEST_ID} и маской ${mask}_*`, async function() {
            await this.browser.url(`${pages.REGISTRATION}?origin=${origin}&test-id=${TEST_ID}`);
            await this.browser.yaShouldBeAtUrl(`${pages.AUTH_REG}?origin=${origin}&test-id=${TEST_ID}`);
        });

        it(`Не должно быть редиректа с валидной маской ${mask} и без эксперимента ${TEST_ID}`, async function() {
            await this.browser.url(`${pages.REGISTRATION}?origin=${origin}&test-id=${invalidTestId}`);
            await this.browser.yaShouldBeAtUrl(`${pages.REGISTRATION}?origin=${origin}&test-id=${invalidTestId}`);
        });
    });

    originsAB.forEach((origin) => {
        const abTestId = 256402;

        it(`Должен быть редирект с экспериментами ${TEST_ID} и ${abTestId} и ориджином ${origin}`, async function() {
            await this.browser.url(`${pages.REGISTRATION}?origin=${origin}&test-id=${TEST_ID}_${abTestId}`);
            await this.browser.yaShouldBeAtUrl(`${pages.AUTH_REG}?origin=${origin}&test-id=${TEST_ID}_${abTestId}`);
        });

        it(`Не должно быть редиректа с валидным ориджином ${origin} и без эксперимента ${abTestId}`, async function() {
            await this.browser.url(`${pages.REGISTRATION}?origin=${origin}&test-id=${TEST_ID}`);
            await this.browser.yaShouldBeAtUrl(`${pages.REGISTRATION}?origin=${origin}&test-id=${TEST_ID}`);
        });
    });

    originsMaskAB.forEach((mask) => {
        const origin = `${mask}_mask`;
        const abTestId = 256402;

        it(`Должен быть редирект с экспериментами ${TEST_ID} и ${abTestId} и маской ${mask}_*`, async function() {
            await this.browser.url(`${pages.REGISTRATION}?origin=${origin}&test-id=${TEST_ID}_${abTestId}`);
            await this.browser.yaShouldBeAtUrl(`${pages.AUTH_REG}?origin=${origin}&test-id=${TEST_ID}_${abTestId}`);
        });

        it(`Не должно быть редиректа с валидной маской ${mask} и без эксперимента ${abTestId}`, async function() {
            await this.browser.url(`${pages.REGISTRATION}?origin=${origin}&test-id=${TEST_ID}`);
            await this.browser.yaShouldBeAtUrl(`${pages.REGISTRATION}?origin=${origin}&test-id=${TEST_ID}`);
        });
    });

    originsAB.forEach((origin) => {
        const abTestId = 262323;

        it(`Должен быть редирект с экспериментами ${TEST_ID} и ${abTestId} и ориджином ${origin}`, async function() {
            await this.browser.url(`${pages.REGISTRATION}?origin=${origin}&test-id=${TEST_ID}_${abTestId}`);
            await this.browser.yaShouldBeAtUrl(`${pages.AUTH_REG}?origin=${origin}&test-id=${TEST_ID}_${abTestId}`);
        });

        it(`Не должно быть редиректа с валидным ориджином ${origin} и без эксперимента ${abTestId}`, async function() {
            await this.browser.url(`${pages.REGISTRATION}?origin=${origin}&test-id=${TEST_ID}`);
            await this.browser.yaShouldBeAtUrl(`${pages.REGISTRATION}?origin=${origin}&test-id=${TEST_ID}`);
        });
    });

    originsMaskAB.forEach((mask) => {
        const origin = `${mask}_mask`;
        const abTestId = 262323;

        it(`Должен быть редирект с экспериментами ${TEST_ID} и ${abTestId} и маской ${mask}_*`, async function() {
            await this.browser.url(`${pages.REGISTRATION}?origin=${origin}&test-id=${TEST_ID}_${abTestId}`);
            await this.browser.yaShouldBeAtUrl(`${pages.AUTH_REG}?origin=${origin}&test-id=${TEST_ID}_${abTestId}`);
        });

        it(`Не должно быть редиректа с валидной маской ${mask} и без эксперимента ${abTestId}`, async function() {
            await this.browser.url(`${pages.REGISTRATION}?origin=${origin}&test-id=${TEST_ID}`);
            await this.browser.yaShouldBeAtUrl(`${pages.REGISTRATION}?origin=${origin}&test-id=${TEST_ID}`);
        });
    });

    it('Регистрация', async function() {
        const PO = this.PO;
        const origin = 'neophonish';

        await this.browser.url(`${pages.AUTH_REG}?origin=${origin}&test-id=${TEST_ID}`);

        // Шаг ввода телефона
        await this.browser.yaSetValue(PO.auth.phoneInput(), utils.getRandomFakePhoneInE164());
        await this.browser.click(PO.submitButton());

        // Шаг подтверждения телефона
        const trackId = await this.browser.yaGetTrackId();
        const code = await utils.getPhoneConfirmationCode(trackId);

        await this.browser.yaSetValue(PO.auth.phoneCodeInput(), code);

        // Шаг с ФИ
        await this.browser.yaSetValue(PO.auth.firstnameInput(), 'John');
        await this.browser.yaSetValue(PO.auth.lastnameInput(), 'Doe');
        await this.browser.click(PO.submitButton());

        // Шаг с пользовательским соглашением
        await this.browser.waitUntil(
            () => this.browser.click(PO.submitButton()),
            3000,
            'не смогли согласиться с EULA за 3 секунды'
        );

        // Профиль
        await this.browser.waitUntil(
            () => this.browser.getText('.user-account_has-ticker_yes > span:nth-child(2)'),
            3000,
            'не смогли перейти на профиль за 3 секунды'
        );
        await this.browser.yaShouldBeAtUrl(`${pages.PROFILE}?origin=${origin}`);
    });
});
