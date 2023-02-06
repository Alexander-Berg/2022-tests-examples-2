import info from '../../fixtures/responses/client/client-info.json';
describe('Настройки профиля', () => {
    context('Прочие проверки', () => {
        beforeEach(() => {
            cy.yandexLogin('autotestcorp-prepaid');
            cy.prepareLocalStorage();
            cy.intercept('GET', '/api/1.0/client/*', {
                fixture: 'responses/client/client-info.json'
            }).as('info');
            cy.visit('/profile/settings');
            cy.intercept('POST', '/api/1.0/client/*/invoice', {
                body: {
                    invoice_url:
                        'https://passport.yandex.ru/passport?mode=subscribe&from=balance&retpath=https%3A%2F%2Fuser-balance.greed-tc.paysys.yandex.ru%2Fpaypreview.xml%3Frequest_id%3D3826300349%26ref_service_id%3D650%26region%3Dru'
                }
            }).as('invoice');
        });

        it('corptaxi-540: Получение токена для API. Раздел Настройки. Вкладка профиль', () => {
            cy.location().then(loc => {
                if (loc.hostname === 'corp-client.taxi.tst.yandex.ru') {
                    cy.xpath(`//h5[text() = 'Получить токен для API']`)
                        .contains('Получить токен для API')
                        .click();
                    cy.get('.amber-modal-content').should('exist');
                    cy.get('.amber-modal-content').contains('Токен сгенерирован').should('exist');
                    cy.get('.amber-modal-content .amber-input__control').should('exist');
                    cy.get('.amber-modal-content .amber-button__text').click();
                } else {
                    cy.xpath(`//h5[text() = 'Получить токен для API']`)
                        .contains('Получить токен для API')
                        .click();
                    // Проверка модалки токена для анстейбла, тк в неё не получится получить токен
                    cy.visit(
                        '/oauth#access_token=AQAAAADvD5YYAAAPeC5j_Qji7UBer3riOURXVwU&token_type=bearer&expires_in=28443092'
                    );
                    cy.getModal().should('exist');
                    cy.getModal()
                        .find('.amber-input input')
                        .should('have.value', 'AQAAAADvD5YYAAAPeC5j_Qji7UBer3riOURXVwU');
                }
            });
        });

        it('corptaxi-1054: Напоминание о низком балансе выключено', () => {
            cy.intercept('/api/1.0/client/*/contracts?is_active=true', {
                fixture: 'responses/client/contract-settings-off'
            }).as('contract-off');
            cy.visit('/profile/settings');
            cy.wait('@contract-off');
            cy.xpath(`//h2/..//*[name()="svg"]`).click();
            cy.xpath(`//div[text() = 'при балансе ']`).should('not.exist');
        });

        it('corptaxi-1055: Чекбокс Напомнить об оплате включен', () => {
            cy.allure().tms('Тесткейс', 'taxiweb-1524');
            cy.intercept('/api/1.0/client/*/contracts?is_active=true', {
                fixture: 'responses/client/contract-settings-on'
            }).as('contract-on');
            cy.visit('/profile/settings');
            cy.wait('@contract-on');
            cy.xpath(`//h2/..//*[name()="svg"]`).click();
            cy.xpath(`//div[text() = 'при балансе ']`).should('exist');
            cy.get('.amber-section .price_theme_no-opacity').contains('100 100');
            cy.get('.amber-button_theme_accent', {timeout: 10000}).click();
        });

        it('corptaxi-1056: Формирование счета, ручка invoice. Вкладка профиль', () => {
            cy.allure().tms('Тесткейс', 'taxiweb-1530');
            cy.xpath(`//h5[text() = 'Сформировать счёт']`).click();
            cy.get('.amber-button_theme_fill').should('have.class', 'amber-button_disabled');
            cy.get('.MuiTextField-root').click().type('100');
            cy.get('.amber-button_theme_fill').should('not.have.class', 'amber-button_disabled');
            cy.get('.amber-button__text').contains('Сформировать счёт').click();
            cy.wait('@invoice')
                .its('request.body')
                .then(body => {
                    expect(body.value).eq(100);
                });
        });

        it('corptaxi-1057: Проверка наличия полей. Имя Почта id Логин', () => {
            cy.allure().tms('Тесткейс', 'taxiweb-1527');
            cy.visit('/profile/settings');
            cy.xpath('//*[@title="autotestcorp-prepaid-name"]');
            cy.get('[id="clamped-content-clientName"]').should(
                'have.text',
                'autotestcorp-prepaid-name'
            );
            cy.xpath(`//h5[text() = '21786dbbfa014bff81c7d47afda60e2d']`).should(
                'have.text',
                '21786dbbfa014bff81c7d47afda60e2d'
            );
            cy.xpath(`//h5[text() = 'dffddf@test.com']`).should('have.text', 'dffddf@test.com');
            cy.xpath(`//h5[text() = 'autotestcorp-prepaid-login']`).should(
                'have.text',
                'autotestcorp-prepaid-login'
            );
        });
    });

    context('Сервисы. Состояние чекбоксов', () => {
        beforeEach(() => {
            cy.yandexLogin('autotestcorp-prepaid');
            cy.prepareLocalStorage();
        });

        it('corptaxi-1059: Включение сервисов: такси, логистика, еда, драйв, маркет', () => {
            cy.allure().tms('Тесткейс', 'taxiweb-1701');
            cy.intercept('GET', '/api/1.0/client/*/services', {
                fixture: 'responses/client/client-services-off.json'
            }).as('services');
            cy.intercept('/api/1.0/client/*/contracts?is_active=true', {
                fixture: 'responses/client/services'
            }).as('modal');
            cy.visit('/profile/settings');
            cy.intercept('PATCH', '/api/1.0/client/*/services/taxi', {
                is_visible: true,
                comment: 'коммент корповый да',
                default_category: 'econom'
            });
            cy.intercept('PATCH', '/api/1.0/client/*/services/cargo', {is_visible: true});
            cy.intercept('PATCH', '/api/1.0/client/*/services/eats2', {is_visible: true});
            cy.intercept('PATCH', '/api/1.0/client/*/services/drive', {is_visible: true});
            cy.intercept('PATCH', '/api/1.0/client/*/services/market', {is_visible: true});
            cy.get('[type="checkbox"]').eq(0).click();
            cy.get('[type="checkbox"]').eq(1).click();
            cy.get('[type="checkbox"]').eq(2).click();
            cy.get('[type="checkbox"]').eq(3).click();
            cy.get('[type="checkbox"]').eq(4).click();
            cy.get('.Mui-checked').eq(0).should('exist');
            cy.get('.Mui-checked').eq(1).should('exist');
            cy.get('.Mui-checked').eq(2).should('exist');
            cy.get('.Mui-checked').eq(3).should('exist');
            cy.get('.Mui-checked').eq(4).should('exist');
        });

        it('corptaxi-1058: Выключение сервисов: такси, логистика, еда, драйв, маркет', () => {
            cy.allure().tms('Тесткейс', 'taxiweb-1881');
            cy.intercept('GET', '/api/1.0/client/*/services', {
                fixture: 'responses/client/client-services-on.json'
            }).as('services');
            cy.intercept('/api/1.0/client/*/contracts?is_active=true', {
                fixture: 'responses/client/services'
            }).as('modal');
            cy.visit('/profile/settings');
            cy.intercept('PATCH', '/api/1.0/client/*/services/taxi', {
                is_visible: false,
                comment: 'коммент корповый да',
                default_category: 'econom'
            });
            cy.intercept('PATCH', '/api/1.0/client/*/services/cargo', {is_visible: false});
            cy.intercept('PATCH', '/api/1.0/client/*/services/eats2', {is_visible: false});
            cy.intercept('PATCH', '/api/1.0/client/*/services/drive', {is_visible: false});
            cy.intercept('PATCH', '/api/1.0/client/*/services/market', {is_visible: false});
            cy.get('[type="checkbox"]').eq(0).click();
            cy.xpath('//*[text()="Да"]').click();
            cy.get('[type="checkbox"]').eq(1).click();
            cy.xpath('//*[text()="Да"]').click();
            cy.get('[type="checkbox"]').eq(2).click();
            cy.xpath('//*[text()="Да"]').click();
            cy.get('[type="checkbox"]').eq(3).click();
            cy.xpath('//*[text()="Да"]').click();
            cy.get('[type="checkbox"]').eq(4).click();
            cy.xpath('//*[text()="Да"]').click();
            // Проверяет, что нет ни одного включенного чекбокса
            cy.get('.Mui-checked').should('not.exist');
        });
    });
});
