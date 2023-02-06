import TariffsPage from '../../PageObjects/TariffsPage';

describe('Публичные тарифы', () => {
    const tariffs = new TariffsPage();

    it('corptaxi-1134: Выбор города. Публичные Тарифы', () => {
        tariffs
            .openTariffsByUrl('/public/tariffs?country=rus&zone=novosibirsk')
            .selectCity('Москва');
        cy.get('h2').contains('Тарифы для города Москва').should('exist');
    });

    it('corptaxi-1135: Выбор тарифа. Публичные Тарифы', () => {
        tariffs
            .openTariffsByUrl(
                '/public/tariffs?country=rus&zone=moscow&tariff=econom&category=interval.day&category_type=application&day_type=0'
            )
            .selectTariff('Комфорт')
            .expectTariffHeadersShouldBeVisible();
    });

    it('corptaxi-1136: Выбор трансфера. Публичные Тарифы', () => {
        tariffs
            .openTariffsByUrl(
                '/public/tariffs?country=rus&zone=moscow&tariff=econom&category=interval.day&category_type=application&day_type=0'
            )
            .selectTransfer('Аэропорт Домодедово — Москва')
            .expectTransferHeadersShouldBeVisible();
    });
});
