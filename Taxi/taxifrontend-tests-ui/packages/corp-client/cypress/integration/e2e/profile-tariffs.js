import TariffsPage from '../../PageObjects/TariffsPage';

describe('Тарифы', () => {
    const corpUser = 'autotestcorp-profile';
    const tariffs = new TariffsPage();

    beforeEach(() => {
        cy.yandexLogin(corpUser);
        cy.prepareLocalStorage();
    });

    it('corptaxi-1130: Переход на вкладку Тарифы', () => {
        cy.visit('profile/');
        tariffs.clickBtn('Тарифы');
        cy.url().should('contain', 'profile/tariffs');
    });

    it('corptaxi-1131: Выбор города. Раздел Тарифы. Вкладка Профиль', () => {
        tariffs
            .openTariffsByUrl('profile/tariffs/?country=rus&zone=novosibirsk')
            .selectCity('Москва');
        cy.get('h2').contains('Тарифы для города Москва').should('exist');
    });

    it('corptaxi-1132: Выбор тарифа. Раздел Тарифы. Вкладка Профиль', () => {
        tariffs
            .openTariffsByUrl(
                '/profile/tariffs?country=rus&zone=moscow&tariff=econom&category=interval.day&category_type=application&day_type=0'
            )
            .selectTariff('Комфорт')
            .expectTariffHeadersShouldBeVisible();
    });

    it('corptaxi-1133: Выбор трансфера. Раздел Тарифы. Вкладка Профиль', () => {
        tariffs
            .openTariffsByUrl(
                '/profile/tariffs?country=rus&zone=moscow&tariff=econom&category=interval.day&category_type=application&day_type=0'
            )
            .selectTransfer('Аэропорт Домодедово — Москва')
            .expectTransferHeadersShouldBeVisible();
    });
});
