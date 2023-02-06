import news from '../../fixtures/responses/announcements/news/news.json';
import promo from '../../fixtures/responses/announcements/promos/promo.json';
import promoOneNotRead from '../../fixtures/responses/announcements/promos/promo_one_unread.json';
import dayjs from 'dayjs';

const datePromoPublish = dayjs(promo.announcements[0].publish_at).format('DD.MM.YYYY');

function pushAnnouncement() {
    cy.request({url: '/api/auth', headers: {'X-Application-Version': '0.0.82'}}).then(response => {
        const clientId = response.body.client_id;
        window.localStorage.removeItem(`${clientId}.corp-client.push.timestamp`);
    });
}

function fixtureAnnouncement(news, promo) {
    cy.intercept('/api/1.0/client/*/announcements', {
        fixture: 'responses/announcements/news/' + news + ''
    });
    cy.intercept('/api/1.0/client/*/announcements/promos', {
        fixture: 'responses/announcements/promos/' + promo + ''
    });
}

describe('Уведомления', () => {
    beforeEach(() => {
        cy.yandexLogin('autotestcorp-profile');
        cy.prepareLocalStorage();
    });

    it('corptaxi-896: Отображается список новых уведомлений при открытии страницы(промо+новость)', () => {
        cy.allure().tms('Тесткейс', 'taxiweb-1676');
        fixtureAnnouncement('news', 'promo_one_unread');
        pushAnnouncement();

        cy.visit('/');
        cy.get(':nth-child(1)')
            .contains(promoOneNotRead.announcements[0].title, {timeout: 10000})
            .should('exist');
        cy.get(':nth-child(1)')
            .contains(promoOneNotRead.announcements[0].text, {timeout: 10000})
            .should('exist');
        cy.get(':nth-child(2)')
            .contains(news.announcements[0].title, {timeout: 10000})
            .should('exist');
        cy.get(':nth-child(2)')
            .contains(news.announcements[0].text, {timeout: 10000})
            .should('exist');
    });

    it('corptaxi-897: Отображается список новых уведомлений при открытии страницы(2 промо)', () => {
        fixtureAnnouncement('news-read', 'promo');
        pushAnnouncement();

        cy.visit('/');
        cy.get(':nth-child(1)')
            .contains(promo.announcements[0].title, {timeout: 10000})
            .should('exist');
        cy.get(':nth-child(1)')
            .contains(promo.announcements[0].text, {timeout: 10000})
            .should('exist');
        cy.get(':nth-child(2)')
            .contains(promo.announcements[1].title, {timeout: 10000})
            .should('exist');
        cy.get(':nth-child(2)')
            .contains(promo.announcements[1].text, {timeout: 10000})
            .should('exist');
    });

    it('corptaxi-898: Отображается список новых уведомлений при открытии страницы(2 новости)', () => {
        fixtureAnnouncement('news', 'promo-read');
        pushAnnouncement();

        cy.visit('/');
        cy.get(':nth-child(1)', {timeout: 10000})
            .contains(news.announcements[0].title)
            .should('exist');
        cy.get(':nth-child(1)', {timeout: 10000})
            .contains(news.announcements[0].text)
            .should('exist');
        cy.get(':nth-child(2)', {timeout: 10000})
            .contains(news.announcements[1].title)
            .should('exist');
        cy.get(':nth-child(2)', {timeout: 10000})
            .contains(news.announcements[1].text)
            .should('exist');
    });

    it('corptaxi-899: Уведомления через некоторое время закрываются', () => {
        fixtureAnnouncement('news', 'promo');
        pushAnnouncement();

        cy.visit('/orders');
        cy.xpath(`(//*[text()='${promo.announcements[0].title}'])[1]`, {timeout: 10000}).should(
            'be.visible'
        );
        cy.xpath(`(//*[text()='${promo.announcements[0].title}'])[1]`, {timeout: 12000}).should(
            'not.exist'
        );
    });

    it('corptaxi-900: Клик по новому уведомлению', () => {
        fixtureAnnouncement('news', 'promo');
        pushAnnouncement();

        cy.visit('/');
        cy.get(':nth-child(1)').contains(promo.announcements[0].title, {timeout: 10000}).click();
        cy.xpath(`//*[text()='${datePromoPublish}']`, {
            timeout: 10000
        }).should('exist');
        cy.xpath(`//*[@role='presentation']//h4[text()='${promo.announcements[0].title}']`, {
            timeout: 10000
        }).should('exist');
        cy.xpath(`//*[@role='presentation']//span[text()='${promo.announcements[0].text}']`, {
            timeout: 10000
        }).should('exist');
    });

    it('corptaxi-902: Раскрытие списка уведомлений', () => {
        fixtureAnnouncement('news', 'promo');

        cy.visit('/');
        cy.get('[fill="#FA6A3C"]').click();
        cy.get(':nth-child(1)')
            .contains(promo.announcements[0].title, {timeout: 10000})
            .should('exist');
        cy.get(':nth-child(1)')
            .contains(promo.announcements[0].text, {timeout: 10000})
            .should('exist');
        cy.get(':nth-child(2)')
            .contains(promo.announcements[1].title, {timeout: 10000})
            .should('exist');
        cy.get(':nth-child(2)')
            .contains(promo.announcements[1].text, {timeout: 10000})
            .should('exist');
    });

    it('corptaxi-904: Нет новых уведомлений', () => {
        fixtureAnnouncement('news-read', 'promo-read');

        cy.visit('/');
        cy.xpath('(//header//*[@fill="currentColor"])[1]').click();
        cy.get(':nth-child(1)').contains('Нет новых уведомлений', {timeout: 10000}).should('exist');

        cy.xpath(`(//span[text()='Свернуть'])`).click();
        cy.xpath(`(//span[text()='Свернуть'])`, {timeout: 4000}).should('not.exist');
    });

    it('corptaxi-905: Клик по уведомлению в списке', () => {
        fixtureAnnouncement('news', 'promo');

        cy.visit('/');
        cy.get('[fill="#FA6A3C"]').click();
        cy.get(':nth-child(1)').contains(promo.announcements[0].title, {timeout: 10000}).click();
        cy.xpath(`//*[text()='${datePromoPublish}']`, {
            timeout: 10000
        }).should('exist');
        cy.xpath(`//*[@role='presentation']//h4[text()='${promo.announcements[0].title}']`, {
            timeout: 10000
        }).should('exist');
        cy.xpath(`//*[@role='presentation']//span[text()='${promo.announcements[0].text}']`, {
            timeout: 10000
        }).should('exist');
    });

    it('corptaxi-906: Закрытие уведомления в списке', () => {
        fixtureAnnouncement('news', 'promo');

        cy.visit('/orders');
        cy.get('[fill="#FA6A3C"]').click();

        cy.xpath(`//*[text()='${promo.announcements[0].title}']/../../../*[name()='svg']`).click();
        cy.xpath(`(//h4[text()='${promo.announcements[0].title}'])[1]`, {timeout: 10000}).should(
            'not.exist'
        );
    });

    it('corptaxi-908: Показывает иконку непрочитанных уведомлений', () => {
        fixtureAnnouncement('news', 'promo');

        cy.visit('/');
        cy.get('[fill="#FA6A3C"]').should('exist');
    });

    it('corptaxi-909: Показывает иконку прочитанных уведомлений', () => {
        fixtureAnnouncement('news-read', 'promo-read');
        cy.visit('/');
        cy.get('[fill="currentColor"]', {timeout: 10000}).should('exist');
    });

    it('corptaxi-910: Отправка на сервер пометок о прочтении', () => {
        fixtureAnnouncement('news', 'promo');
        cy.intercept('POST', '/api/1.0/client/*/announcement/read').as('markAsRead');
        cy.visit('/');
        cy.get(':nth-child(1)').contains(promo.announcements[0].title, {timeout: 10000}).click();

        pushAnnouncement();

        cy.wait('@markAsRead', {timeout: 10000})
            .its('request.body')
            .then(body => {
                expect(body).to.deep.equal({
                    announcement_id: promo.announcements[0].announcement_id
                });
            });
    });
});
