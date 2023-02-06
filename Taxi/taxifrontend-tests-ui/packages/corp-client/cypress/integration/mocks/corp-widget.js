describe('Корп виджет', () => {
    beforeEach(() => {
        cy.visit('/pages/offer');
    });

    const formData = {
        company: 'тест название',
        name: 'Маказов Магазинов Магазин',
        email: 'gdekupitpivadlyasobak@sobakalco.com',
        city: 'Архангельск',
        phone: '+79991234444',
        captcha_answer: '123789',
        utm: {
            ya_source: 'testya'
        }
    };

    const fillForm = () => {
        cy.intercept('/api/1.0/suggest/cities', {
            body: {
                items: [
                    {
                        text: 'Архангельск',
                        description: 'Архангельская область, Северо-Западный ФО, Россия',
                        city: 'Архангельск'
                    }
                ]
            }
        }).as('cities');
        cy.get('[name="company"]').type(formData.company);
        cy.get('[name="name"]').type(formData.name);
        cy.get('[name="email"]').type(formData.email);
        cy.get('[name="city-input"]')
            .type(formData.city)
            .wait('@cities')
            .get('.WidgetSuggestInput__suggest-option')
            .contains(formData.city)
            .click();
        cy.get('[name="phone"]').clear().type(formData.phone);
        cy.get('[name="captcha"]').type(formData.captcha_answer);
    };

    it('corptaxi-918: Форма не отправляется при незаполненных полях', () => {
        cy.get('[type="submit"]').click();
        cy.get('.FieldLayout__error').contains('Обязательное поле').should('exist');
    });

    it('corptaxi-921: Ошибка при неверно введенной капче', () => {
        fillForm();
        cy.intercept('/api/public/register-trial', {
            statusCode: 403,
            body: {message: 'Forbidden'}
        });
        cy.get('[type="submit"]').click();

        cy.xpath('//*[text()="Неверно введена капча"]').should('be.visible');
    });

    it('corptaxi-922: Поля формы корректно отправляются', () => {
        cy.visit(`/pages/offer?ya_source=${formData.utm.ya_source}`);
        cy.intercept('/api/public/register-trial', {
            statusCode: 200,
            body: {id: '174d6e82a65b403e92bb02668e9dac11'}
        }).as('registerTrial');

        fillForm();
        cy.get('[type="submit"]').click();

        cy.wait('@registerTrial')
            .its('request.body')
            .then(body => {
                expect(body.company).eq(formData.company);
                expect(body.name).eq(formData.name);
                expect(body.email).eq(formData.email);
                expect(body.city).eq(formData.city);
                expect(body.phone).eq(formData.phone);
                expect(body.captcha_answer).eq(formData.captcha_answer);
                expect(body.utm.ya_source).eq(formData.utm.ya_source);
            });

        cy.xpath(
            `//*[text()="Мы отправили на почту ${formData.email} логин, пароль и ссылку для входа в Личный кабинет Яндекс.Такси для бизнеса."]`
        ).should('be.visible');
    });

    it('corptaxi-923: Переход на длинный флоу', () => {
        fillForm();
        cy.intercept('/api/public/register-trial', {
            statusCode: 429,
            body: {message: 'Too Many Requests'}
        });

        cy.get('[type="submit"]').click();

        cy.xpath('//*[text()="Войти в Паспорт"]').should('be.visible');
    });
});
