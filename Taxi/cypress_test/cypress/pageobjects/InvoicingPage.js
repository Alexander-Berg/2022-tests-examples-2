import {AuthPageLocators, BasePageLocators,AgrementsPageLocators,VendorsPageLocators, InvoicPageLoc, AutoordPageLocators,PurInstPageLocators, OrdersPageLocators, WarePageLocators} from './LocatorsPage'
import { HomePage } from './HomePage'
import { PurOrdersPage } from './OrdersPage'



export class InvoicingPage {
    
    static InvoicingAuth() {
        HomePage.login()
        HomePage.elem_cycle_click(BasePageLocators.MENU_BTN,InvoicPageLoc.INVOICING_BTN)// Invoicing
    };

    static InvoicingAuth_N(login,password) {
        HomePage.login_n(login,password)
        HomePage.elem_cycle_click(BasePageLocators.MENU_BTN,InvoicPageLoc.INVOICING_BTN)// Invoicing c выбором юзеров
    };

    static InvoisingTaxNotValidate(name) {
        InvoicingPage.InvoicingAuth()
        HomePage.elem_cycle_click(InvoicPageLoc.INVOIC_VEND_BTN,InvoicPageLoc.INVOIC_PRODUCT_BTN,InvoicPageLoc.INVOIC_REMOVE_BTN)
        HomePage.elem_cycle_click(InvoicPageLoc.INVOIC_FILTER_BTN)
        HomePage.contains_click('a',InvoicPageLoc.INVOIC_TO_VAL_BTN)
        HomePage.xpath_clicks_on_the_button(InvoicPageLoc.INVOIC_PRODUCT1_XP)
        HomePage.elem_cycle_click(InvoicPageLoc.INVOIC_TAX_VAL_DEN_BTN)
        HomePage.element_cycle('The tax for product [178007]')
        HomePage.elem_cycle_click(BasePageLocators.MENU_BTN,BasePageLocators.PURCHASE_BTN,VendorsPageLocators.VEND1_BTN,AgrementsPageLocators.PURAGR_BTN)
        HomePage.contains_click('td',name)
        HomePage.element_cycle('Tax Rate 20.0 for product [178007]')
    };

    static InvoiTaxesEdit_0(name,tax) {
        InvoicingPage.InvoicingAuth()
        HomePage.elem_cycle_click(InvoicPageLoc.INVOIC_CONF_BTN,InvoicPageLoc.INVOIC_TAX_BTN,name)
        HomePage.elem_cycle_click(BasePageLocators.EDIT_BTN)
        HomePage.clicks_button_clear(InvoicPageLoc.INVOIC_AMOUNT_FLD,tax)
        HomePage.elem_cycle_click(AutoordPageLocators.SAVE_BTN)
        HomePage.element_cycle('Edit')
    };

    // Тест LT-144-1 Confirm и оплата билла - права админ
    static Bill_Confirm_144_1(name,number) {
        InvoicingPage.InvoicingAuth()
        HomePage.elem_cycle_click(InvoicPageLoc.INVOIC_VEND_BTN,InvoicPageLoc.INVOIC_BILL_BTN)
        HomePage.contains_click('td',name)
        HomePage.elem_cycle_click(BasePageLocators.EDIT_BTN)
        HomePage.xpath_find_click_and_fill_in(InvoicPageLoc.BILL_REF_FLD_XP,number)
        HomePage.elem_cycle_click(InvoicPageLoc.INVOIC_CONFIRM_BTN)
        HomePage.elem_cycle_click(InvoicPageLoc.INVOIC_MANY_CONF_BTN)
        HomePage.elem_cycle_click(InvoicPageLoc.INVOIC_REG_PAY_BTN)
        HomePage.elem_cycle_click(InvoicPageLoc.INVOIC_CREATE_PAY_BTN)
        HomePage.elem_cycle_click(InvoicPageLoc.NEW_BILL_BTN)
        HomePage.element_cycle('In Payment','Edit','Vendor Bill Created')
    };

    // Тест LT-144-2 Confirm и оплата билла - права бухгалтер
    static Bill_Confirm_144_2(login,password,name,number) {
        InvoicingPage.InvoicingAuth_N(login,password)
        HomePage.elem_cycle_click(InvoicPageLoc.INVOIC_VEND_BTN)
        HomePage.element_n(InvoicPageLoc.INVOIC_BILL_BTN,5000)
        HomePage.elem_cycle_click(InvoicPageLoc.INVOIC_BILL_BTN)
        HomePage.contains_click('td',name)
        HomePage.element_n(BasePageLocators.EDIT_BTN,5000)
        HomePage.elem_cycle_click(BasePageLocators.EDIT_BTN)
        HomePage.xpath_find_click_and_fill_in(InvoicPageLoc.BILL_REF_FLD_XP,number)
        HomePage.element_n(InvoicPageLoc.INVOIC_CONFIRM_BTN,5000)
        HomePage.elem_cycle_click(InvoicPageLoc.INVOIC_CONFIRM_BTN)
        HomePage.element_cycle('Ask another accountant to confirm.')
    };

    // Тест LT-144-3 Confirm и оплата билла утвержденного бухгалтером - права бухгалтер
    static Bill_Confirm_144_3(login,password,name) {
        InvoicingPage.InvoicingAuth_N(login,password)
        HomePage.elem_cycle_click(InvoicPageLoc.INVOIC_VEND_BTN,InvoicPageLoc.INVOIC_BILL_BTN)
        HomePage.contains_click('td',name)
        HomePage.elem_cycle_click(InvoicPageLoc.INVOIC_CONFIRM_BTN)
        HomePage.element_n(InvoicPageLoc.INVOIC_MANY_CONF_BTN,5000)
        HomePage.elem_cycle_click(InvoicPageLoc.INVOIC_MANY_CONF_BTN)
        HomePage.element_n(InvoicPageLoc.INVOIC_REG_PAY_BTN,5000)
        HomePage.elem_cycle_click(InvoicPageLoc.INVOIC_REG_PAY_BTN)
        HomePage.element_n(InvoicPageLoc.INVOIC_CREATE_PAY_BTN,5000)
        HomePage.elem_cycle_click(InvoicPageLoc.INVOIC_CREATE_PAY_BTN)
        HomePage.elem_cycle_click(InvoicPageLoc.NEW_BILL_BTN)
        HomePage.element_cycle('In Payment','Edit','Vendor Bill Created')
    };

    // Тест LT-124-1 Импорт копии ордера
    static Bill_Import_124_1(Reference,NAME_AGR,) {
        PurOrdersPage.PurOrdersAuth()
        HomePage.contains_click('td','PO101')
        HomePage.clicks_on_the_button(BasePageLocators.ACTION_BTN)
        HomePage.contains_click('a',InvoicPageLoc.CREATE_VEND_BILL_TXT)
        HomePage.element_n(InvoicPageLoc.INVOIC_CONFIRM_BTN,5000)
        HomePage.clicks_on_the_button(BasePageLocators.EDIT_BTN)
        HomePage.element_n_xp(InvoicPageLoc.BILL_REF_FLD_XP)
        HomePage.xpath_find_click_and_fill_in(InvoicPageLoc.BILL_REF_FLD_XP,Reference)
        HomePage.contains_click('span',InvoicPageLoc.IMP_FROM_EX_TXT)
        cy.get(AgrementsPageLocators.NAME_FILE_BTN).attachFile({ filePath: NAME_AGR});
        HomePage.contains_click('span',InvoicPageLoc.LOAD_LINE_FR_F_TXT)
        HomePage.text_n(InvoicPageLoc.CONF_CHANGE_TXT,1000)
        HomePage.contains_click('span',InvoicPageLoc.CONF_CHANGE_TXT)
        HomePage.not_text_n('Import FAQ',1000)
        HomePage.element_cycle('157.50','131.25','Bill lines from vendor')
    };

    // Тест LT-124-2 В билле изменили цену,количество,налог
    static Bill_Import_124_2(name,NAME_AGR,sum_untax,Total_sum,percent) {
        InvoicingPage.InvoicingAuth()
        HomePage.elem_cycle_click(InvoicPageLoc.INVOIC_VEND_BTN,InvoicPageLoc.INVOIC_BILL_BTN)
        HomePage.contains_click('td',name)
        HomePage.element_n(BasePageLocators.EDIT_BTN,5000)
        HomePage.contains_click('span',InvoicPageLoc.IMP_FROM_EX_TXT)
        cy.get(AgrementsPageLocators.NAME_FILE_BTN).attachFile({ filePath: NAME_AGR});
        HomePage.contains_click('span',InvoicPageLoc.LOAD_LINE_FR_F_TXT)
        HomePage.contains_click('span',InvoicPageLoc.CONF_CHANGE_TXT)
        HomePage.element_cycle(sum_untax,Total_sum,percent)
    };

    //Тест LT-124-4 Вводим неверную итоговую сумму в продукт
    static Bill_Import_124_4(name,NAME_AGR,error) {
        InvoicingPage.InvoicingAuth()
        HomePage.elem_cycle_click(InvoicPageLoc.INVOIC_VEND_BTN,InvoicPageLoc.INVOIC_BILL_BTN)
        HomePage.contains_click('td',name)
        HomePage.element_n(BasePageLocators.EDIT_BTN,5000)
        HomePage.contains_click('span',InvoicPageLoc.IMP_FROM_EX_TXT)
        cy.get(AgrementsPageLocators.NAME_FILE_BTN).attachFile({ filePath: NAME_AGR});
        HomePage.contains_click('span',InvoicPageLoc.LOAD_LINE_FR_F_TXT)
        HomePage.element_cycle(error)
    };

    // Тест LT-158-1 Группировка по коду
    static Bill_Group_158_1(Reference,NAME_AGR) {
        PurOrdersPage.PurOrdersAuth()
        HomePage.xpath_elem_cycle_click(InvoicPageLoc.CHECK_105,InvoicPageLoc.CHECK_106,InvoicPageLoc.CHECK_107)
        HomePage.clicks_on_the_button(BasePageLocators.ACTION_BTN)
        HomePage.contains_click('a',InvoicPageLoc.CREATE_VEND_BILL_TXT)
        HomePage.element_n(InvoicPageLoc.INVOIC_CONFIRM_BTN,5000)
        HomePage.clicks_on_the_button(BasePageLocators.EDIT_BTN)
        HomePage.xpath_find_click_and_fill_in(InvoicPageLoc.BILL_REF_FLD_XP,Reference)
        HomePage.elem_cycle_click(AutoordPageLocators.SAVE_BTN)
        HomePage.contains_click('span',InvoicPageLoc.IMP_FROM_EX_TXT)
        cy.get(AgrementsPageLocators.NAME_FILE_BTN).attachFile({ filePath: NAME_AGR});
        HomePage.contains_click('span',InvoicPageLoc.LOAD_LINE_FR_F_TXT)
        HomePage.text_n(InvoicPageLoc.CONF_CHANGE_TXT,1000)
        HomePage.contains_click('span',InvoicPageLoc.CONF_CHANGE_TXT)
        HomePage.not_text_n('Import FAQ',1000)
        HomePage.element_cycle('472.50','78.75','Bill lines from vendor')
    };

    // Тест LT-158-2 Удаление сгруппированного товара
    static Bill_Group_158_2(Reference,NAME_AGR) {
        PurOrdersPage.PurOrdersAuth()
        HomePage.xpath_elem_cycle_click(InvoicPageLoc.CHECK_108,InvoicPageLoc.CHECK_109,InvoicPageLoc.CHECK_110)
        HomePage.clicks_on_the_button(BasePageLocators.ACTION_BTN)
        HomePage.contains_click('a',InvoicPageLoc.CREATE_VEND_BILL_TXT)
        HomePage.element_n(InvoicPageLoc.INVOIC_CONFIRM_BTN,5000)
        HomePage.clicks_on_the_button(BasePageLocators.EDIT_BTN)
        HomePage.xpath_find_click_and_fill_in(InvoicPageLoc.BILL_REF_FLD_XP,Reference)
        HomePage.elem_cycle_click(AutoordPageLocators.SAVE_BTN)
        HomePage.contains_click('span',InvoicPageLoc.IMP_FROM_EX_TXT)
        cy.get(AgrementsPageLocators.NAME_FILE_BTN).attachFile({ filePath: NAME_AGR});
        HomePage.contains_click('span',InvoicPageLoc.LOAD_LINE_FR_F_TXT)
        HomePage.text_n(InvoicPageLoc.CONF_CHANGE_TXT,1000)
        HomePage.contains_click('span',InvoicPageLoc.CONF_CHANGE_TXT)
        HomePage.not_text_n('Import FAQ',1000)
        HomePage.element_cycle('378.00','63.00','Bill lines from vendor')
    };

    // Тест LT-188-1 Проверка что можно апрувнуть измененения в билле
    static Bill_Appruv_188_1(Reference) {
        PurOrdersPage.PurOrdersAuth()
        HomePage.xpath_elem_cycle_click(InvoicPageLoc.CHECK_102)
        HomePage.clicks_on_the_button(BasePageLocators.ACTION_BTN)
        HomePage.contains_click('a',InvoicPageLoc.CREATE_VEND_BILL_TXT)
        HomePage.element_n(InvoicPageLoc.INVOIC_CONFIRM_BTN,5000)
        HomePage.clicks_on_the_button(BasePageLocators.EDIT_BTN)
        HomePage.xpath_find_click_and_fill_in(InvoicPageLoc.BILL_REF_FLD_XP,Reference)
        HomePage.xpath_find_click_and_fill_in(InvoicPageLoc.BILL_PRICE_FLD_XP,'100')
        HomePage.xpath_find_click_and_fill_in(InvoicPageLoc.BILL_QUANT_FLD_XP,'100')
        HomePage.elem_cycle_click(AutoordPageLocators.SAVE_BTN)
        HomePage.xpath_clicks_on_the_button(InvoicPageLoc.CONFIRM_BTN_XP)
        HomePage.elem_cycle_click(BasePageLocators.MENU_BTN,InvoicPageLoc.INVOICING_BTN)
        HomePage.elem_cycle_click(InvoicPageLoc.INVOIC_VEND_BTN,InvoicPageLoc.INVOIC_BILL_BTN)
        HomePage.contains_click('td',Reference)
        HomePage.element_n_xp(InvoicPageLoc.APPRUV_BTN_XP,2000)
        HomePage.xpath_elem_cycle_click(InvoicPageLoc.APPRUV_BTN_XP)
        HomePage.xpath_elem_cycle_click(InvoicPageLoc.CHECK_APP_XP_188_1)
        HomePage.element_cycle("I'm confirmed the reason quantity with description")
    };

    // Тест LT-188-2 Проверка что можно апрувнуть измененения в билле под менеджером
    static Bill_Appruv_188_2(login,password,name) {
        InvoicingPage.InvoicingAuth_N(login,password)
        HomePage.elem_cycle_click(InvoicPageLoc.INVOIC_VEND_BTN)
        HomePage.element_n(InvoicPageLoc.INVOIC_BILL_BTN,5000)
        HomePage.elem_cycle_click(InvoicPageLoc.INVOIC_BILL_BTN)
        HomePage.contains_click('td',name)
        HomePage.element_n_xp(InvoicPageLoc.APPRUV_BTN_XP,2000)
        HomePage.xpath_elem_cycle_click(InvoicPageLoc.APPRUV_BTN_XP)
        HomePage.xpath_elem_cycle_click(InvoicPageLoc.CHECK_APP_XP_188_2)
        HomePage.element_cycle("I'm confirmed the reason")
    };

    // Тест LT-188-3 Проверка что можно апрувнуть измененения в билле из файла 
    static Bill_Appruv_188_3(Reference,NAME_AGR) {
        PurOrdersPage.PurOrdersAuth()
        HomePage.xpath_elem_cycle_click(InvoicPageLoc.CHECK_101)
        HomePage.clicks_on_the_button(BasePageLocators.ACTION_BTN)
        HomePage.contains_click('a',InvoicPageLoc.CREATE_VEND_BILL_TXT)
        HomePage.element_n(InvoicPageLoc.INVOIC_CONFIRM_BTN,5000)
        HomePage.clicks_on_the_button(BasePageLocators.EDIT_BTN)
        HomePage.xpath_find_click_and_fill_in(InvoicPageLoc.BILL_REF_FLD_XP,Reference)
        HomePage.contains_click('span',InvoicPageLoc.IMP_FROM_EX_TXT)
        cy.get(AgrementsPageLocators.NAME_FILE_BTN).attachFile({ filePath: NAME_AGR});
        HomePage.contains_click('span',InvoicPageLoc.LOAD_LINE_FR_F_TXT)
        HomePage.text_n(InvoicPageLoc.CONF_CHANGE_TXT,1000)
        HomePage.contains_click('span',InvoicPageLoc.CONF_CHANGE_TXT)
        HomePage.elem_cycle_click(AutoordPageLocators.SAVE_BTN)
        HomePage.xpath_clicks_on_the_button(InvoicPageLoc.CONFIRM_BTN_XP)
        HomePage.element_cycle("Personal approval")
    };
}
