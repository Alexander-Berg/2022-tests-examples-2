import {AuthPageLocators, BasePageLocators,AgrementsPageLocators,VendorsPageLocators, AutoordPageLocators} from './LocatorsPage'
import { HomePage } from './HomePage'


export class AgremPage {
    
    static AgremAuth() {
        HomePage.login()
        HomePage.clicks_on_the_button(BasePageLocators.MENU_BTN)
        HomePage.clicks_on_the_button(BasePageLocators.PURCHASE_BTN)
        HomePage.clicks_on_the_button(VendorsPageLocators.VEND1_BTN) // vendor 1
        HomePage.clicks_on_the_button(AgrementsPageLocators.PURAGR_BTN) // Purchase Agreements
        cy.wait(1000)
        HomePage.not_odoo_error()
    };

    //Функция апрувит все товары в агрименте
    static APP_ALL() {
        cy.wait(1000)
        HomePage.elem_cycle_click(VendorsPageLocators.VEND1_BTN,AgrementsPageLocators.PURAGR_LINES_BTN)
        HomePage.xpath_elem_cycle_click(AgrementsPageLocators.ALL_AGR_LIN_XP,AgrementsPageLocators.APP_PRICE_XP)
        HomePage.xpath_elem_cycle_click(AgrementsPageLocators.ALL_AGR_LIN_XP,AgrementsPageLocators.APP_TAXES_XP)
        HomePage.not_odoo_error()
    };

    static OPEN_AGR() {
        cy.wait(1000)
        HomePage.clicks_on_the_button(VendorsPageLocators.VEND1_BTN)
        HomePage.xpath_elem_cycle_click(AgrementsPageLocators.PURAG_XP)
        HomePage.xpath_elem_cycle_click(AgrementsPageLocators.ONE_AGR_XP)
        HomePage.not_odoo_error()
    };

    // Первое создание Purchase Agreements при всех обязательных значениях
    static AgremCreate(name,Col,Code) {
        AgremPage.AgremAuth()
        HomePage.clicks_on_the_button(AgrementsPageLocators.CREATE_PUAG_BTN)//create
        HomePage.clicks_button_enter(AgrementsPageLocators.VENDOR_PUAG_FLD)//поле вендора
        HomePage.two_clicks_in_the_fields(AgrementsPageLocators.ADD_A_LINETXT_BTN,AgrementsPageLocators.PRODUCT_FLD)//Выбираем выбор продукта и поле продукта
        HomePage.enter_click()
        HomePage.find_click_and_fill_in(AgrementsPageLocators.UNIT_PR_FLD,Col)// Вводим цену
        HomePage.clicks_button_enter(AgrementsPageLocators.VEND_TAX_FLD)//Выбираем % ставку
        HomePage.click_write_enter(AgrementsPageLocators.START_D_FLD,HomePage.date_local_n(4))
        HomePage.find_click_and_fill_in(AgrementsPageLocators.VEND_PRCODE_FLD,Code)// вводим код
        HomePage.two_clicks_in_the_fields(AgrementsPageLocators.LAV_AV_BTN,AgrementsPageLocators.ADD_A_LINE_BTN)//Выбираем геометку
        HomePage.elem_cycle_click(AgrementsPageLocators.GEO_UK_BTN)
        HomePage.elem_cycle_click(AgrementsPageLocators.SAVE_BTN,AgrementsPageLocators.CONFIRM_BTN)//Сохраняем 
        HomePage.element_cycle('Edit',name,Col,Code)
        AgremPage.APP_ALL()
        HomePage.not_odoo_error()
    };

    // Создание агримента через файл.Все данные валидные
    static Agrement_Create_xls(el_1,el_2,el_3,NAME_AGR) {
        AgremPage.AgremAuth()
        HomePage.clicks_on_the_button(AgrementsPageLocators.CREATE_PUAG_BTN)//create
        HomePage.clicks_button_enter(AgrementsPageLocators.VENDOR_PUAG_FLD)//поле вендора
        HomePage.elem_cycle_click(AgrementsPageLocators.OK_BTN,AgrementsPageLocators.IMP_LIN_BTN)
        cy.get(AgrementsPageLocators.NAME_FILE_BTN).attachFile({ filePath: NAME_AGR});
        HomePage.clicks_on_the_button(AgrementsPageLocators.LOAD_F_BTN)
        HomePage.elem_cycle_click(AgrementsPageLocators.SAVE_BTN,AgrementsPageLocators.CONFIRM_BTN)//Сохраняем
        HomePage.element_cycle('Edit',el_1,el_2,el_3)
        HomePage.not_odoo_error() 
    };

    // Апрувим цены в агрименте,ставим геотег
    static AgremEdit_1(name,geo) {
        AgremPage.AgremAuth()
        AgremPage.APP_ALL()
        AgremPage.OPEN_AGR()
        HomePage.elem_cycle_click(AgrementsPageLocators.LAV_AV_BTN)
        HomePage.clicks_on_the_button(BasePageLocators.EDIT_BTN)
        HomePage.elem_cycle_click(AgrementsPageLocators.ADD_A_LINE_BTN,AgrementsPageLocators.GEO_UK_BTN,AgrementsPageLocators.SAVE_BTN)
        HomePage.element_cycle('Edit',name,geo)
        HomePage.not_odoo_error() 
    };

    // LT-180-1 Создание агримента через файл.Дубль товара в агрименте
    static Agrement_Create_xls_duble(el_1,el_2,NAME_AGR) {
        AgremPage.AgremAuth()
        HomePage.clicks_on_the_button(AgrementsPageLocators.CREATE_PUAG_BTN)//create
        HomePage.clicks_button_enter(AgrementsPageLocators.VENDOR_PUAG_FLD)//поле вендора
        HomePage.elem_cycle_click(AgrementsPageLocators.OK_BTN,AgrementsPageLocators.IMP_LIN_BTN)
        cy.get(AgrementsPageLocators.NAME_FILE_BTN).attachFile({ filePath: NAME_AGR});
        HomePage.clicks_on_the_button(AgrementsPageLocators.LOAD_F_BTN)
        HomePage.elem_cycle_click(AgrementsPageLocators.SAVE_BTN,AgrementsPageLocators.CONFIRM_BTN)//Сохраняем
        AgremPage.APP_ALL()
        AgremPage.OPEN_AGR()
        HomePage.element_cycle('Edit',el_1,el_2)
        HomePage.not_cont_text('Еда2')
        HomePage.not_odoo_error()
    };

    // LT-180-2 'Создание Purchase Agreements при пустой ставке в файле'
    static Agrement_Create_180_2(el_1,el_2,NAME_AGR) {
        AgremPage.AgremAuth()
        HomePage.clicks_on_the_button(AgrementsPageLocators.CREATE_PUAG_BTN)//create
        HomePage.clicks_button_enter(AgrementsPageLocators.VENDOR_PUAG_FLD)//поле вендора
        HomePage.elem_cycle_click(AgrementsPageLocators.OK_BTN,AgrementsPageLocators.IMP_LIN_BTN)
        cy.get(AgrementsPageLocators.NAME_FILE_BTN).attachFile({ filePath: NAME_AGR});
        HomePage.clicks_on_the_button(AgrementsPageLocators.LOAD_F_BTN)
        HomePage.element_cycle(el_1,el_2)
        HomePage.not_odoo_error()
    };

    // 390-1 Создание агримента через файл.Активные и не активные строки
    static Agrement_Active_and_not_active(el_1,el_2,el_3,NAME_AGR) {
        AgremPage.AgremAuth()
        HomePage.clicks_on_the_button(AgrementsPageLocators.CREATE_PUAG_BTN)//create
        HomePage.clicks_button_enter(AgrementsPageLocators.VENDOR_PUAG_FLD)//поле вендора
        HomePage.elem_cycle_click(AgrementsPageLocators.OK_BTN,AgrementsPageLocators.IMP_LIN_BTN)
        cy.get(AgrementsPageLocators.NAME_FILE_BTN).attachFile({ filePath: NAME_AGR});
        HomePage.clicks_on_the_button(AgrementsPageLocators.LOAD_F_BTN)
        HomePage.elem_cycle_click(AgrementsPageLocators.SAVE_BTN,AgrementsPageLocators.CONFIRM_BTN)//Сохраняем
        HomePage.element_cycle(el_1,el_2,el_3)
        cy.get(AgrementsPageLocators.STR1).should('be.checked')
        cy.get(AgrementsPageLocators.STR4).should('not.be.checked')
        HomePage.not_odoo_error()
    };


    // 390-2-3 Изменение цен в существующем агрименте
    static AgremEdit_390_2(name,NAME_AGR,el_1,el_2,checkbox1,checkbox2,meaning) {
        AgremPage.AgremAuth()
        HomePage.contains_click('td',name)
        HomePage.elem_cycle_click(AgrementsPageLocators.IMP_LIN_BTN)
        cy.get(AgrementsPageLocators.NAME_FILE_BTN).attachFile({ filePath: NAME_AGR});
        HomePage.clicks_on_the_button(AgrementsPageLocators.LOAD_F_BTN)
        AgremPage.APP_ALL()
        AgremPage.OPEN_AGR()
        HomePage.element_cycle('Edit',name,el_1,el_2) 
        cy.get(checkbox1).should(meaning)
        cy.get(checkbox2).should(meaning)
        HomePage.not_odoo_error()
    };

    // 390-4 Изменение активности строк в существующем агрименте
    static AgremEdit_390_4(name,NAME_AGR) {
        AgremPage.AgremAuth()
        HomePage.contains_click('td',name)
        HomePage.elem_cycle_click(AgrementsPageLocators.IMP_LIN_BTN)
        cy.get(AgrementsPageLocators.NAME_FILE_BTN).attachFile({ filePath: NAME_AGR});
        HomePage.clicks_on_the_button(AgrementsPageLocators.LOAD_F_BTN)
        AgremPage.APP_ALL()
        AgremPage.OPEN_AGR()
        cy.get(AgrementsPageLocators.STR1).should('not.be.checked')
        cy.get(AgrementsPageLocators.STR2).should('not.be.checked')
        HomePage.not_odoo_error()
    };

    // LT-92-1 Создание агримента через файл.Есть нулевые ставки налога
    static Agrement_Create_xls_0taxes(NAME_AGR,error) {
        AgremPage.AgremAuth()
        HomePage.clicks_on_the_button(AgrementsPageLocators.CREATE_PUAG_BTN)//create
        HomePage.clicks_button_enter(AgrementsPageLocators.VENDOR_PUAG_FLD)//поле вендора
        HomePage.elem_cycle_click(AgrementsPageLocators.OK_BTN,AgrementsPageLocators.IMP_LIN_BTN)
        cy.get(AgrementsPageLocators.NAME_FILE_BTN).attachFile({ filePath: NAME_AGR});
        HomePage.clicks_on_the_button(AgrementsPageLocators.LOAD_F_BTN)
        HomePage.element_cycle(error)
        HomePage.not_odoo_error() 
    };


    // LT-92-3 Создание агримента через файл.Есть нулевые ставки налога.Ставка должна быть принята
    static Agrement_Create_xls_0taxes_True(NAME_AGR,error) {
        AgremPage.Agrement_Create_xls_0taxes(NAME_AGR,error)
        HomePage.elem_cycle_click(AgrementsPageLocators.SAVE_BTN,AgrementsPageLocators.CONFIRM_BTN)
        HomePage.element_cycle('0%','New Quotation')
        HomePage.not_odoo_error()
    };

    // LT-547-1 Проверка отсутствия поля create в OEBS контракт
    static Agrem_Not_OEBS_Create(NAME_AGR) {
        AgremPage.AgremAuth()
        HomePage.contains_click('td',NAME_AGR)
        HomePage.elem_cycle_click(BasePageLocators.EDIT_BTN,AgrementsPageLocators.OEBS_CONT_FLD)
        HomePage.element_cycle('Save','No search results.')
        HomePage.not_element('body > div.ui-helper-hidden-accessible > div:nth-child(2)')
        HomePage.not_odoo_error()
    };
}

