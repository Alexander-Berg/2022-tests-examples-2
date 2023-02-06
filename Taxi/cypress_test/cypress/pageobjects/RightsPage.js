import {AuthPageLocators, BasePageLocators,PurInstPageLocators,VendorsPageLocators,AgrementsPageLocators, AutoordPageLocators, 
    OrdersPageLocators,YandexWMSPageLoc, InvoicPageLoc, SalesPageLoc,OpenAPIPageLoc,JobQueuePageLoc} from './LocatorsPage'
import { HomePage } from './HomePage'
import { SettingsPage } from './SettingsPage'

export class RightsPage {
    
    //LT-218-1 Проверка основных плашек главного меню
    static Right_218_1(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.get_cycle(BasePageLocators.DISC_BTN,BasePageLocators.SALE_BTN,BasePageLocators.API_BTN)
        HomePage.get_cycle(BasePageLocators.J_QUEUE_BTN,BasePageLocators.YAWMS_BTN,BasePageLocators.SALE_PR_BTN)
        HomePage.get_cycle(BasePageLocators.PURCHASE_BTN,BasePageLocators.INVENT_BTN,BasePageLocators.INVOIC_BTN)
        HomePage.get_cycle(BasePageLocators.DASH_BTN,BasePageLocators.APP_BTN,BasePageLocators.SETT_BTN)
        };

    //LT-218-2 Проверяем что есть все элементы выбора основных разделов Purchase
    static Right_218_2(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.elem_cycle_click(BasePageLocators.PURCHASE_BTN)
        HomePage.get_cycle(OrdersPageLocators.ORDERS_BTN,OrdersPageLocators.PRODUCT_BTN,OrdersPageLocators.VENDOR_BTN)
        HomePage.get_cycle(OrdersPageLocators.WAREHOUSES_BTN,OrdersPageLocators.AUTOORDER_BTN,OrdersPageLocators.PURCHASE_INS_BTN)
        HomePage.get_cycle(OrdersPageLocators.TEAMS_BTN,OrdersPageLocators.REPORTING_BTN,OrdersPageLocators.CONFIGURATION_BTN)
        };

    //LT-218-3 Проверяем что есть все элементы выбора основных разделов Purchase - Orders
    static Right_218_3(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.elem_cycle_click(BasePageLocators.PURCHASE_BTN,OrdersPageLocators.ORDERS_BTN)
        HomePage.get_cycle(OrdersPageLocators.DRAFT_RFQS_BTN,OrdersPageLocators.REGUEST_BTN,OrdersPageLocators.PURCH_ORD_BTN)
        HomePage.get_cycle(OrdersPageLocators.PURCH_ORD_LN_BTN,OrdersPageLocators.CREAT_BILL_BTN,OrdersPageLocators.TRANSF_OR_BTN)
        };

    //LT-218-4 Проверяем что есть все элементы выбора основных разделов Purchase - Products
    static Right_218_4(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.elem_cycle_click(BasePageLocators.PURCHASE_BTN,OrdersPageLocators.PRODUCT_BTN)
        HomePage.get_cycle(OrdersPageLocators.PUR_ASS_MAT_BTN,OrdersPageLocators.PRODUCT_PR_BTN)
        };

    //LT-218-5 Проверяем что есть все элементы выбора основных разделов Purchase - Vendors
    static Right_218_5(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.elem_cycle_click(BasePageLocators.PURCHASE_BTN,OrdersPageLocators.VENDOR_BTN)
        HomePage.get_cycle(OrdersPageLocators.VENDORS_BTN,OrdersPageLocators.PUR_AGR_BTN,OrdersPageLocators.PUR_AGR_LINE_BTN)
        HomePage.get_cycle(OrdersPageLocators.OEBS_CON_BTN)
        };

    //LT-218-6 Проверяем что есть все элементы выбора основных разделов Purchase - Autoorder
    static Right_218_6(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.elem_cycle_click(BasePageLocators.PURCHASE_BTN,OrdersPageLocators.AUTOORDER_BTN)
        HomePage.get_cycle(OrdersPageLocators.DELIV_SHEDULE_BTN,OrdersPageLocators.SAFETY_ST_BTN,OrdersPageLocators.CORRECT_COEF_BTN)
        HomePage.get_cycle(OrdersPageLocators.FIX_ORD_SET_BTN,OrdersPageLocators.TASK_BTN,OrdersPageLocators.SUPPLY_CHAIN_BTN)
        HomePage.get_cycle(OrdersPageLocators.TRANSIT_SET_BTN,OrdersPageLocators.AUTOORD_RESULT_BTN,OrdersPageLocators.EXP_TO_AUTOORD_BTN)
        HomePage.get_cycle(OrdersPageLocators.DIST_CENTER_QUANT_BTN)
        };

    //LT-218-7 Проверяем что есть все элементы выбора основных разделов Purchase - Purchase Instruments
    static Right_218_7(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.elem_cycle_click(BasePageLocators.PURCHASE_BTN,OrdersPageLocators. PURCHASE_INS_BTN)
        HomePage.get_cycle(OrdersPageLocators.IMPORT_ORDER_BTN,OrdersPageLocators.IMP_ORD_WITH_DELIV_BTN,OrdersPageLocators.IMP_ASSORT_BTN)
        HomePage.get_cycle(OrdersPageLocators.IMP_SCHEDULE_BTN,OrdersPageLocators.IMP_PROD_OUT_VAT_BTN,OrdersPageLocators. IMP_SAFETY_ST_BTN)
        HomePage.get_cycle(OrdersPageLocators.IMP_REG_LINES_BTN,OrdersPageLocators.IMP_TRANSFER_BTN,OrdersPageLocators.IMP_SUPP_CHAIN_BTN)
        HomePage.get_cycle(OrdersPageLocators.IMP_TRANSIT_SETT_BTN,OrdersPageLocators.IMP_SUPP_QUANTS)
        };

    //LT-218-8 Проверяем что есть все элементы выбора основных разделов Purchase - Configuration
    static Right_218_8(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.elem_cycle_click(BasePageLocators.PURCHASE_BTN,OrdersPageLocators. CONFIGURATION_BTN)
        HomePage.get_cycle(OrdersPageLocators.SETTING_BTN,OrdersPageLocators.VENDOR_PRICE_BTN,OrdersPageLocators.PURCH_AGR_TYPE_BTN)
        HomePage.get_cycle(OrdersPageLocators.PRODUCT_CAT_BTN)
        };

    //LT-219-1 Проверка основных меню верхнего ряда Yandex.WMS
    static Right_219_1(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.elem_cycle_click(BasePageLocators.YAWMS_BTN)
        HomePage.get_cycle(YandexWMSPageLoc.WMS_BTN,YandexWMSPageLoc.QUEUE_BTN,YandexWMSPageLoc.SHEDULE_ACT_BTN)
        HomePage.get_cycle(YandexWMSPageLoc.SISTEM_PARAMETRS_BTN,YandexWMSPageLoc.APPROVALS_BTN,YandexWMSPageLoc.WAREHAUSES_BTN)
        HomePage.get_cycle(YandexWMSPageLoc.DOCUMENTS_BTN,YandexWMSPageLoc. AUTOTESTS_BTN)   
        };

    //LT-219-2 Проверка основных меню Yandex.WMS - WMS
    static Right_219_2(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.elem_cycle_click(BasePageLocators.YAWMS_BTN,YandexWMSPageLoc.WMS_BTN)
        HomePage.get_cycle(YandexWMSPageLoc.ORDERS_BTN,YandexWMSPageLoc.STOCK_LOGS_BTN,YandexWMSPageLoc.WMS_CURSOR_BTN)
        HomePage.get_cycle(YandexWMSPageLoc.WMS_LOCKS_BTN)
        };

    //LT-219-3 Проверка основных меню Yandex.WMS - Documents
    static Right_219_3(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.elem_cycle_click(BasePageLocators.YAWMS_BTN,YandexWMSPageLoc.DOCUMENTS_BTN)
        HomePage.get_cycle(YandexWMSPageLoc.PURSHASE_ORD_BTN,YandexWMSPageLoc.TRANSFER_ORD_BTN,YandexWMSPageLoc.PURSHASE_AGR_BTN)
        HomePage.get_cycle(YandexWMSPageLoc.PURSHASE_AGR_LINE_BTN,YandexWMSPageLoc.STOCK_MOVES_BTN,YandexWMSPageLoc.SALE_ORDER_BTN)
        };

    //LT-219-4 Проверка основных меню Yandex.WMS - Autotests
    static Right_219_4(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.elem_cycle_click(BasePageLocators.YAWMS_BTN,YandexWMSPageLoc.AUTOTESTS_BTN)
        HomePage.get_cycle(YandexWMSPageLoc.CREATE_USERS_BTN)
        };

    //LT-233-1 Проверка что верхний ряд заполнен Invoicing
    static Right_233_1(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.elem_cycle_click(InvoicPageLoc.INVOICING_BTN)
        HomePage.get_cycle(InvoicPageLoc.CUSTOMERS_BTN,InvoicPageLoc.INVOIC_VEND_BTN,InvoicPageLoc.REPORTING_BTN)
        HomePage.get_cycle(InvoicPageLoc.INVOIC_CONF_BTN)
        };

    //LT-233-2 Проверка что в Invoicing-Customers есть все пункты
    static Right_233_2(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.elem_cycle_click(InvoicPageLoc.INVOICING_BTN,InvoicPageLoc.CUSTOMERS_BTN)
        HomePage.get_cycle(InvoicPageLoc.INVOICES_BTN,InvoicPageLoc.CREDIT_NOTE_BTN,InvoicPageLoc.PAYMENTS_BTN)
        HomePage.get_cycle(InvoicPageLoc.PRODUCTS_BTN,InvoicPageLoc.CUSTOMERS_CUS_BTN)
        };

    //LT-233-2 Проверка что в Invoicing-Customers есть все пункты
    static Right_233_2(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.elem_cycle_click(InvoicPageLoc.INVOICING_BTN,InvoicPageLoc.CUSTOMERS_BTN)
        HomePage.get_cycle(InvoicPageLoc.INVOICES_BTN,InvoicPageLoc.CREDIT_NOTE_BTN,InvoicPageLoc.PAYMENTS_BTN)
        HomePage.get_cycle(InvoicPageLoc.PRODUCTS_BTN,InvoicPageLoc.CUSTOMERS_CUS_BTN)
        };

    //LT-233-3 Проверка что в Invoicing-Vendors есть все пункты
    static Right_233_3(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.elem_cycle_click(InvoicPageLoc.INVOICING_BTN,InvoicPageLoc.INVOIC_VEND_BTN)
        HomePage.get_cycle(InvoicPageLoc.BILLS_BTN,InvoicPageLoc.REFUNDS_BTN,InvoicPageLoc.PAYMENTS_BTN)
        HomePage.get_cycle(InvoicPageLoc.INVOIC_PRODUCT_BTN,InvoicPageLoc.VENDORS_BTN)
        };

    //LT-233-4 Проверка что в Invoicing-Reporting есть все пункты
    static Right_233_4(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.elem_cycle_click(InvoicPageLoc.INVOICING_BTN,InvoicPageLoc.REPORTING_BTN)
        HomePage.get_cycle(InvoicPageLoc.INVOICE_ANALYSIS_BTN)
        };

    //LT-233-5 Проверка что в Invoicing-Configuration есть все пункты
    static Right_233_5(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.elem_cycle_click(InvoicPageLoc.INVOICING_BTN,InvoicPageLoc.INVOIC_CONF_BTN)
        HomePage.get_cycle(InvoicPageLoc.SETTING_BTN,InvoicPageLoc.PAY_TERMS_BTN,InvoicPageLoc.INCOTERMS_BTN)
        HomePage.get_cycle(InvoicPageLoc.ADD_A_BANK_BTN,InvoicPageLoc.RECON_MODEL_BTN,InvoicPageLoc.TAXES_BTN)
        HomePage.get_cycle(InvoicPageLoc.JOURNAL_BTN,InvoicPageLoc.FISCAL_POS_BTN,InvoicPageLoc.JOURNAL_GR_BTN)
        HomePage.get_cycle(InvoicPageLoc.PAYMENT_ACG_BTN,InvoicPageLoc.PRODUCT_CAT_BTN,InvoicPageLoc.INPUT_BALANCES_BTN)
        };

    //LT-236-1 Проверка что верхний ряд заполнен Sales
    static Right_236_1(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.elem_cycle_click(BasePageLocators.SALE_BTN)
        HomePage.get_cycle(SalesPageLoc.ORDERS_BTN,SalesPageLoc.TO_INVOICE_BTN,SalesPageLoc.PRODUCT_BTN)
        HomePage.get_cycle(SalesPageLoc.REPORTING_BTN,SalesPageLoc.CONFIG_BTN)
        };

    //LT-236-2 Проверка что в Sales-Orders есть все пункты
    static Right_236_2(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.elem_cycle_click(BasePageLocators.SALE_BTN,SalesPageLoc.ORDERS_BTN)
        HomePage.get_cycle(SalesPageLoc.QUOTATION_BTN,SalesPageLoc.ORDER_BTN,SalesPageLoc.SALES_TEAMS_BTN)
        HomePage.get_cycle(SalesPageLoc.CUSTOMERS_BTN)
        };

    //LT-236-3 Проверка что в Sales-To Invoice есть все пункты
    static Right_236_3(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.elem_cycle_click(BasePageLocators.SALE_BTN,SalesPageLoc.TO_INVOICE_BTN)
        HomePage.get_cycle(SalesPageLoc.ORD_TO_INV_BTN,SalesPageLoc.ORD_TO_UPSELL)
        };

    //LT-236-4 Проверка что в Sales-Products есть все пункты
    static Right_236_4(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.elem_cycle_click(BasePageLocators.SALE_BTN,SalesPageLoc.PRODUCT_BTN)
        HomePage.get_cycle(SalesPageLoc.PRODUCTS_BTN)
        };

    //LT-236-5 Проверка что в Sales-Reporting есть все пункты
    static Right_236_5(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.elem_cycle_click(BasePageLocators.SALE_BTN,SalesPageLoc.REPORTING_BTN)
        HomePage.get_cycle(SalesPageLoc.SALES_BTN)
        };

    //LT-236-6 Проверка что в Sales-Configuration есть все пункты
    static Right_236_6(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.elem_cycle_click(BasePageLocators.SALE_BTN,SalesPageLoc.CONFIG_BTN)
        HomePage.get_cycle(SalesPageLoc.SETTINGS_BTN,SalesPageLoc.SALE_TEAM_BTN,SalesPageLoc.TAGS_BTN)
        };

    //LT-237-1 Проверка есть все меню OpenAPI
    static Right_237_1(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.elem_cycle_click(BasePageLocators.API_BTN,OpenAPIPageLoc.OPEN_API_BTN)
        HomePage.get_cycle(OpenAPIPageLoc.OPEN_API_BTN)
        };

    //LT-238-1 Проверка что верхний ряд заполнен Job Queue
    static Right_238_1(User,pass) {
        SettingsPage.SettAuth_n(User,pass)
        HomePage.elem_cycle_click(BasePageLocators.J_QUEUE_BTN,JobQueuePageLoc.QUEUE_BTN)
        HomePage.get_cycle(JobQueuePageLoc.JOBS_BTN,JobQueuePageLoc.CHANNELS_BTN,JobQueuePageLoc.JOB_FUNCT_BTN)
        };


    }
