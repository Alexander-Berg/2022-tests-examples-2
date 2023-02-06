import {AuthPageLocators, BasePageLocators,OrdersPageLocators,AutoordPageLocators} from './LocatorsPage'
import { HomePage } from './HomePage'


export class AutoorderPage {
    
    static AutoorderAuth() {
        HomePage.login()
        HomePage.elem_cycle_click(BasePageLocators.MENU_BTN,BasePageLocators.PURCHASE_BTN,AutoordPageLocators.AUTOORD_BTN)// Autoorder
        };

    // Создание Delivery Schedule при всех обязательных значениях и геометки
    static Deliv_Schedule(num,VIS_TXT) {
        AutoorderPage.AutoorderAuth()
        HomePage.clicks_on_the_button(AutoordPageLocators.DELIV_SH_BTN)
        HomePage.clicks_on_the_button(OrdersPageLocators.CREATE_ORD_BTN) //create
        HomePage.clicks_button_enter(AutoordPageLocators.VEND_ID) //Поле vendor
        HomePage.clicks_button_clear(AutoordPageLocators.DAYS_BO_FLD,num)
        HomePage.two_clicks_in_the_fields(AutoordPageLocators.OR_WE2_BTN,AutoordPageLocators.OR_WE3_BTN)
        HomePage.clicks_on_the_button(AutoordPageLocators.DE_WE_BTN)
        HomePage.click_write_enter(AutoordPageLocators.WAR_TAG_FLD,'geo: UK')
        HomePage.clicks_on_the_button(OrdersPageLocators.Save_ORD_BTN) //Save
        HomePage.element_cycle(VIS_TXT,num)
        };

    // Проверка что Delivery Schedule нельзя создать без указания склада или геометки
    static Deliv_Schedule_222_1(num) {
        AutoorderPage.AutoorderAuth()
        HomePage.clicks_on_the_button(AutoordPageLocators.DELIV_SH_BTN)
        HomePage.clicks_on_the_button(OrdersPageLocators.CREATE_ORD_BTN) //create
        HomePage.clicks_button_enter(AutoordPageLocators.VEND_ID) //Поле vendor
        HomePage.clicks_button_clear(AutoordPageLocators.DAYS_BO_FLD,num)
        HomePage.two_clicks_in_the_fields(AutoordPageLocators.OR_WE2_BTN,AutoordPageLocators.OR_WE3_BTN)
        HomePage.clicks_on_the_button(AutoordPageLocators.DE_WE_BTN)
        HomePage.clicks_on_the_button(OrdersPageLocators.Save_ORD_BTN) //Save
        HomePage.cont_text('Choose warehouse groups or warehouses')
        };

    // Создание Delivery Schedule при всех обязательных значениях и выборе склада
    static Deliv_Schedule_222_2(num,VIS_TXT) {
        AutoorderPage.AutoorderAuth()
        HomePage.clicks_on_the_button(AutoordPageLocators.DELIV_SH_BTN)
        HomePage.clicks_on_the_button(OrdersPageLocators.CREATE_ORD_BTN) //create
        HomePage.clicks_button_enter(AutoordPageLocators.VEND_ID) //Поле vendor
        HomePage.clicks_button_clear(AutoordPageLocators.DAYS_BO_FLD,num)
        HomePage.two_clicks_in_the_fields(AutoordPageLocators.OR_WE2_BTN,AutoordPageLocators.OR_WE3_BTN)
        HomePage.clicks_on_the_button(AutoordPageLocators.DE_WE_BTN)
        HomePage.click_write_enter(AutoordPageLocators.WAREH_FLD,'San Francisco')
        HomePage.clicks_on_the_button(OrdersPageLocators.Save_ORD_BTN) //Save
        HomePage.element_cycle(VIS_TXT,num)
        };

    // Создание Delivery Schedule при всех обязательных значениях с Order Exception Days
    static Deliv_Schedule_EX_D(num,VIS_TXT,n1,n2) {
        AutoorderPage.AutoorderAuth()
        HomePage.clicks_on_the_button(AutoordPageLocators.DELIV_SH_BTN)
        HomePage.clicks_on_the_button(OrdersPageLocators.CREATE_ORD_BTN) //create
        HomePage.clicks_button_enter(AutoordPageLocators.VEND_ID) //Поле vendor
        HomePage.clicks_button_clear(AutoordPageLocators.DAYS_BO_FLD,num)
        HomePage.two_clicks_in_the_fields(AutoordPageLocators.OR_WE2_BTN,AutoordPageLocators.OR_WE3_BTN)
        HomePage.clicks_on_the_button(AutoordPageLocators.DE_WE_BTN)
        HomePage.clicks_on_the_button(AutoordPageLocators.ADD_DELIV_BTN)
        HomePage.click_write_enter(AutoordPageLocators.ORDER_DATE_FLD,HomePage.date_local_n(n1))
        HomePage.click_write_enter(AutoordPageLocators.DELIV_DATE_FLD,HomePage.date_local_n(n2))
        HomePage.click_write_enter(AutoordPageLocators.WAR_TAG_FLD,'geo: UK')
        HomePage.clicks_on_the_button(OrdersPageLocators.Save_ORD_BTN) //Save
        HomePage.element_cycle(VIS_TXT,num)
        };

    // Создание Safety Stock при всех обязательных значениях
    static Safety_Stock(num,reason) {
        AutoorderPage.AutoorderAuth()
        HomePage.clicks_on_the_button(AutoordPageLocators.SAF_ST_BTN)
        HomePage.clicks_on_the_button(OrdersPageLocators.CREATE_ORD_BTN) //create
        HomePage.clicks_button_enter(BasePageLocators.PROD_ID_FLD) //выбор продукта
        HomePage.clicks_button_clear(AutoordPageLocators.VAL_FLD,num)
        HomePage.clicks_button_enter(AutoordPageLocators.WAR_TAG_FLD) //выбор геометки
        HomePage.clicks_on_the_button(OrdersPageLocators.Save_ORD_BTN) //Save
        HomePage.cont_text(reason)
        };

    // Создание Correction Coefficient при всех обязательных значениях
    static Corr_Coeff(hour,coef,reason) {
        AutoorderPage.AutoorderAuth()
        HomePage.clicks_on_the_button(AutoordPageLocators.CORR_COEFF_BTN)
        HomePage.clicks_on_the_button(OrdersPageLocators.CREATE_ORD_BTN) //create
        HomePage.click_write_enter(AutoordPageLocators.START_D_FLD,HomePage.date_local_n(0))
        HomePage.click_write_enter(AutoordPageLocators.END_D_FLD,HomePage.date_local_n(hour))
        HomePage.clicks_button_enter(BasePageLocators.PROD_ID_FLD) //выбор продукта
        HomePage.clicks_button_enter(AutoordPageLocators.WAREH_TAG_BTN) //выбор метки склада
        HomePage.find_click_and_fill_in(AutoordPageLocators.VAL_FLD,coef)
        HomePage.find_click_and_fill_in(AutoordPageLocators.REASON_FLD,reason)
        HomePage.clicks_on_the_button(AutoordPageLocators.SAVE_BTN) //Save
        HomePage.element_cycle(reason,'Create')//Проверяем что поле save сменилось на create
        };
    
    // Создание Safety Stock при всех обязательных значениях
    static Fix_Ord_Setting(min_n,max_n) {
        AutoorderPage.AutoorderAuth()
        HomePage.clicks_on_the_button(AutoordPageLocators.FIX_ORD_SET_BTN)
        HomePage.clicks_on_the_button(OrdersPageLocators.CREATE_ORD_BTN) //create
        HomePage.clicks_button_enter(BasePageLocators.PROD_ID_FLD) //выбор продукта
        HomePage.clicks_button_enter(AutoordPageLocators.WAREH_TAG_BTN) //выбор геометки
        HomePage.clicks_button_clear(AutoordPageLocators.MIN_ST_FLD,min_n)
        HomePage.clicks_button_clear(AutoordPageLocators.MAX_ST_FLD,max_n)
        HomePage.clicks_on_the_button(AutoordPageLocators.SAVE_BTN) //Save
        HomePage.element_cycle('Create',max_n)//Проверяем что поле save сменилось на create
        };
    }
