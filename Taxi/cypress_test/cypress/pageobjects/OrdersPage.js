import {AuthPageLocators, BasePageLocators,OrdersPageLocators,AgrementsPageLocators,PurInstPageLocators} from './LocatorsPage'
import { HomePage } from './HomePage'
var chaiColors = require('chai-colors');    
chai.use(chaiColors);


export class PurOrdersPage {
    
    static PurOrdersAuth() {
        HomePage.login()
        HomePage.elem_cycle_click(BasePageLocators.MENU_BTN,BasePageLocators.PURCHASE_BTN,OrdersPageLocators.ORDERS_BTN)
        HomePage.clicks_on_the_button(OrdersPageLocators.PURCH_ORD_BTN) // Purchase Orders
        };

    static DraftAuth() {
        HomePage.login()
        HomePage.elem_cycle_click(BasePageLocators.MENU_BTN,BasePageLocators.PURCHASE_BTN,OrdersPageLocators.ORDERS_BTN)
        HomePage.clicks_on_the_button(OrdersPageLocators.DRAFT_BTN) // Draft
        };

    static TransOrdersAuth() {
        HomePage.login()
        HomePage.elem_cycle_click(BasePageLocators.MENU_BTN,BasePageLocators.PURCHASE_BTN,OrdersPageLocators.ORDERS_BTN)
        HomePage.clicks_on_the_button(OrdersPageLocators.TR_ORD_BTN) // Transfer Orders
        };

    static RequestQuotAuth() {
        HomePage.login()
        HomePage.elem_cycle_click(BasePageLocators.MENU_BTN,BasePageLocators.PURCHASE_BTN,OrdersPageLocators.ORDERS_BTN) 
        HomePage.clicks_on_the_button(OrdersPageLocators.REQ_F_Q_BTN) // Requests for Quotation
        };

    // Создание orders при всех обязательных значениях
    static Pur_Ord_Create(NAME_AGR,Value,Status) {
        PurOrdersPage.PurOrdersAuth()
        HomePage.clicks_on_the_button(OrdersPageLocators.IMPORT_ORD_BTN) //import
        cy.get(AgrementsPageLocators.NAME_FILE_BTN).attachFile({ filePath: NAME_AGR});
        HomePage.clicks_on_the_button(PurInstPageLocators.LOAD_BTN)
        HomePage.element_cycle(Value,Status)
        };

    // LT_132_1 Проверка невозможности править цену
    static Dont_Edit_Price(NAME_AGR,Value,Status) {
        PurOrdersPage.PurOrdersAuth()
        HomePage.clicks_on_the_button(OrdersPageLocators.IMPORT_ORD_BTN) //import
        cy.get(AgrementsPageLocators.NAME_FILE_BTN).attachFile({ filePath: NAME_AGR});
        HomePage.clicks_on_the_button(PurInstPageLocators.LOAD_BTN)
        HomePage.contains_click('span',BasePageLocators.BASE_VENDOR)
        HomePage.clicks_on_the_button(BasePageLocators.EDIT_BTN)
        HomePage.xpath_clicks_on_the_button(OrdersPageLocators.RFQ_FLD_XP)
        HomePage.xpath_find_click_and_fill_in(OrdersPageLocators.PRICE_FLD_XP,'555')
        HomePage.xpath_elem_cycle_click(BasePageLocators.SAVE_XP_BTN)
        HomePage.element_cycle(Value,Status)
        };

    // LT_132_2 Проверка что возможно править количество товара
    static Edit_Price(NAME_AGR,Value,COL) {
        PurOrdersPage.PurOrdersAuth()
        HomePage.clicks_on_the_button(OrdersPageLocators.IMPORT_ORD_BTN) //import
        cy.get(AgrementsPageLocators.NAME_FILE_BTN).attachFile({ filePath: NAME_AGR});
        HomePage.clicks_on_the_button(PurInstPageLocators.LOAD_BTN)
        HomePage.contains_click('span',BasePageLocators.BASE_VENDOR)
        HomePage.clicks_on_the_button(BasePageLocators.EDIT_BTN)
        HomePage.xpath_find_click_and_fill_in(OrdersPageLocators.RFQ_FLD_XP,77777)
        HomePage.xpath_elem_cycle_click(BasePageLocators.SAVE_XP_BTN)
        HomePage.element_cycle(Value,COL)
        };


    // Создание transfer_orders при всех обязательных значениях
    static Pur_Transf_Create(WAREH_OUT,WAREH_IN,COL_FLD,id_pr,n) {
        PurOrdersPage.TransOrdersAuth()
        HomePage.clicks_on_the_button(OrdersPageLocators.CREATE_ORD_BTN) //create
        HomePage.click_write_enter(OrdersPageLocators.WAREH_OUT_FLD,WAREH_OUT)
        HomePage.click_write_enter(OrdersPageLocators.WAREH_IN_FLD,WAREH_IN)
        HomePage.click_write_enter(OrdersPageLocators.DATE_FLD,HomePage.date_local_n(n))
        HomePage.xpath_clicks_on_the_button(OrdersPageLocators.PRODUCT_ORD_BTN_XP)
        HomePage.click_write_enter(OrdersPageLocators.PR_ORD_FIELD,id_pr)
        HomePage.find_click_and_fill_in(OrdersPageLocators.COL_FLD,COL_FLD)
        HomePage.clicks_on_the_button(OrdersPageLocators.Save_ORD_BTN)
        HomePage.element_cycle(OrdersPageLocators.CREAT_OK_TXT1,WAREH_OUT,WAREH_IN,COL_FLD)
        };

    // Добавление в transfer_orders нового файла
    static Pur_Transf_Edit_xls(NAME_AGR,el1,el2,el3) {
        PurOrdersPage.TransOrdersAuth()
        HomePage.clicks_on_the_button(OrdersPageLocators.Ware_IN_77)
        HomePage.xpath_elem_cycle_click(OrdersPageLocators.IMP_FR_EX_XP)
        cy.get(AgrementsPageLocators.NAME_FILE_BTN).attachFile({ filePath: NAME_AGR});
        HomePage.clicks_on_the_button(AgrementsPageLocators.LOAD_F_BTN)
        HomePage.element_cycle(el1,el2,el3,'Edit')
        };

    // Создание Requests for Quotation при всех обязательных значениях
    static Request_F_Quat_Create(NAME_AGR,Value,Status) {
        PurOrdersPage.RequestQuotAuth()
        HomePage.clicks_on_the_button(OrdersPageLocators.IMPORT_ORD_BTN) //import
        cy.get(AgrementsPageLocators.NAME_FILE_BTN).attachFile({ filePath: NAME_AGR});
        HomePage.clicks_on_the_button(PurInstPageLocators.LOAD_BTN)
        HomePage.element_cycle(Value,Status)
        };

    // Проверка невозможности редактирования wms_id
    static Drafr_Not_Edit() {
        PurOrdersPage.DraftAuth()
        HomePage.clicks_on_the_button(OrdersPageLocators.NUM_ORD_BTN)
        HomePage.element(OrdersPageLocators.PO1)
        };

    // Проверка цветовой индикации даты ордера
    static Color_Date() {
        PurOrdersPage.DraftAuth()
        HomePage.color_check(OrdersPageLocators.COLOR_BTN,OrdersPageLocators.gray)//серый-завтра
        HomePage.clicks_on_the_button(OrdersPageLocators.COLOR_BTN)
        HomePage.clicks_on_the_button(BasePageLocators.EDIT_BTN)
        HomePage.clicks_button_clear(OrdersPageLocators.RES_DATE_BTN,HomePage.date_local())
        HomePage.elem_cycle_click(OrdersPageLocators.Save_ORD_BTN,OrdersPageLocators.DRAFT_RFQ_BTN)
        HomePage.color_check(OrdersPageLocators.COLOR_BTN,OrdersPageLocators.orange)//оранжевый - сегодня
        HomePage.elem_cycle_click(OrdersPageLocators.COLOR_BTN,BasePageLocators.EDIT_BTN)
        HomePage.clicks_button_clear(OrdersPageLocators.RES_DATE_BTN,HomePage.date_local_n(-24))
        HomePage.elem_cycle_click(OrdersPageLocators.Save_ORD_BTN,OrdersPageLocators.DRAFT_RFQ_BTN)
        HomePage.color_check(OrdersPageLocators.COLOR_BTN,OrdersPageLocators.red)//красный-вчера
        };

    // Проверка невозможности удаления продукта из ордера в wms
    static Not_Del_Product(number) {
        PurOrdersPage.DraftAuth()
        HomePage.contains_click('td',number)
        HomePage.elem_cycle_click(BasePageLocators.ACTION_BTN,BasePageLocators.SEND_WMS_BTN,BasePageLocators.EDIT_BTN,)
        HomePage.elem_cycle_click(OrdersPageLocators.DELIT_BTN,OrdersPageLocators.Save_ORD_BTN)
        HomePage.cont_text('User Error')
        };

    // Тест LT-148-1 Проверка создания Duplicate Draft
    static Draft_Duplicate_148_1(order,SUM) {
        PurOrdersPage.DraftAuth()
        HomePage.contains_click('td',order)
        HomePage.xpath_elem_cycle_click(OrdersPageLocators.DUBL_OR_BTN_XP)
        HomePage.element_n_xp(BasePageLocators.SAVE_XP_BTN,5000)
        HomePage.xpath_clicks_on_the_button(BasePageLocators.SAVE_XP_BTN)
        HomePage.element_cycle('Edit',SUM)
    }

    // Тесты проверки джобы по отмене просроченных ордеров
    static Aut_Cansell_Orders() {
        HomePage.login()
        HomePage.elem_cycle_click(BasePageLocators.MENU_BTN,BasePageLocators.YAWMS_BTN,BasePageLocators.SC_ACT_BTN)
        HomePage.xpath_clicks_on_the_button(BasePageLocators.AUT_CANS_ORD_WMS_XP)
        HomePage.clicks_on_the_button(BasePageLocators.RUN_MAN_BTN)
        HomePage.elem_cycle_click(BasePageLocators.MENU_BTN,BasePageLocators.PURCHASE_BTN,OrdersPageLocators.ORDERS_BTN,OrdersPageLocators.REQ_F_Q_BTN)
        HomePage.should_text(OrdersPageLocators.ORD1,'Locked')
        HomePage.should_text(OrdersPageLocators.ORD2,'Locked')
        HomePage.should_text(OrdersPageLocators.ORD3,'RFQ Sent')
        HomePage.should_text(OrdersPageLocators.ORD4,'Cancelled')
        HomePage.should_text(OrdersPageLocators.ORD5,'Locked') 
        };

    // 458-1 Проверка отмены ордера имеющего статус shipment
    static Cansell_Transfer_Shipment(WAREH_OUT,WAREH_IN,COL_FLD,id_pr,n) {
       PurOrdersPage.Pur_Transf_Create(WAREH_OUT,WAREH_IN,COL_FLD,id_pr,n)
       HomePage.clicks_on_the_button(OrdersPageLocators.CHECK_PLAN_BTN)
       HomePage.element_cycle('Ordered quantity successfully checked')
       HomePage.clicks_on_the_button(OrdersPageLocators.APPROVE_ORDER_BTN)
       HomePage.clicks_on_the_button(OrdersPageLocators.CREATE_SHIP_BTN)
       HomePage.color_check(OrdersPageLocators.CURR_SENT,OrdersPageLocators.green)
       HomePage.not_element_n(BasePageLocators.SPIN,300000)
       HomePage.element_cycle('Ordered quantity successfully checked')
       HomePage.clicks_on_the_button(OrdersPageLocators.CANCEL_BTN)
       HomePage.color_check(OrdersPageLocators.CURR_SENT,OrdersPageLocators.green)
       HomePage.element_cycle('Requesting WMS to cancel ')
        };

    // Тест 589-1 Проверка невозможности создать ТО на вчерашнюю дату
    static Date_TO_Expiried(WAREH_OUT,WAREH_IN,COL_FLD,id_pr,n) {
        PurOrdersPage.TransOrdersAuth()
        HomePage.clicks_on_the_button(OrdersPageLocators.CREATE_ORD_BTN) //create
        HomePage.click_write_enter(OrdersPageLocators.WAREH_OUT_FLD,WAREH_OUT)
        HomePage.click_write_enter(OrdersPageLocators.WAREH_IN_FLD,WAREH_IN)
        HomePage.click_write_enter(OrdersPageLocators.DATE_FLD,HomePage.date_local_n(n))
        HomePage.xpath_clicks_on_the_button(OrdersPageLocators.PRODUCT_ORD_BTN_XP)
        HomePage.click_write_enter(OrdersPageLocators.PR_ORD_FIELD,id_pr)
        HomePage.find_click_and_fill_in(OrdersPageLocators.COL_FLD,COL_FLD)
        HomePage.clicks_on_the_button(OrdersPageLocators.Save_ORD_BTN)
        HomePage.element_cycle("The 'Planned shipment date' can not be set in the past")
        HomePage.clicks_on_the_button(OrdersPageLocators.OK_TO_BTN)
        HomePage.not_cont_text("The 'Planned shipment date' can not be set in the past")
        HomePage.element_cycle('Save')
        };

    // Тест 589-2 Проверка невозможности создать ТО на вчерашнюю дату через файл
    static Date_TO_Expiried_xls(WAREH_OUT,WAREH_IN,n) {
        PurOrdersPage.TransOrdersAuth()
        HomePage.clicks_on_the_button(OrdersPageLocators.CREATE_ORD_BTN) //create
        HomePage.click_write_enter(OrdersPageLocators.WAREH_OUT_FLD,WAREH_OUT)
        HomePage.click_write_enter(OrdersPageLocators.WAREH_IN_FLD,WAREH_IN)
        HomePage.click_write_enter(OrdersPageLocators.DATE_FLD,HomePage.date_local_n(n))
        HomePage.xpath_elem_cycle_click(OrdersPageLocators.IMP_FR_EX_XP)
        HomePage.element_cycle("The 'Planned shipment date' can not be set in the past")
        HomePage.clicks_on_the_button(OrdersPageLocators.OK_TO_BTN)
        HomePage.not_cont_text("The 'Planned shipment date' can not be set in the past")
        HomePage.element_cycle('Save')
        };

    // Тест 590-1 Проверка удаления ТО через delit
    static TransOrderDelit(WAREH_OUT,WAREH_IN,COL_FLD,id_pr,n) {
        PurOrdersPage. Pur_Transf_Create(WAREH_OUT,WAREH_IN,COL_FLD,id_pr,n)
        HomePage.elem_cycle_click(OrdersPageLocators.TR_ORD_ACTION_BTN,OrdersPageLocators.TR_ORD_DEL_BTN)
        HomePage.cont_text('Are you sure you want to delete this record?')
        HomePage.clicks_on_the_button(OrdersPageLocators.OK_TO_DEL_BTN)
        HomePage.not_cont_text(COL_FLD)
        };

    // Тест 590-2 Проверка удаления ТО через delit - можно отменить удаление
    static TransOrderDelit(WAREH_OUT,WAREH_IN,COL_FLD,id_pr,n) {
        PurOrdersPage. Pur_Transf_Create(WAREH_OUT,WAREH_IN,COL_FLD,id_pr,n)
        HomePage.elem_cycle_click(OrdersPageLocators.TR_ORD_ACTION_BTN,OrdersPageLocators.TR_ORD_DEL_BTN)
        HomePage.cont_text('Are you sure you want to delete this record?')
        HomePage.clicks_on_the_button(OrdersPageLocators. TR_ORD_CANS_BTN)
        HomePage.cont_text(COL_FLD)
        };

    // Тест 590-3 Проверка отмены ТО через cansell из action 
    static TransOrderDelit(WAREH_OUT,WAREH_IN,COL_FLD,id_pr,n) {
        PurOrdersPage. Pur_Transf_Create(WAREH_OUT,WAREH_IN,COL_FLD,id_pr,n)
        HomePage.elem_cycle_click(OrdersPageLocators.TR_ORD_ACTION_BTN,OrdersPageLocators.TR_ACT_CANS_BTN)
        HomePage.color_check(OrdersPageLocators.CURR_SENT,OrdersPageLocators.green)
        };
}