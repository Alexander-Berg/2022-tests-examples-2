import {AuthPageLocators, BasePageLocators} from './LocatorsPage'
var chaiColors = require('chai-colors');    
chai.use(chaiColors);

export class HomePage {
    static login() { //Авторизация//
        cy.clearCookies()
        cy.visit('http://localhost:8069')
        cy.window().then((win)=> {
            if(win.top.odoo === undefined){
                win.top.odoo = win.odoo;
            }
        })
        cy.get(AuthPageLocators.LOGIN_FIELD).type('admin')
        cy.get('.o_loading').should('not.exist');
        cy.get(AuthPageLocators.PASSWORD_FIELD).type('admin')
        cy.get('.o_loading').should('not.exist');
        cy.get('button').contains('Log In').click()
    };
    
    static login_n(login,password) { //Авторизация с переменными//
        cy.clearCookies()
        cy.visit('http://localhost:8069')
        cy.window().then((win)=> {
            if(win.top.odoo === undefined){
                win.top.odoo = win.odoo;
            }
        })
        cy.get(AuthPageLocators.LOGIN_FIELD).type(login)
        cy.get('.o_loading').should('not.exist');
        cy.get(AuthPageLocators.PASSWORD_FIELD).type(password)
        cy.get('.o_loading').should('not.exist');
        cy.get('button').contains('Log In').click()
    };
    

    // Последовательный клик по двум элементам
    static two_clicks_in_the_fields(selector,selector2) {
        cy.get('.o_loading').should('not.be.visible');
        cy.get(selector).click()
        cy.wait(500)
        cy.get('.o_loading').should('not.be.visible');
        cy.get(selector2).click()
        cy.wait(500)
    };

    static deleteNTimes(selector,meaning,n){
        let result = ""
        cy.get(selector).click()
        cy.wait(500)
        for (let i = 0; i < n; i++){
        result += "{backspace}"
        }
        cy.wait(500)
        cy.get(selector).type(meaning)
        return result
        };

    //Найти поле-кликнуть//
    static clicks_on_the_button(selector) {
        cy.wait(500)
        cy.get('.o_loading').should('not.be.visible');
        cy.get(selector).click()
    };

    //Найти поле-кликнуть xpath//
    static xpath_clicks_on_the_button(selector) {
        cy.wait(500)
        cy.get('.o_loading').should('not.be.visible');
        cy.xpath(selector).click()
    };

    //Найти поле-кликнуть-ввести данные xpath//
    static xpath_find_click_and_fill_in(selector, meaning) {
        cy.wait(500)
        cy.get('.o_loading').should('not.be.visible');
        cy.xpath(selector).type(meaning)
    };

    //Найти поле-кликнуть-ввести данные//
    static find_click_and_fill_in(selector, meaning) {
        cy.wait(500)
        cy.get('.o_loading').should('not.be.visible');
        cy.get(selector).type(meaning)
    };

    //Найти текст-кликнуть-ввести данные//
    static find_click_and_fill_in_text(tag,text,meaning) {
        cy.wait(500)
        cy.get('.o_loading').should('not.be.visible');
        cy.get(tag).contains(text).type(meaning)
        HomePage.enter_click()
    };

    //Нажатие Enter//
    static enter_click() {
        cy.wait(500)
        cy.get('.o_loading').should('not.be.visible');
        cy.get('body').type('{enter}')
    };

    //Найти элемент по тексту и кликнуть//
    static contains_click(tag,text) {
        cy.wait(500)
        cy.get('.o_loading').should('not.be.visible');
        cy.get(tag).contains(text).click()
    };

    //Проверка совпадения текста//
    static should_text(tag,text) {
        cy.get('.o_loading').should('not.be.visible');
        cy.get(tag).should('have.text',text)
    };

     //Проверка совпадения текста по всем полям//
     static cont_text(text) {
        cy.get('.o_loading').should('not.be.visible');
        cy.contains(text)
    };

      //Проверка отсутствия текста по всем полям//
      static not_cont_text(text) {
        cy.get('.o_loading').should('not.be.visible');
        cy.contains(text).should('not.exist')
    };

    //Проверка отсутствия ошибки Odoo Error//
    static not_odoo_error() {
        cy.get('.o_loading').should('not.be.visible');
        cy.contains('Odoo Error').should('not.exist')
    };

    //Проверка отсутствия элемента//
    static not_element(text) {
        cy.get('.o_loading').should('not.be.visible');
        cy.get(text).should('not.exist')
    };

    //Проверка присутствия элемента//
    static element(text) {
        cy.get('.o_loading').should('not.be.visible');
        cy.get(text).should('exist')
    };

    //Проверка присутствия элемета xpath циклом//
    static xpath_cycle(...elements) {
        cy.get('.o_loading').should('not.be.visible');
        elements.forEach(e => cy.xpath(e))
     };

     //Проверка присутствия элемета get циклом//
    static get_cycle(...elements) {
        cy.get('.o_loading').should('not.be.visible');
        elements.forEach(e => cy.get(e))
     };

    //Проверка присутствия текста циклом//
    static element_cycle(...elements) {
        cy.get('.o_loading').should('not.be.visible');
        elements.forEach(e => cy.contains(e))
     };

    // кликни и нажми enter
    static clicks_button_enter(selector) {
        cy.wait(500)
        cy.get('.o_loading').should('not.be.visible');
        cy.get(selector).click()
        HomePage.enter_click()
    };

    //Найти поле-кликнуть-ввести данные-нажать enter//
    static click_write_enter(selector, meaning) {
        cy.wait(500)
        cy.get('.o_loading').should('not.be.visible');
        cy.get(selector).type(meaning)
        HomePage.enter_click()
    };

    // кликни, очисти поле и введи данные
    static clicks_button_clear(selector,meaning) {
        cy.wait(500)
        cy.get('.o_loading').should('not.be.visible');
        cy.get(selector).click().clear()
        cy.get(selector).type(meaning)      
    };

    // кликни, очисти поле и введи данные нажми enter
    static clicks_button_clear_enter(selector,meaning) {
        cy.wait(500)
        cy.get('.o_loading').should('not.be.visible');
        cy.get(selector).click().clear()
        cy.get(selector).type(meaning)
        HomePage.enter_click()      
    };

    //выбор значения из выпадающего списка
    static clicks_button_select(selector,select) {
        cy.wait(500)
        cy.get('.o_loading').should('not.be.visible')
        cy.get(selector).select(select)
    };

    //текущая дата.Передавать HomePage.date_local()
    static date_local() {
        cy.wait(500)
        const date = new Date()
        return date.toLocaleString()
    };

    //текущая дата+n часов.Передавать HomePage.date_local_n()
    static date_local_n(n) {
        cy.wait(500)
        const date = new Date()
        date.setHours(n);
        return date.toLocaleString()
    };

    //проверка цвета - вводить код в формате rgb(220, 165, 0)
    static color_check(selector,code) {
        cy.wait(500)
        cy.get('.o_loading').should('not.be.visible')
        cy.get(selector)
            .should('have.css', 'color')
            .and('eq', code)
    };

    //Ожидание появления элемента//
    static element_n(text,time) {
        cy.wait(500)
        cy.get('.o_loading').should('not.be.visible');
        cy.get(text, {timeout: time}).should('exist')
    };

    //Ожидание появления элемента xpath//
    static element_n_xp(text,time) {
        cy.wait(500)
        cy.get('.o_loading').should('not.be.visible');
        cy.xpath(text, {timeout: time}).should('exist')
    };

    //Ожидание появления текста//
    static text_n(text,time) {
        cy.wait(500)
        cy.get('.o_loading').should('not.be.visible');
        cy.contains(text, {timeout: time}).should('exist')
    };


    //Ожидание пока элемент исчезнет//
    static not_element_n(text,time) {
        cy.get('.o_loading').should('not.be.visible');
        cy.get(text, {timeout: time}).should('not.exist')
    };   

    //Ожидание пока текст исчезнет//
    static not_text_n(text,time) {
        cy.get('.o_loading').should('not.be.visible');
        cy.contains(text, {timeout: time}).should('not.exist')
    }; 

    //Клик по кнопкам циклом//
    static elem_cycle_click(...elements) {
        cy.get('.o_loading').should('not.be.visible');
        cy.wait(500)
        elements.forEach(e => cy.get(e).click().get('.o_loading')
        .should('not.be.visible').wait(500))
     };

    //Подождать загрузку и перезагрузить страницу//
    static reload() {
        cy.get('.o_loading').should('not.be.visible');
        cy.reload()
    };  

    //Клик по кнопкам циклом c xpath//
    static xpath_elem_cycle_click(...elements) {
        cy.get('.o_loading').should('not.be.visible');
        cy.wait(500)
        elements.forEach(e => cy.xpath(e).click().get('.o_loading')
        .should('not.be.visible').wait(500))
     };
}
