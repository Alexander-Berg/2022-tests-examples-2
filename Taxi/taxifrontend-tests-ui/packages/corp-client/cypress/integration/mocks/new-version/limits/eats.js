import LimitsPage from '../../../../PageObjects/LimitsPage';

describe('Создание Лимитов Еды', () => {
    const corpUser = 'autotestcorp-newVersion';
    const limits = new LimitsPage();
    const limitName = 'Eats Manual Name';
    const serviceName = 'Еда';
    const service = 'eats2';
    const limitTitle = 'Новый лимит';

    beforeEach(() => {
        cy.yandexLogin(corpUser);
        cy.prepareLocalStorage();
        cy.corpOpen('/limits');
        limits.responseAfterSaveLimits();
    });
    context('Создаём лимиты Еды', () => {
        it('corptaxi-1077: Создание лимита без ограничений. Сервис Еда', () => {
            limits.clickAddNewLimitBtn();
            cy.get('[placeholder="Название лимита"]').should('have.value', limitTitle);
            limits.enterTitle(limitName).chooseService(serviceName).clickBtn('Сохранить');

            cy.wait('@saveLimits')
                .its('request.body')
                .then(xhr => {
                    expect(xhr).to.deep.equal({
                        limits: {},
                        service: service,
                        title: limitName
                    });
                });
        });

        it('corptaxi-1078: Создание лимита с ограничением по сумме. Сервис Еда', () => {
            let costValue = 11000;
            limits.clickAddNewLimitBtn();
            cy.get('[placeholder="Название лимита"]').should('have.value', limitTitle);
            limits
                .enterTitle(limitName)
                .chooseService(serviceName)
                .chooseRestrictions(service, 'cost')
                .getCostValue(service)
                .eq(0)
                .click()
                .type(costValue);
            limits.clickBtn('Сохранить');

            let ndsValue = costValue + (costValue / 100) * 20;

            cy.wait('@saveLimits')
                .its('request.body')
                .then(xhr => {
                    expect(xhr).to.deep.equal({
                        limits: {
                            orders_cost: {
                                value: '' + ndsValue + '',
                                period: 'month'
                            }
                        },
                        service: service,
                        title: limitName
                    });
                });
        });

        it('corptaxi-1079: Создание лимита с ограничением по времени. Сервис Еда', () => {
            limits.clickAddNewLimitBtn();
            cy.get('[placeholder="Название лимита"]').should('have.value', limitTitle);
            limits
                .enterTitle(limitName)
                .chooseService(serviceName)
                .chooseRestrictions(service, 'date');
            limits.clickBtn('Дни недели/время');
            limits.fillRestrictionsDateTime(service, 'date.items.0.time', '00:00-21:00');
            limits.clickBtn('Дни недели/время');
            limits.fillRestrictionsDateTime(service, 'date.items.1.time', '00:00-21:00');
            limits.fillRestrictionsDaysType(service, 'date.items.1.daysType', 'Выходные');

            limits.clickBtn('Сохранить');

            cy.wait('@saveLimits')
                .its('request.body')
                .then(xhr => {
                    expect(xhr).to.deep.equal({
                        limits: {},
                        service: service,
                        time_restrictions: [
                            {
                                type: 'weekly_date',
                                start_time: '00:00:00',
                                end_time: '21:00:00',
                                days: ['mo', 'tu', 'we', 'th', 'fr']
                            },
                            {
                                type: 'weekly_date',
                                start_time: '00:00:00',
                                end_time: '21:00:00',
                                days: ['sa', 'su']
                            }
                        ],
                        title: limitName
                    });
                });
        });

        it('corptaxi-1080: Создание лимита с ограничением по адресу. Сервис Еда', () => {
            limits.clickAddNewLimitBtn();
            cy.get('[placeholder="Название лимита"]').should('have.value', limitTitle);
            limits
                .enterTitle(limitName)
                .chooseService(serviceName)
                .chooseRestrictions(service, 'geo');
            limits.fillRestrictionDisctrict(service, '0.destination', 'District One');
            limits.clickBtn('Ограничение');
            limits.fillRestrictionDisctrict(service, '1.destination', 'District Two');
            limits.clickBtn('Сохранить');

            cy.wait('@saveLimits')
                .its('request.body')
                .then(xhr => {
                    expect(xhr).to.deep.equal({
                        service: service,
                        title: limitName,
                        geo_restrictions: [
                            {destination: '46636f48cf134429888f5fc919bf99c1'},
                            {destination: '90f8620c486c4490ae60a154686c48ef'}
                        ],
                        limits: {}
                    });
                });
        });
    });

    it('corptaxi-1081: Удаление лимита. Сервис Еда', () => {
        const limitId = '25c1c3274fc1446096febdeecd377a6c';
        const limitName = 'Delete Eats Limits';
        const serviceName = 'Eats';
        limits.fixtureAllLimits(limitId).fixtureViewLimit(limitId, serviceName);
        limits.getExistingLimit(limitName).click();
        limits.clickDeleteLimitBtn();
        limits.clickBtn('Удалить');

        cy.wait('@removeLimits').its('response.statusCode').should('eq', 200);
        limits.getExistingLimit(limitName).should('not.exist');
    });

    it('corptaxi-1082: Создание лимита с разными временными интервалами. Сервис Еда', () => {
        limits.clickAddNewLimitBtn();
        cy.get('[placeholder="Название лимита"]').should('have.value', limitTitle);
        limits
            .enterTitle(limitName)
            .chooseService(serviceName)
            .chooseRestrictions(service, 'date')
            .clickBtn('Дни недели/время');
        limits.fillRestrictionsDateTime(service, 'date.items.0.time', '00:30-21:00');
        limits.fillRestrictionsDaysType(service, 'date.items.0.daysType', 'Будни');
        cy.get(`input[name="${service}.customFormState.restrictions.date.items.0.time"`).should(
            'have.value',
            '00:30-21:00'
        );
        limits.clickBtn('Дни недели/время');
        limits.fillRestrictionsDateTime(service, 'date.items.1.time', '01:14-09:00');
        cy.get(`input[name="${service}.customFormState.restrictions.date.items.1.time"`).should(
            'have.value',
            '01:14-09:00'
        );
        limits.fillRestrictionsDaysType(service, 'date.items.1.daysType', 'Выходные');
        cy.get(`input[name="${service}.customFormState.restrictions.date.items.1.daysType"`).should(
            'have.value',
            'Выходные'
        );
        limits.clickBtn('Интервал').fillRestrictionsInterval('01.01.2022', '09.09.2024');
        cy.xpath('//*[text()="Период"]/..//input').should('have.value', '01.01.2022 - 09.09.2024');
    });

    it('corptaxi-1083: Закрытие незаполненной формы. Вкладка лимиты', () => {
        limits.clickAddNewLimitBtn();
        limits.clickBtn('Отмена');
        cy.get('form').should('not.exist');
    });

    it('corptaxi-1084: Закрытие заполненной формы. Вкладка лимиты', () => {
        limits.clickAddNewLimitBtn();
        cy.get('[placeholder="Название лимита"]').should('have.value', limitTitle);
        limits.enterTitle(limitName).chooseService(serviceName).clickBtn('Отмена').clickBtn('Нет');
        cy.get('form').should('not.exist');
    });
});
