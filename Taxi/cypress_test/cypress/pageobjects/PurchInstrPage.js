import {AuthPageLocators, BasePageLocators,PurInstPageLocators,VendorsPageLocators,AgrementsPageLocators, AutoordPageLocators} from './LocatorsPage'
import { HomePage } from './HomePage'

export class PurInstPage {
    
    //Авторизация
    static PurInAuth() {
        HomePage.login()
        HomePage.elem_cycle_click(BasePageLocators.MENU_BTN,BasePageLocators.PURCHASE_BTN,PurInstPageLocators.PUR_INSR_BTN)// Purchase Instruments
        };

    // Создание трансфера с количеством товара меньше чем на складе
    static Create_TR(NAME_AGR,War_Out,War_IN) {
        PurInstPage.PurInAuth()
        HomePage.clicks_on_the_button(PurInstPageLocators.IMP_TR_BTN) // Import Transfers
        cy.get(AgrementsPageLocators.NAME_FILE_BTN).attachFile({ filePath: NAME_AGR});
        HomePage.clicks_on_the_button(AgrementsPageLocators.LOAD_F_BTN)
        HomePage.element_cycle('Create',War_Out,War_IN,'Draft')
        };

    // Создание трансфера с количеством товара больше чем на складе
    static Create_TR_MAX(NAME_AGR,War_Out,War_IN) {
        PurInstPage.PurInAuth()
        HomePage.clicks_on_the_button(PurInstPageLocators.IMP_TR_BTN) // Import Transfers
        cy.get(AgrementsPageLocators.NAME_FILE_BTN).attachFile({ filePath: NAME_AGR});
        HomePage.clicks_on_the_button(AgrementsPageLocators.LOAD_F_BTN)
        HomePage.element_cycle('Create',War_Out,War_IN,'Draft')
        HomePage.contains_click('span',War_IN)
        HomePage.contains_click('span',BasePageLocators.Che_PLQTY)
        HomePage.element_cycle('Create',War_Out,War_IN,'Draft')
        HomePage.reload()
        HomePage.element_cycle('Edit','Changes in ordered qty 178002: 600000->')
        };

    // Создание ордера с валидными значениями
    static Create_PUR_OR(NAME_AGR,total) {
        PurInstPage.PurInAuth()
        HomePage.clicks_on_the_button(PurInstPageLocators.IMP_PUR_OR_BTN) // Import order
        cy.get(AgrementsPageLocators.NAME_FILE_BTN).attachFile({ filePath: NAME_AGR});
        HomePage.clicks_on_the_button(PurInstPageLocators.LOAD_BTN)
        HomePage.element_cycle(total)
        };

    // Тест LT-57-3 Создание Import Orders с датой большк чем год от сегодня
    static Create_PUR_OR_LT_57_3_4(NAME_AGR,error) {
        PurInstPage.PurInAuth()
        HomePage.clicks_on_the_button(PurInstPageLocators.IMP_PUR_OR_BTN) // Import order
        cy.get(AgrementsPageLocators.NAME_FILE_BTN).attachFile({ filePath: NAME_AGR});
        HomePage.clicks_on_the_button(PurInstPageLocators.LOAD_BTN)
        HomePage.element_cycle(error)
        };

    // Создание ордера из файла с разными датами
    static Create_PUR_OR_N(NAME_AGR,total) {
        PurInstPage.PurInAuth()
        HomePage.clicks_on_the_button(PurInstPageLocators.IMP_PUR_OR_BTN) // Import order
        cy.get(AgrementsPageLocators.NAME_FILE_BTN).attachFile({ filePath: NAME_AGR});
        HomePage.clicks_on_the_button(PurInstPageLocators.LOAD_BTN)
        HomePage.element_cycle(total)
        };

    // Создание Import Schedule из файла с валидными значениями
    static Create_IMP_SCH(NAME_AGR,n1,n2,n3,n4) {
        PurInstPage.PurInAuth()
        HomePage.clicks_on_the_button(PurInstPageLocators.IMP_SCH_BTN) // Import order
        cy.get(AgrementsPageLocators.NAME_FILE_BTN).attachFile({ filePath: NAME_AGR});
        HomePage.elem_cycle_click(PurInstPageLocators.LOAD_BTNSC,AutoordPageLocators.AUTOORD_BTN,AutoordPageLocators.DELIV_SH_BTN)
        HomePage.element_cycle('Create',n1,n2,n3,n4)
        };



    }

    
    