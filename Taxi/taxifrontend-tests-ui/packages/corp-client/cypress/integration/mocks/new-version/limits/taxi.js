import LimitsPage from '../../../../PageObjects/LimitsPage';

describe('Создание Лимитов Такси', () => {
    const corpUser = 'autotestcorp-newVersion';
    const limits = new LimitsPage();
    const limitName = 'Taxi Manual Name';
    const serviceName = 'Такси';
    const service = 'taxi';
    const limitTitle = 'Новый лимит';

    beforeEach(() => {
        cy.yandexLogin(corpUser);
        cy.prepareLocalStorage();
        cy.corpOpen('/limits');
        limits.responseAfterSaveLimits();
        limits.fixtureTariffs();
    });
    context('Создаём лимиты Такси', () => {

        it('corptaxi-1065: Создание лимита без ограничений. Сервис Такси', () => {
            limits.clickAddNewLimitBtn();
            cy.get('[placeholder="Название лимита"]').should('have.value', limitTitle);
            limits
                .enterTitle(limitName)
                .chooseService(serviceName)
                .clickBtn('Сохранить');

            cy.wait('@saveLimits')
                .its('request.body')
                .then(xhr => {
                    expect(xhr).to.deep.equal({
                        service: service,
                        title: limitName,
                        categories: [
                            'vip',
                            'premium_van',
                            'ultimate',
                            'maybach',
                            'cargo',
                            'child_tariff',
                            'business',
                            'comfortplus',
                            'universal',
                            'courier',
                            'minivan',
                            'econom',
                            'express'
                        ],
                        limits: {}
                    });
                });
        });

        it('corptaxi-1066: Создание лимита с ограничением по сумме. Сервис Такси', () => {
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

            cy.wait('@saveLimits')
                .its('request.body')
                .then(xhr => {
                    expect(xhr).to.deep.equal({

                        service: service,
                        title: limitName,
                        categories: [
                            'vip',
                            'premium_van',
                            'ultimate',
                            'maybach',
                            'cargo',
                            'child_tariff',
                            'business',
                            'comfortplus',
                            'universal',
                            'courier',
                            'minivan',
                            'econom',
                            'express'
                        ],
                        limits: {
                            orders_cost: {
                                value: '' + costValue + '',
                                period: 'month'
                            }
                        }
                    });
                });
        });

        it('corptaxi-1067: Создание лимита с ограничением по поездкам. Сервис Такси', () => {
            let ordersAmount = 33;
            limits.clickAddNewLimitBtn();
            cy.get('[placeholder="Название лимита"]').should('have.value', limitTitle);
            limits
                .enterTitle(limitName)
                .chooseService(serviceName)
                .chooseRestrictions(service, 'amount')
                .getOrdersAmount(service)
                .click()
                .type(ordersAmount);
            limits.clickBtn('Сохранить');

            cy.wait('@saveLimits')
                .its('request.body')
                .then(xhr => {
                    expect(xhr).to.deep.equal({
                        service: service,
                        title: limitName,
                        categories: [
                            'vip',
                            'premium_van',
                            'ultimate',
                            'maybach',
                            'cargo',
                            'child_tariff',
                            'business',
                            'comfortplus',
                            'universal',
                            'courier',
                            'minivan',
                            'econom',
                            'express'
                        ],
                        limits: {
                            orders_amount: {
                                value: ordersAmount,
                                period: 'month'
                            }
                        }
                    });
                });
        });

        it('corptaxi-1068: Создание лимита с ограничением по времени. Сервис Такси', () => {
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

                        service: service,
                        title: limitName,
                        categories: [
                            'vip',
                            'premium_van',
                            'ultimate',
                            'maybach',
                            'cargo',
                            'child_tariff',
                            'business',
                            'comfortplus',
                            'universal',
                            'courier',
                            'minivan',
                            'econom',
                            'express'
                        ],
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
                        limits: {}
                    });
                });
        });

        it('corptaxi-1070: Создание лимита с ограничением по адресам(Куда). Сервис Такси', () => {
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
                        categories: [
                            'vip',
                            'premium_van',
                            'ultimate',
                            'maybach',
                            'cargo',
                            'child_tariff',
                            'business',
                            'comfortplus',
                            'universal',
                            'courier',
                            'minivan',
                            'econom',
                            'express'
                        ],
                        geo_restrictions: [
                            { destination: '46636f48cf134429888f5fc919bf99c1' },
                            { destination: '90f8620c486c4490ae60a154686c48ef' }
                        ],
                        limits: {}
                    });
                });
        });

        it('corptaxi-1071: Создание лимита с ограничением по адресам(Откуда). Сервис Такси', () => {
            limits.clickAddNewLimitBtn();
            cy.get('[placeholder="Название лимита"]').should('have.value', limitTitle);
            limits
                .enterTitle(limitName)
                .chooseService(serviceName)
                .chooseRestrictions(service, 'geo');
            limits.fillRestrictionDisctrict(service, '0.source', 'District One');
            limits.clickBtn('Ограничение');
            limits.fillRestrictionDisctrict(service, '1.source', 'District Two');
            limits.clickBtn('Сохранить');

            cy.wait('@saveLimits')
                .its('request.body')
                .then(xhr => {
                    expect(xhr).to.deep.equal({
                        service: service,
                        title: limitName,
                        categories: [
                            'vip',
                            'premium_van',
                            'ultimate',
                            'maybach',
                            'cargo',
                            'child_tariff',
                            'business',
                            'comfortplus',
                            'universal',
                            'courier',
                            'minivan',
                            'econom',
                            'express'
                        ],
                        geo_restrictions: [
                            { source: '46636f48cf134429888f5fc919bf99c1' },
                            { source: '90f8620c486c4490ae60a154686c48ef' }
                        ],
                        limits: {}
                    });
                });
        });

        it('corptaxi-1069: Создание лимита с ограничением по адресам(Откуда-Куда). Сервис Такси', () => {
            limits.clickAddNewLimitBtn();
            cy.get('[placeholder="Название лимита"]').should('have.value', limitTitle);
            limits
                .enterTitle(limitName)
                .chooseService(serviceName)
                .chooseRestrictions(service, 'geo');
            limits.fillRestrictionDisctrict(service, '0.source', 'District One');
            limits.fillRestrictionDisctrict(service, '0.destination', 'District Two');
            limits.clickBtn('Ограничение');
            limits.fillRestrictionDisctrict(service, '1.source', 'District Three');
            limits.fillRestrictionDisctrict(service, '1.destination', 'District Four');
            limits.clickBtn('Сохранить');

            cy.wait('@saveLimits')
                .its('request.body')
                .then(xhr => {
                    expect(xhr).to.deep.equal({
                        service: service,
                        title: limitName,
                        categories: [
                            'vip',
                            'premium_van',
                            'ultimate',
                            'maybach',
                            'cargo',
                            'child_tariff',
                            'business',
                            'comfortplus',
                            'universal',
                            'courier',
                            'minivan',
                            'econom',
                            'express'
                        ],
                        geo_restrictions: [
                            {
                                source: '46636f48cf134429888f5fc919bf99c1',
                                destination: '90f8620c486c4490ae60a154686c48ef'
                            },
                            {
                                source: '46f58ce3e5b84e2f8fa18271ec1d30bf',
                                destination: 'e17a0250efdb4590bc63b2d1d0ca1349'
                            }
                        ],
                        limits: {}
                    });
                });
        });

        it('corptaxi-1072: Лимита с ограничением по тарифам (удаление через крестик). Сервис Такси', () => {
            limits.clickAddNewLimitBtn();
            cy.get('[placeholder="Название лимита"]').should('have.value', limitTitle);

            limits
                .enterTitle(limitName)
                .chooseService(serviceName);

            limits
                .removeTariffClass('Business')
                .removeTariffClass('Cruise')
                .removeTariffClass('Детский');
            limits.clickBtn('Сохранить');

            cy.wait('@saveLimits')
                .its('request.body')
                .then(xhr => {
                    expect(xhr).to.deep.equal({
                        service: service,
                        title: limitName,
                        categories: [
                            'ultimate',
                            'maybach',
                            'cargo',
                            'business',
                            'comfortplus',
                            'universal',
                            'courier',
                            'minivan',
                            'econom',
                            'express'
                        ],
                        limits: {}
                    });
                });
        });

        it('corptaxi-1073: Лимита с ограничением по тарифам (удаление через список). Сервис Такси', () => {
            limits.clickAddNewLimitBtn();
            cy.get('[placeholder="Название лимита"]').should('have.value', limitTitle);

            limits
                .enterTitle(limitName)
                .chooseService(serviceName);
            cy.get('[name="taxi.tariffs"]').eq(1).click();
            limits
                .unselectTariffClass('Business')
                .unselectTariffClass('Cruise')
                .unselectTariffClass('Детский');
            limits.clickBtn('Сохранить');

            cy.wait('@saveLimits')
                .its('request.body')
                .then(xhr => {
                    expect(xhr).to.deep.equal({
                        service: service,
                        title: limitName,
                        categories: [
                            'ultimate',
                            'maybach',
                            'cargo',
                            'business',
                            'comfortplus',
                            'universal',
                            'courier',
                            'minivan',
                            'econom',
                            'express'
                        ],
                        limits: {}
                    });
                });
        });
    });

    context('Остальные манипуляции с Лимитами Такси', () => {
        const limitId = '5f33d82041bc4efabd553821fd5d48c2';
        const limitName = 'Delete/Rename Taxi Limits';
        const fixtureServiceName = 'Taxi';
        beforeEach(() => {
            limits
                .fixtureAllLimits(limitId)
                .fixtureViewLimit(limitId, fixtureServiceName);
            limits.responseAfterChangeLimits();

        });

        it('corptaxi-1074: Редактирование лимита. Сервис Такси', () => {
            cy.intercept('PUT', '/api/2.0/limits/*', {}).as('saveChangeLimits');
            limits.getExistingLimit(limitName).click();
            cy.get('[placeholder="Название лимита"]').should('have.value', limitName);
            limits
                .enterTitle(limitName)
                .chooseRestrictions(service, 'cost')
                .chooseRestrictions(service, 'amount')
                .chooseRestrictions(service, 'date')
                .chooseRestrictions(service, 'geo');
            cy.get('[name="taxi.tariffs"]').eq(1).click();
            limits.unselectTariffClass('Business');
            limits.clickBtn('Сохранить');

            cy.wait('@saveChangeLimits')
                .its('request.body')
                .then(xhr => {
                    expect(xhr).to.deep.equal({
                        service: service,
                        title: limitName,
                        categories: [
                            'ultimate',
                            'maybach',
                            'cargo',
                            'business',
                            'comfortplus',
                            'universal',
                            'courier',
                            'minivan',
                            'econom',
                            'express',
                            'child_tariff',
                            'premium_van',
                            'vip'
                        ],
                        limits: {}
                    });
                });
        });

        it('corptaxi-1075: Удаление лимита. Сервис Такси', () => {
            limits.getExistingLimit(limitName).click();
            limits.clickDeleteLimitBtn();
            limits.clickBtn('Удалить');

            cy.wait('@removeLimits').its('response.statusCode').should('eq', 200);
            limits.getExistingLimit(limitName).should('not.exist');
        });

        it('corptaxi-1076: Создание лимита с разными временными интервалами. Сервис Такси', () => {
            const serviceName = 'Такси';
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
            limits
                .clickBtn('Интервал')
                .fillRestrictionsInterval('01.01.2022', '09.09.2024')
            cy.xpath('//*[text()="Период"]/..//input').should('have.value', '01.01.2022 - 09.09.2024')
        });
    });
});
