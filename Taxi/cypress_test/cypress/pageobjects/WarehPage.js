import {AuthPageLocators, BasePageLocators, WarePageLocators} from './LocatorsPage'
import { HomePage } from './HomePage'
import { time } from 'console'


export class WarehausesPage {
    
    static WarehAuthYAMS() {
        HomePage.login()
        HomePage.elem_cycle_click(BasePageLocators.MENU_BTN,BasePageLocators.YAWMS_BTN,BasePageLocators.SC_ACT_BTN)
        HomePage.xpath_elem_cycle_click(BasePageLocators.PROD_WMS_XP,BasePageLocators.RUN_MAN_BTN_XP)
        cy.wait(30000)
        HomePage.reload()
        HomePage.xpath_elem_cycle_click(BasePageLocators.WAREH_WMS_XP,BasePageLocators.RUN_MAN_BTN_XP)
        // HomePage.element_n(BasePageLocators.SPIN,300000)
        // HomePage.not_element_n(BasePageLocators.SPIN,300000)
        HomePage.elem_cycle_click(BasePageLocators.AUTOTEST_BTN,BasePageLocators.CREAT_USER_BTN)
        cy.wait(1000)
        HomePage.not_odoo_error()
        };
    
    static WarehAuth() {
        HomePage.login()
        HomePage.elem_cycle_click(BasePageLocators.MENU_BTN,BasePageLocators.PURCHASE_BTN,WarePageLocators.WARE_BTN)// warehouses
        HomePage.not_odoo_error()
        };

    // Редактирование Английского склада. Добавление геометок
    static Wareh_GEO_ADD(GEO,geo,assortment) {
        WarehausesPage.WarehAuth()
        HomePage.elem_cycle_click(WarePageLocators.DELI_BTN,WarePageLocators.EDIT_BTN,WarePageLocators.LAV_AUT_BTN,WarePageLocators.WARE_TAGS_BTN)//Lavka.Autoorder,dd a line Warehouse Tags
        HomePage.clicks_on_the_button(WarePageLocators.CREATE_WARTAG_BTN)
        HomePage.clicks_button_select(WarePageLocators.TYPE_BTN,WarePageLocators.VS_BTN)
        HomePage.find_click_and_fill_in(WarePageLocators.NAME_FLD,GEO)
        HomePage.xpath_elem_cycle_click(WarePageLocators.SAVE_CLOSE_XP)
        HomePage.two_clicks_in_the_fields(WarePageLocators.PUR_TAGS_BTN,WarePageLocators.CREATE_WARTAG_BTN)
        HomePage.clicks_button_select(WarePageLocators.TYPE_BTN,WarePageLocators.ASSORT_BTN)
        HomePage.find_click_and_fill_in(WarePageLocators.NAME_FLD,GEO)
        HomePage.xpath_elem_cycle_click(WarePageLocators.SAVE_CLOSE_XP)
        HomePage.clicks_on_the_button(WarePageLocators.SAVE_BTN)
        HomePage.element_cycle(geo,assortment)
        HomePage.not_odoo_error()
        };

    // LT-149-1 Проверка невозможности дубля геометки
    static Wareh_GEO_NO_DOUBLE(GEO) {
        WarehausesPage.WarehAuth()
        HomePage.elem_cycle_click(WarePageLocators.DELI_BTN,WarePageLocators.EDIT_BTN,WarePageLocators.LAV_AUT_BTN,WarePageLocators.WARE_TAGS_BTN)//Lavka.Autoorder,dd a line Warehouse Tags
        HomePage.clicks_on_the_button(WarePageLocators.CREATE_WARTAG_BTN)
        HomePage.clicks_button_select(WarePageLocators.TYPE_BTN,WarePageLocators.VS_BTN)
        HomePage.find_click_and_fill_in(WarePageLocators.NAME_FLD,GEO)
        HomePage.xpath_elem_cycle_click(WarePageLocators.SAVE_CLOSE_XP)
        HomePage.element_cycle('Type + name should be unique')
        HomePage.xpath_elem_cycle_click(BasePageLocators.OK_XP_BTN)
        HomePage.not_odoo_error()
        };

    // LT-149-2 Проверка невозможности дубля метки ассортимента
    static Wareh_ASSORT_NO_DOUBLE(assortment) {
        WarehausesPage.WarehAuth()
        HomePage.elem_cycle_click(WarePageLocators.DELI_BTN,WarePageLocators.EDIT_BTN,WarePageLocators.LAV_AUT_BTN)//Lavka.Autoorder
        HomePage.two_clicks_in_the_fields(WarePageLocators.PUR_TAGS_BTN,WarePageLocators.CREATE_WARTAG_BTN)
        HomePage.clicks_button_select(WarePageLocators.TYPE_BTN,WarePageLocators.ASSORT_BTN)
        HomePage.find_click_and_fill_in(WarePageLocators.NAME_FLD,assortment)
        HomePage.xpath_elem_cycle_click(WarePageLocators.SAVE_CLOSE_XP)
        HomePage.element_cycle('Type + name should be unique')
        HomePage.xpath_elem_cycle_click(BasePageLocators.OK_XP_BTN)
        HomePage.not_odoo_error()
        };

     // Проверка что невозможно создать склад и отредактировать название
    static Wareh_No_Create() {
        WarehausesPage.WarehAuth()
        HomePage.not_cont_text('Create')
        HomePage.clicks_on_the_button(WarePageLocators.DELI_BTN)
        HomePage.not_element(WarePageLocators.NAME_WH,WarePageLocators.NAME_WMS)
        HomePage.not_odoo_error()
        };   
    
}