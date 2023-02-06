import {AuthPageLocators, BasePageLocators,SettingsPageLocators,VendorsPageLocators,AgrementsPageLocators,InvoicPageLoc,AutoordPageLocators, TeamsPageLocators} from './LocatorsPage'
import { HomePage } from './HomePage'


export class SettingsPage {
    
    static SettAuth() {
        HomePage.login()
        HomePage.clicks_on_the_button(BasePageLocators.MENU_BTN)
        HomePage.clicks_on_the_button(SettingsPageLocators.SETTINGS_BTN)
        HomePage.clicks_on_the_button(SettingsPageLocators.MAN_USER_TXT) // Manage Users
        cy.wait(1000)
        };

    static SettAuth_n(User,pass) {
        HomePage.login_n(User,pass)
        // HomePage.xpath_clicks_on_the_button(BasePageLocators.OK_XP_BTN)
        HomePage.elem_cycle_click(BasePageLocators.MENU_BTN)
        };

    // LT_191_1 Создаем нового пользователя
    static CREATE_USER_191(name,email) {
        SettingsPage.SettAuth()
        HomePage.clicks_on_the_button(BasePageLocators.CREATE_BTN)
        HomePage.find_click_and_fill_in(SettingsPageLocators.NAME_FLD,name) // Name
        HomePage.find_click_and_fill_in(SettingsPageLocators.LOGIN_FLD,email) // Login
        HomePage.elem_cycle_click(SettingsPageLocators.USER_ROLE_SEL)
        HomePage.xpath_clicks_on_the_button(SettingsPageLocators.CATMAN_XP)
        HomePage.clicks_on_the_button(SettingsPageLocators.SAVE_BTN) //save
        HomePage.xpath_elem_cycle_click(BasePageLocators.ACTION_XP_BTN,SettingsPageLocators.CHA_PASS_XP) // action,задать пароль
        HomePage.find_click_and_fill_in(SettingsPageLocators.NEW_PASS_FLD,BasePageLocators.PASS) // пароль
        HomePage.clicks_on_the_button(SettingsPageLocators.SAVE_PASSW_BTN) //сохранить пароль
        cy.wait(1000) //нужно дать время на загрузку ордера 
        };

    // LT-130 Автотесты на права read only
    static SettAuthReadOnly(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.contains_click('span','OpenAPI')
        HomePage.not_element(BasePageLocators.CREATE_BTN)
        HomePage.cont_text('Intergrations')
        HomePage.elem_cycle_click(BasePageLocators.MENU_BTN)
        HomePage.contains_click('span','Purchase')
        HomePage.not_element(BasePageLocators.CREATE_BTN)
        HomePage.elem_cycle_click(VendorsPageLocators.VEND1_BTN,AgrementsPageLocators.PURAGR_BTN)
        HomePage.not_element(BasePageLocators.CREATE_BTN)
        HomePage.elem_cycle_click(AutoordPageLocators.AUTOORD_BTN,AutoordPageLocators.DELIV_SH_BTN)
        HomePage.not_element(BasePageLocators.CREATE_BTN)
        HomePage.elem_cycle_click(TeamsPageLocators.TEAMS_BTN)
        HomePage.not_element(BasePageLocators.CREATE_BTN)
        HomePage.elem_cycle_click(BasePageLocators.MENU_BTN)
        HomePage.contains_click('span','Invoicing')
        HomePage.not_element(BasePageLocators.CREATE_BTN)
        HomePage.elem_cycle_click(InvoicPageLoc.INVOIC_VEND_BTN,InvoicPageLoc.INVOIC_BILL_BTN)
        HomePage.not_element(BasePageLocators.CREATE_BTN)
        HomePage.elem_cycle_click(BasePageLocators.MENU_BTN)
        HomePage.contains_click('span','Discuss')
        HomePage.cont_text('Inbox')
        HomePage.elem_cycle_click(BasePageLocators.MENU_BTN)
        HomePage.contains_click('span','Inventory')
        HomePage.cont_text('Inventory Overview')
        HomePage.elem_cycle_click(BasePageLocators.MENU_BTN)
        HomePage.contains_click('span','Dashboards')
        HomePage.cont_text('My Dashboard')
        HomePage.elem_cycle_click(BasePageLocators.MENU_BTN)
        HomePage.contains_click('span','Sales')
        HomePage.cont_text('Quotations')
        };
}
