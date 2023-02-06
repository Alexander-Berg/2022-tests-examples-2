import {AuthPageLocators, BasePageLocators,OrdersPageLocators,TeamsPageLocators,AgrementsPageLocators,VendorsPageLocators} from './LocatorsPage'
import { HomePage } from './HomePage'
import { AgremPage } from './AgremPage'


export class TeamsPage {
    
    static TeamsAuth() {
        HomePage.login()
        HomePage.elem_cycle_click(BasePageLocators.MENU_BTN,BasePageLocators.PURCHASE_BTN,TeamsPageLocators.TEAMS_BTN)
        };

    static TeamsAuth_n(User,pass) {
        HomePage.login_n(User,pass)
        HomePage.elem_cycle_click(BasePageLocators.MENU_BTN,BasePageLocators.PURCHASE_BTN)
        };

    //создание группы
    static TeamsCreate(TEXT,LID,USER) {
        TeamsPage.TeamsAuth()
        HomePage.clicks_on_the_button(OrdersPageLocators.CREATE_ORD_BTN) //create
        HomePage.find_click_and_fill_in(TeamsPageLocators.SAL_TEA_FLD,TEXT)
        HomePage.click_write_enter(TeamsPageLocators.TEAM_LID_FLD,LID)
        HomePage.contains_click('a',TeamsPageLocators.AD_MEM_TXT)
        HomePage.clicks_on_the_button(TeamsPageLocators.USER_FLD)
        HomePage.contains_click('a',USER)
        HomePage.clicks_on_the_button(OrdersPageLocators.Save_ORD_BTN) //Save
        HomePage.element_cycle(TEXT,USER)
        };

    //редактированип группы,удаление пользователя
    static TeamsEdit(TEAMS,USER) {
        TeamsPage.TeamsAuth()
        HomePage.contains_click('td',TEAMS)
        HomePage.elem_cycle_click(BasePageLocators.EDIT_BTN,TeamsPageLocators.DEL_BTN,OrdersPageLocators.Save_ORD_BTN)
        HomePage.not_cont_text(USER)  
        };

    //создание группы Purchase1
    static TeamsCreate_Purchase(TEXT,USER1,USER2,USER3) {
        TeamsPage.TeamsAuth()
        HomePage.clicks_on_the_button(OrdersPageLocators.CREATE_ORD_BTN) //create
        HomePage.find_click_and_fill_in(TeamsPageLocators.SAL_TEA_FLD,TEXT)
        HomePage.click_write_enter(TeamsPageLocators.TEAM_LID_FLD,USER1)
        HomePage.find_click_and_fill_in_text('a',TeamsPageLocators.AD_MEM_TXT,USER2)
        HomePage.clicks_on_the_button(TeamsPageLocators.VOICE_BTN1)
        HomePage.find_click_and_fill_in_text('a',TeamsPageLocators.AD_MEM_TXT,USER3)
        HomePage.clicks_on_the_button(OrdersPageLocators.Save_ORD_BTN) //Save
        HomePage.element_cycle(TEXT,USER1,USER2,USER3,'Edit')
        };

    //Смена группы у вендора
    static TEAM_VEND_ADD(User,pass,NAME_VEND,NAME_TEAM) {
        TeamsPage.TeamsAuth_n(User,pass)
        HomePage.elem_cycle_click(VendorsPageLocators.VEND1_BTN,VendorsPageLocators.VEND2_BTN)
        HomePage.contains_click('span',NAME_VEND)
        HomePage.elem_cycle_click(BasePageLocators.EDIT_BTN,VendorsPageLocators.SP_BTN)
        HomePage.clicks_button_clear_enter(VendorsPageLocators.Team_FLD,NAME_TEAM)
        HomePage.clicks_on_the_button(OrdersPageLocators.Save_ORD_BTN) //Save
        };
    
    //Создание под User1 агримента апрув прайс
    static TEAM_AGR_USER1(User,pass,NAME_VEND,NAME_AGR) {
        TeamsPage.TeamsAuth_n(User,pass)
        HomePage.elem_cycle_click(VendorsPageLocators.VEND1_BTN,AgrementsPageLocators.PURAGR_BTN,AgrementsPageLocators.CREATE_PUAG_BTN)
        HomePage.click_write_enter(AgrementsPageLocators.VENDOR_PUAG_FLD,NAME_VEND)
        HomePage.elem_cycle_click(AgrementsPageLocators.IMP_LIN_BTN)
        cy.get(AgrementsPageLocators.NAME_FILE_BTN).attachFile({ filePath: NAME_AGR});
        HomePage.clicks_on_the_button(AgrementsPageLocators.LOAD_F_BTN)
        HomePage.two_clicks_in_the_fields(AgrementsPageLocators.SAVE_BTN,AgrementsPageLocators.CONFIRM_BTN)//Сохраняем
        HomePage.element_cycle('Edit',NAME_VEND,' Price list attach ')
        };
        
    //Апрувим прайс под User2
    static TeamsApprov_price(User,pass) {
        TeamsPage.TeamsAuth_n(User,pass)
        HomePage.elem_cycle_click(VendorsPageLocators.VEND1_BTN,AgrementsPageLocators.PURAGR_LINES_BTN)
        AgremPage.APP_ALL()
        HomePage.clicks_on_the_button(AgrementsPageLocators.TABL_APPR_BTN)
        cy.get(AgrementsPageLocators.PROD1APP).should('be.checked')
        cy.get(AgrementsPageLocators.PROD2APP).should('be.checked')
        cy.get(AgrementsPageLocators.PROD3APP).should('be.checked')
        };

    //Новые цены под User3
    static NEW_price(User,pass,name,NAME_AGR,el1,el2,el3) {
        TeamsPage.TeamsAuth_n(User,pass)
        HomePage.elem_cycle_click(VendorsPageLocators.VEND1_BTN,AgrementsPageLocators.PURAGR_BTN)
        HomePage.contains_click('span',name)
        HomePage.elem_cycle_click(AgrementsPageLocators.IMP_LIN_BTN)
        cy.get(AgrementsPageLocators.NAME_FILE_BTN).attachFile({ filePath: NAME_AGR});
        HomePage.clicks_on_the_button(AgrementsPageLocators.LOAD_F_BTN)
        HomePage.element_cycle('Price list attach','Edit',el1,el2,el3)
        };

    //Апрувим прайс под User2
    static TeamsApprov_price2(User,pass,selector) {
        TeamsPage.TeamsAuth_n(User,pass)
        HomePage.elem_cycle_click(VendorsPageLocators.VEND1_BTN,AgrementsPageLocators.PURAGR_LINES_BTN,AgrementsPageLocators.PROD5)
        HomePage.clicks_on_the_button(AgrementsPageLocators.APP_PR_BTN)
        cy.reload()
        cy.get(selector).should('be.checked')
        };

    //Апрувим прайс под User1
    static TeamsApprov_price3(User,pass) {
        TeamsPage.TeamsAuth_n(User,pass)
        HomePage.elem_cycle_click(VendorsPageLocators.VEND1_BTN,AgrementsPageLocators.PURAGR_LINES_BTN)
        HomePage.elem_cycle_click(AgrementsPageLocators.PROD5,AgrementsPageLocators.PROD6,AgrementsPageLocators.PROD7)
        HomePage.clicks_on_the_button(AgrementsPageLocators.APP_PR_BTN)
        };

    //Проверяем что User3 не видит кнопки approve price
    static TeamsNot_Approv_price(User,pass) {
        TeamsPage.TeamsAuth_n(User,pass)
        HomePage.elem_cycle_click(VendorsPageLocators.VEND1_BTN,AgrementsPageLocators.PURAGR_LINES_BTN)
        HomePage.not_element(AgrementsPageLocators.APP_PR_BTN)
        };

    //Проверяем что User2 и User3 не могут редактировать группу
    static TeamsNot_Edit(User,pass,teams,User2,pass2) {
        TeamsPage.TeamsAuth_n(User,pass)
        HomePage.elem_cycle_click(OrdersPageLocators.ORDERS_BTN,TeamsPageLocators.TEAMS_BTN)
        HomePage.contains_click('div',teams)
        HomePage.not_element(BasePageLocators.EDIT_BTN)
        TeamsPage.TeamsAuth_n(User2,pass2)
        HomePage.elem_cycle_click(OrdersPageLocators.ORDERS_BTN,TeamsPageLocators.TEAMS_BTN)
        HomePage.contains_click('div',teams)
        HomePage.not_element(BasePageLocators.EDIT_BTN)
    };

    //Потеря прав лидером на редактирование группы после смены лидера.
    static TeamsNot_Edit_Lid(User,pass,teams,LID) {
        TeamsPage.TeamsAuth_n(User,pass)
        HomePage.elem_cycle_click(OrdersPageLocators.ORDERS_BTN,TeamsPageLocators.TEAMS_BTN)
        HomePage.contains_click('div',teams)
        HomePage.clicks_on_the_button(BasePageLocators.EDIT_BTN)
        HomePage.clicks_button_clear_enter(TeamsPageLocators.TEAM_LID_FLD,LID)
        HomePage.clicks_on_the_button(OrdersPageLocators.Save_ORD_BTN) //Save
        cy.reload()
        HomePage.not_element(BasePageLocators.EDIT_BTN)
    };

    //создание группы Purchase2-проверка что user может быть только в одной группе
    static TeamsCreate_Purchase2(User,pass,TEXT,USER2,teams) {
        TeamsPage.TeamsAuth_n(User,pass)
        HomePage.elem_cycle_click(TeamsPageLocators.TEAMS_BTN,OrdersPageLocators.CREATE_ORD_BTN)
        HomePage.find_click_and_fill_in(TeamsPageLocators.SAL_TEA_FLD,TEXT)
        HomePage.click_write_enter(TeamsPageLocators.TEAM_LID_FLD,USER2)
        HomePage.find_click_and_fill_in_text('a',TeamsPageLocators.AD_MEM_TXT,USER2)
        HomePage.elem_cycle_click(OrdersPageLocators.Save_ORD_BTN,TeamsPageLocators.TEAMS_BTN)
        HomePage.clicks_on_the_button(teams)
        HomePage.not_cont_text(USER2)
    };
}
