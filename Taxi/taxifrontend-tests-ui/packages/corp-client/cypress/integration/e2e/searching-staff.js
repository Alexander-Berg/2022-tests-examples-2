let latinName = 'David';
let cyrillicsName = 'Борис Бритва';
let phone = '+7 (992) 193 41 44';
let cyrillicsDep = 'Департамент';
let latinDep = 'Department';
let enclosedDep = 'Enclosed';

describe('Сотрудники', () => {
    const corpUser = 'autotestcorp-departments';

    beforeEach(() => {
        cy.yandexLogin(corpUser);
        cy.prepareLocalStorage();
        cy.corpOpen('staff/');
    });

    it('corptaxi-961: Поиск на латинице. Поле Поиск по сотрудникам', () => {
        cy.get('[placeholder="Поиск"]', {timeout: 10000}).type(latinName);
        cy.get('.UserV2__fullname > .UserV2__name', {timeout: 10000}).contains(latinName);
    });

    it('corptaxi-960: Поиск на русском. Поле Поиск по сотрудникам', () => {
        cy.get('[placeholder="Поиск"]', {timeout: 10000}).type(cyrillicsName);
        cy.get('.UserV2__fullname > .UserV2__name', {timeout: 10000}).contains(cyrillicsName);
    });

    it('corptaxi-962: Поиск по Номеру телефона в поле Поиск по сотрудникам', () => {
        cy.get('[placeholder="Поиск"]', {timeout: 10000}).type(phone);
        cy.get('.UserV2__fullname > .amber-typography', {timeout: 10000}).contains(phone);
    });

    it('corptaxi-963: Поиск несуществующего. Поле Поиск по сотрудникам', () => {
        cy.get('[placeholder="Поиск"]', {timeout: 10000}).type('negative');
        cy.get('.BlankSlate__text', {timeout: 10000}).contains('В этой группе ещё нет сотрудников');
    });

    it('corptaxi-965: Поиск на русском. Поле Поиск по подразделениям', () => {
        cy.get('[placeholder="Поиск по подразделениям"]', {timeout: 10000}).type(cyrillicsDep);
        cy.get('.MuiGrid-root', {timeout: 10000}).contains(cyrillicsDep);
    });

    it('corptaxi-964: Поиск на латинице. Поле Поиск по подразделениям', () => {
        cy.get('[placeholder="Поиск по подразделениям"]', {timeout: 10000}).type(latinDep);
        cy.get('.MuiGrid-root', {timeout: 10000}).contains(latinDep);
    });

    it('corptaxi-966: Поиск дочернего. Поле Поиск по подразделениям.', () => {
        cy.get('[placeholder="Поиск по подразделениям"]', {timeout: 10000}).type(enclosedDep);
        cy.get('.MuiGrid-root', {timeout: 10000}).contains(enclosedDep);
    });
});
