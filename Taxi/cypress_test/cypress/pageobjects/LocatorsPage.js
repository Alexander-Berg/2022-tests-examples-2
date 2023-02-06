
export const AuthPageLocators = {
    LOGIN_FIELD: "#login", // Поле логин
    PASSWORD_FIELD:'#password', // Поле пароль
    ENTER_BTN:'button[type="submit"]' // Кнопка Вход
};

export const BasePageLocators = {
    DISC_BTN: '[data-menu-xmlid="mail.menu_root_discuss"]', //Discuss
    SALE_BTN: '[data-menu-xmlid="sale.sale_menu_root"]', //Sales
    API_BTN: '[data-menu-xmlid="openapi.main_openapi_menu"]', //Open Api
    J_QUEUE_BTN: '[data-menu-xmlid="queue_job.menu_queue_job_root"]', //Job Queue
    YAWMS_BTN: 'a[data-menu-xmlid="lavka.integration_menu_root"]', // Yandex.WMS
    SALE_PR_BTN: '[data-menu-xmlid="lavka.sale_price_menu_root"]', // Sale prices
    PURCHASE_BTN: 'a[data-menu-xmlid="purchase.menu_purchase_root"]', // PURCHASE
    INVENT_BTN: '[data-menu-xmlid="stock.menu_stock_root"]', // Inventory
    INVOIC_BTN: '[data-menu-xmlid="account.menu_finance"]', // Invoicing
    DASH_BTN: '[data-menu-xmlid="base.menu_board_root"]', // Dashboards
    APP_BTN: '[data-menu-xmlid="base.menu_management"]', // Apps
    SETT_BTN: '[data-menu-xmlid="base.menu_administration"]', //Settings

    SC_ACT_BTN: 'a[data-menu-xmlid="lavka.scheduled_action"]' ,// Кнопка Scheduled Action
    YA_DOC_BTN: 'tr td[title="Ya.WMS Import Documents from WMS"]' ,// Ya.WMS Import Documents from WMS
    YA_PR_BTN: 'tr td[title="Ya.WMS Import Products from WMS"]' ,// Ya.WMS Import Products from WMS
    YA_WARE_BTN: 'tr td[title="Ya.WMS Import Warehouses from WMS"]' ,// Ya.WMS Import Warehouses from WMS
    YA_PUSH_BTN: 'tr td[title="Ya.WMS Push purchase orders to WMS"]' ,// Ya.WMS Push purchase orders to WMS
    ACTIVE_BTN: 'td div[name="active"]' ,// active
    RUN_BTN: 'button[nam:"method_direct_trigger"]' ,// run manualy
    SEARCH_FLD: 'input[placeholder="Search..."]' ,// фильтр
    SCACT_BTN: 'li[accesske:"b"] a' ,// Возврат в Scheduled Action
    CREATE_BTN:'button [title="Create"]',//

    MENU_BTN: 'a i[class="fa fa-th-large"]', // Меню выбора

    PROD_ID_FLD:'div[name="product_id"]',//Поле выбора продуктов для всех сущностей
    VALUE_FLD:'[name="value"]',//value
    EDIT_BTN:'button [title="Edit"]',// редактирование
    ACTION_BTN:'div.o_cp_action_menus > div:nth-child(2)',//ACTION
    ACTION_XP_BTN:'.//span[text()="Action"]',//ACTION_XPATH
    ARCHIVE_XP_BTN:'.//a[text()="Archive"]',//Archive_XPATH
    OK_XP_BTN:'.//span[text()="Ok"]',//Ok xpath
    DUPLICATE_XP_BTN:'.//a[text()="Duplicate"]',//Duplucate_xpath
    CANCEL_XP_BTN:".//a[text()='Сancel ']",//Cancel_xpath
    SAVE_XP_BTN:'.//span[text()="Save"]',//save
    SEND_WMS_BTN:'div.btn-group.o_dropdown.show > ul > li:nth-child(4)',//Send to WMS 
    AUTOTEST_BTN:'[data-menu-xmlid="lavka.autotests_menu_item"]',//Autotest
    SPIN:'[class="oe_blockui_spin"]',// поле загрузки импортов
    Che_PLQTY:'Check Plan QTY in wms',
    WARNING:'Warning',
    PASS:'111',
    AD_PASS:'admin',
    AUT_CANS_ORD_WMS_XP:'//td[text()="Ya.WMS Automatic cancellation of orders"]/preceding-sibling::td[@class="o_list_record_selector"]',//Ya.WMS Automatic cancellation of orders чекбокс
    DOC_WMS_XP:'//td[text()="Ya.WMS Import Documents from WMS"]/preceding-sibling::td[@class="o_list_record_selector"]',//Ya.WMS Import Documents from WMS чекбокс
    PROD_WMS_XP:'//td[text()="Ya.WMS Import Products from WMS"]/preceding-sibling::td[@class="o_list_record_selector"]/child::div',//Ya.WMS Import Products from WMS чекбокс
    WAREH_WMS_XP:'//td[text()="Ya.WMS Import Warehouses from WMS"]/preceding-sibling::td[@class="o_list_record_selector"]',//Ya.WMS Import Warehouses from WMS чекбокс
    RUN_MAN_BTN_XP:'//span[text()="Run Manually"]',//Run Manually XP
    CREAT_USER_BTN:'[data-menu-xmlid="lavka.autotest_create_users"]',//Create users
    BASE_VENDOR:'1_Vendortest',//базовый вендор для многих тестов
};

export const VendorsPageLocators = {
    VEND1_BTN: '[data-menu-xmlid="lavka.vendors_menuitem"]', // Vendor1 
    
    //Vendor//
    VEND2_BTN: 'a[data-menu-xmlid="purchase.menu_procurement_management_supplier_name"]', // Vendor2 
    CREATEVEN_BTN: 'i[title="Create"]', // Create
    VEND_NAME: 'input.o_input[placeholder="Name"]', // Name
    VEND_CITY: 'div.o_address_format input +[name="city"]', // City
    VEND_COUNT: 'div[name="country_id"]', // Country
    VEND_EMAIL: 'button[name="mail_action_blacklist_remove"] + input', // email
    VEND_TAX_ID: 'input.o_input[placeholder="e.g. 1234"]', // tax id
    LOGIN_VEND: 'span[name="name"]', // login
    ACTION_VEND: 'span.o_dropdown_title', // action
    DEL_VEND: ' div.o_cp_action_menus > div > ul > li:nth-child(3)', // delete
    OKDEL_VEND: 'div > div > footer > button.btn.btn-primary', // ok delete
    SP_BTN: "div.o_notebook > div.o_notebook_headers > ul > li:nth-child(2) > a", // Sales & Purchase
    Team_FLD: 'div[name="team_id"]', // Team поле
    Team_BTN: "//a[@clas:'ui-menu-item-wrapper ui-state-active']", // Team вып список (By.XPATH
    CONTACTS: 'Contacts & Addresses', // Contacts & Addresses text a
    ADD:'[title="Add"]',// +add 
    CONT_NAME_FLD:'[class="modal-body o_act_window"] input[class="o_field_char o_field_widget o_input o_required_modifier"]',//Contact name
    EMAILSAB_FLD:'[class="o_group o_inner_group o_group_col_5"] input[name="email"]',//Email
    SAVE_NEW_BTN:'Save & New',//Save & New text span
    DELIVERY_BTN:'Delivery Address',// Delivery Address text label
    SUB_VEN_NAME_FLD:'[class="o_field_char o_field_widget o_input"]',//Sub Vendor name
    S_CL_SABV_BTN:'Save & Close',//Save & Close text span
    REFERENCE_FLD:'[name="oebs_supplier_id"]',//Reference

    // OEBS
    OEBS_BTN:'[data-menu-xmlid="lavka.oebs_contract_menu"]',//OEBS contract
    SUPPLIER_FLD:'[name="oebs_supplier_id"]',//Supplier поле
    EXP_DATE_FLD:'input[name="export_date"]',// Export Date
    START_DATE_FLD:'input[name="start_date"]',//START DATE
    AGR_DATE_FLD:'input[name="agreement_date"]',//Agreement Date
    END_DATE_FLD:'input[name="end_date"]',//End Date

    // Переменные
    Name_Vendor1:'1_Vendortest', //логин вендора для первого теста
    Name_Vendor2:'2_Vendortest_in_sab', //логин вендора для второго теста
    City_UK:'London',
    Country_UK:'United Kingdom',
    Email_UK:'test@yandex.ru',
    Tax_ID_UK:'12345',
    Sub1:'Contsabv',//Contact name сабвендор
    Sub_Email1:'Contsabv@yandex.ruu',//Email Contact name сабвендор
    Sub2:'Delivsabv',//Deliv name сабвендор
    Sub_Email2:'Delivsabv@yandex.ruu',//Email Deliv name сабвендор
};

export const OrdersPageLocators = {
    ORDERS_BTN: '[data-menu-xmlid="purchase.menu_procurement_management"]',//Orders
        DRAFT_RFQS_BTN:'[data-menu-xmlid="lavka.menu_purchase_draft_rfq_menu"]',//Draft RFQs
        REGUEST_BTN: '[data-menu-xmlid="purchase.menu_purchase_rfq"]',//Requests for Quotation
        PURCH_ORD_BTN: 'ul.o_menu_sections > li.show > div > a:nth-child(4)', //Purchase order
        PURCH_ORD_LN_BTN: '[data-menu-xmlid="lavka.menu_purchase_order_line_menu"]',//Purchase Orders Lines
        CREAT_BILL_BTN: '[data-menu-xmlid="lavka.menu_creator_bill_menu"]',//Creator of bill
        TRANSF_OR_BTN:'[data-menu-xmlid="lavka.menu_stock_lavka_transfers"]', //Transfer Orders


    PRODUCT_BTN: '[data-menu-xmlid="purchase.menu_purchase_products"]',//Product
        PUR_ASS_MAT_BTN:'[data-menu-xmlid="lavka.purchase_assortment_matrix_menuitem"]',//Purchasing Assortment Matrix
        PRODUCT_PR_BTN:'[data-menu-xmlid="purchase.menu_procurement_partner_contact_form"]',//Product-Product

    VENDOR_BTN: '[data-menu-xmlid="lavka.vendors_menuitem"]',//Vendors
        VENDORS_BTN:'[data-menu-xmlid="purchase.menu_procurement_management_supplier_name"]',//Vendors
        PUR_AGR_BTN:'[data-menu-xmlid="purchase_requisition.menu_purchase_requisition_pro_mgt"]',//Purchase Agreements
        PUR_AGR_LINE_BTN:'[data-menu-xmlid="lavka.menu_purchase_requisition_line_menu"]',//Purchase Agreements Lines
        OEBS_CON_BTN:'[data-menu-xmlid="lavka.oebs_contract_menu"]',//OEBS contracts

    WAREHOUSES_BTN: '[data-menu-xmlid="lavka.purchase_warehouses"]',//WAREHOUSES

    AUTOORDER_BTN: '[data-menu-xmlid="lavka.autoorder_config_menuitem"]',//Autoorder
        DELIV_SHEDULE_BTN:'[data-menu-xmlid="lavka.delivery_shedule_menuitem"]',//Delivery Schedule
        SAFETY_ST_BTN:'[data-menu-xmlid="lavka.safety_stock_menuitem"]',//Safety Stock
        CORRECT_COEF_BTN:'[data-menu-xmlid="lavka.correction_coefficient_menuitem"]',//Correction Coefficient
        FIX_ORD_SET_BTN:'[data-menu-xmlid="lavka.fixed_order_menuitem"]',//Fixed Order Settings
        TASK_BTN:'[data-menu-xmlid="lavka.task_menuitem"]',//Task
        SUPPLY_CHAIN_BTN:'[data-menu-xmlid="lavka.purchase_suppply_chain_menuitem"]',//Supply chain
        TRANSIT_SET_BTN:'[data-menu-xmlid="lavka.purchase_cross_dock_pbl_menuitem"]',//Transit Settings
        AUTOORD_RESULT_BTN:'[data-menu-xmlid="lavka.autoorder_result_menuitem"]',//Autoorder Result
        EXP_TO_AUTOORD_BTN:'[data-menu-xmlid="lavka.autoorder_settings_menuitem"]',//Export To Autoorder
        DIST_CENTER_QUANT_BTN:'[data-menu-xmlid="lavka.menu_dc_quants"]',//Distribution Center Quants

    PURCHASE_INS_BTN: '[data-menu-xmlid="lavka.purchase_instruments"]',//Purchase Instruments
        IMPORT_ORDER_BTN:'[data-menu-xmlid="lavka.import_purchase_order"]',//Import Orders
        IMP_ORD_WITH_DELIV_BTN:'[data-menu-xmlid="lavka.import_purchase_order_delivery_type"]',//Import Orders with Delivery Type
        IMP_ASSORT_BTN:'[data-menu-xmlid="lavka.import_assortments"]',//Import Assortment
        IMP_SCHEDULE_BTN:'[data-menu-xmlid="lavka.import_schedule"]',//Import Schedule
        IMP_PROD_OUT_VAT_BTN:'[data-menu-xmlid="lavka.import_product_out_vat_menu"]',//Import Products out VAT
        IMP_SAFETY_ST_BTN:'[data-menu-xmlid="lavka.import_safety_stock"]',//Import Safety Stock
        IMP_REG_LINES_BTN:'[data-menu-xmlid="lavka.import_req_activity"]',//Import Req Lines Activity
        IMP_TRANSFER_BTN:'[data-menu-xmlid="lavka.import_transfers"]',//Import Transfers
        IMP_SUPP_CHAIN_BTN:'[data-menu-xmlid="lavka.import_supply_chain"]',//Import Supply Chain
        IMP_TRANSIT_SETT_BTN:'[data-menu-xmlid="lavka.import_transit_settings"]',//Import Transit Settings
        IMP_SUPP_QUANTS:'[data-menu-xmlid="lavka.import_supplier_quant"]',//Import Suppliers Quants

    TEAMS_BTN: '[data-menu-xmlid="lavka.lavka_team_config"]', // Teams
    REPORTING_BTN: '[data-menu-xmlid="purchase.purchase_report"]',//Reporting

    CONFIGURATION_BTN:'[data-menu-xmlid="purchase.menu_purchase_config"]',//Configuration
        SETTING_BTN:'[data-menu-xmlid="purchase.menu_purchase_general_settings"]',//Settings
        VENDOR_PRICE_BTN:'[data-menu-xmlid="purchase.menu_product_pricelist_action2_purchase"]',//Vendor Pricelists
        PURCH_AGR_TYPE_BTN:'[data-menu-xmlid="purchase_requisition.menu_purchase_requisition_type"]',//Purchase Agreement Types
        PRODUCT_CAT_BTN:'[data-menu-xmlid="purchase.menu_product_category_config_purchase"]',//Product Categories


    CREATE_ORD_BTN: 'button i[title="Create"]', // create
    IMPORT_ORD_BTN: '[class="btn btn-primary oe_import_order_button oe_highlight"]',//import
    
    Save_ORD_BTN: '[title="Save"]', // Save
    Vendor_ORD_BTN: "//a[contains(text(),'Vendortest ‒ 12345')]", // Vendor выпадающий список
    PurAg_ORD_FIELD: 'div[name="requisition_id"]', // Purchase Agreement поле
    DELIV_ORD_FIELD: 'div[name="picking_type_id"] input[type="text"]', // Deliver To поле
    PRODUCT_ORD_BTN_XP: '//a[text()="Add a product"]', // Выбор продукта Add a product XP
    PR_ORD_FIELD: 'div[name="product_id"] input', // поле выбора продукта
    RFG10_ORD_BTN: 'tr td input[name="product_init_qty"]', // RFQ Quantity
    PRINT_RFQ_BTN:'[name="print_quotation"][class="btn btn-primary"]',//Print RFQ
    CONF_ORD_BTN: 'div button[id="draft_confirm"]', // confirm
    DELI_ORD_TXT: 'Deli - Cudworth 25A: Receipts', // склад англии с тегом 'a'
    NUM_ORD_BTN:'table > tbody > tr:nth-child(1) > td.o_data_cell.o_field_cell.o_list_char.o_readonly_modifier.o_required_modifier.text-bf',//номер ордера
    COLOR_BTN:'table > tbody > tr:nth-child(1) > td:nth-child(5)',//селектор даты ордера для проверки цвета
    ORD_PRODUCT_BTN:'table > tbody > tr:nth-child(1) > td:nth-child(5)',//селектор ордера для проверки удаления продукта
    RES_DATE_BTN:'div[name="date_planned"] input[name="date_planned"]',//Receipt Date
    DRAFT_RFQ_BTN:'[class="breadcrumb-item o_back_button"]',//Draft RFQs
    DELIT_BTN:'[name="delete"]',//Delete
    NEW_RFQ_ORD_BTN:'tr:nth-child(1) > td.o_data_cell.o_field_cell.o_list_char.o_readonly_modifier.o_required_modifier.text-bf',//Последний созданный ордер в RFQ
    SEL_STATUS:'[title="Current state"]',//Селектор статуса ордера
    PRICE_FLD_XP:'//tr[@class="o_data_row o_selected_row"]/descendant::td[@title="5.25"]',//поле Unit Price в драфт ордере
    RFQ_FLD_XP:'//tr[@class="o_data_row"]/descendant::td[@title="30.0"][2]',//поле количества в ордере
    DUBL_OR_BTN_XP:".//span[text()='Duplicate']",//дубликат драфта ордера
    PRICE_SPAN_XP: ".//span[text()='5.25']",// элемент для проверки что цену нельзя редактировать

    //Переменные
    orange:'rgb(220, 165, 0)',//код оранжевого цвета
    gray:'rgb(76, 76, 76)',//код серого цвета
    red:'rgb(197, 34, 49)',//код красного цвета
    green:'rgb(61, 164, 115)',//зеленый цвет RFQ Sent

    // transfer
    TR_ORD_BTN:'[data-menu-xmlid="lavka.menu_stock_lavka_transfers"]',// transfer_orders
    WAREH_OUT_FLD:'[name="warehouse_out"]',// warehouse_out
    WAREH_IN_FLD:'[name="warehouse_in"]',// warehouse_in
    DATE_FLD:'div[name="date_planned"]',//Дата
    COL_FLD:'[name="qty_plan"]',//Количество товаров
    CREAT_OK_TXT:'[class="o_Message_prettyBody"]',// сообщение от бота что поле создано 'Lavka Transfer created'
    Ware_IN_77:'tbody > tr:nth-child(1) > td:nth-child(3) > span',//77 Queens Circus
    CHECK_PLAN_BTN:'[name="button_get_stocks_for_lines"]',//Check Plan QTY in wms
    SET_TO_DRAFT_BTN:'[name="set_to_draft"]',//Set To Draft
    APPROVE_ORDER_BTN:'[class="o_statusbar_buttons"] [name="button_approved"] span',//Approve Order
    CREATE_SHIP_BTN:'[name="button_send_shipment"]',//Create Shipment
    CURR_SENT:'[title="Current state"]',//активный статус трансфера
    CANCEL_BTN:'[name="button_cancel"]',//Cancel
    OK_TO_BTN:'div > div > footer > button',//Ок в модальном окне при ошибке в дате
    TR_ORD_ACTION_BTN:'[class="o_dropdown_title"]',//Action
    TR_ORD_DEL_BTN:' div.o_cp_action_menus > div > ul > li:nth-child(2)',//delete
    OK_TO_DEL_BTN:' div > footer > button.btn.btn-primary',//Ок в модальном окне при удалении
    TR_ORD_CANS_BTN:'[class="btn btn-secondary"]',//cansell в модальном окне при удалении
    TR_ACT_CANS_BTN:'div.o_cp_action_menus > div > ul > li:nth-child(3)',//cansell в action
    IMP_FR_EX_XP:'//span[text()="Import from Excel"]',//Import from Excel

    //Переменные
    WAREH_OUT1:'Deli - Cudworth 25A',
    WAREH_IN1:'77 Queens Circus',
    CREAT_OK_TXT1:'Lavka Transfer created',
    TOTAL_SUM: '$ 315.00',
    
    //Requests for Quotation
    REQ_F_Q_BTN:'[data-menu-xmlid="purchase.menu_purchase_rfq"]',//Requests for Quotation
    VEND_FLD:'[name="partner_id"]',//поле Vendor
    PURAG_FLD:'[name="requisition_id"]',//Purchase Agreement
    OK_TXT:'Ok',// OK c тегом span
    PUR_OK_TXT:'div:nth-child(3) > div.o_Message_core [class="o_Message_content"]',// сообщение от бота что поле создано 'Lavka Transfer created'

    // Локаторы для проверки статуса ордеров после запуска отмены просроченных
    ORD5:'tbody > tr:nth-child(11) > td.o_data_cell.o_field_cell.o_badge_cell.o_readonly_modifier > span',//Locked
    ORD4:'tbody > tr:nth-child(10) > td.o_data_cell.o_field_cell.o_badge_cell.o_readonly_modifier > span',//Cancelled
    ORD3:'tbody > tr:nth-child(9) > td.o_data_cell.o_field_cell.o_badge_cell.o_readonly_modifier > span',//RFQ Sent
    ORD2:'tbody > tr:nth-child(8) > td.o_data_cell.o_field_cell.o_badge_cell.o_readonly_modifier > span',//Locked
    ORD1:'tbody > tr:nth-child(7) > td.o_data_cell.o_field_cell.o_badge_cell.o_readonly_modifier > span',//Locked

    //Переменные
    PUR_OK_TXT1:'Purchase Order created',//сообщение от бота что поле создано 'Purchase Order created'

    //Draft RFQs
    DRAFT_BTN:'[data-menu-xmlid="lavka.menu_purchase_draft_rfq_menu"]',//Draft RFQs
    PO1:'span[name="name"]',//PO-211122-000001
};

export const WarePageLocators = {
    WARE_BTN: 'a[data-menu-xmlid="lavka.purchase_warehouses"]', // warehouses
    CREATE_WAREH_BTN: 'button i[title="Create"]', // create
    
    WARNING_BTN: 'footer button[type="button"]', // Warning
    WARE_FIELD: 'h1 input[name="name"]', // поле Warehouse
    CODE_FIELD: 'input[name="code"]', // поле Short Name
    WMS_ID_FIELD: 'input[name="wms_id"]', // поле wms_id
    LAV_AUT_BTN: 'div.o_notebook_headers > ul > li:nth-child(1) ', // Lavka.Autoorder
    WARE_TAGS_BTN: 'div[name="warehouse_tag_ids"] td a[role="button"]', // Add a line Warehouse Tags
    
    CREATE_WARTAG_BTN: 'button[type="button"][class="btn btn-primary"]', // create Add: Warehouse tags
    TYPE_BTN: '[class="o_group o_inner_group"] td [name="type"]', // TYPE Warehouse tags
    // VS_BTN: 'select[name="type"] option:nth-child(2)', // GEO
    VS_BTN: 'Geo', // GEO
    ASSORT_BTN: 'Assortment', //     Assortment
    NAME_FLD: 'td input[name="name"]', // NAME GEO
    SAVE_CLOSE_XP:"//span[text()='Save & Close']", // SAVE i Close XPATH
    PUR_TAGS_BTN: 'div[name="product_tag_ids"] a[role="button"]', // Add a line Purchase Assortments
    SAVE_BTN: 'button[type="button"] i[title="Save"]', // Save
    DELI_BTN:'td[title="Deli - Cudworth 25A"]', // выбор Английского склада для редактирования
    EDIT_BTN: 'button i[title="Edit"]',//Edit
    STOCK_FLD: 'tr[data-id="stock.warehouse.tag_2"] div', // чекбокс геометки
    SELECT_BTN: 'button[class="btn btn-primary o_select_button"]', // select
    SORTABLE_FLD: ' td.o_list_record_selector > div', // чекбокс ассортимента

    //Переменные
    GEO_UK:'UK',//Геометка для английского склада
    NAME_UK:'Test google maps',
    SHORT_NAME_UK:'23213211432423',
    WMS_ID_UK:'58809e91243c4bd6a7a2a700850aed9d000100020000',
    NAME_WH:'input[name="name"]',
    NAME_WMS:'input[name="wms_id"]',
    GEOUK:'geo: UK',
    ASSORT_UK:'assortment: UK',
};

export const AgrementsPageLocators = {
    PURAGR_BTN: 'a[data-menu-xmlid="purchase_requisition.menu_purchase_requisition_pro_mgt"]', // Purchase Agreements
    PURAG_XP:"//span[text()='Purchase Agreements']",//Purchase Agreements xpath
    PURAGR_LINES_BTN:'[data-menu-xmlid="lavka.menu_purchase_requisition_line_menu"]',//Purchase Agreements lines
    CREATE_PUAG_BTN: 'button i[title="Create"]', // Purchase Agreements create
    VENDOR_PUAG_FLD: 'div[name="vendor_id"] div input', // Vendor выбор в поле
    VEND_PUAG_BTN: "Vendortest", // Vendor выбор в выпадающем списке 
    ADD_A_LINETXT_BTN: 'div[name="line_ids"] td a[role="button"]', // add a line продуктов 
    ADD_A_LINE_BTN: 'div[name="warehouse_tag_ids"] td a[role="button"]', // Add a line геометки
    GEO_UK_BTN:'[title="geo: UK"]',//Выбор геометки 
    OEBS_CONT_FLD:'[name="oebs_contract_id"]',//OEBS Contract поле
    ALL_AGR_LIN_XP:'//th[@class="o_list_record_selector"]',//чекбокс выбора всех продуктов в агримент лайн
    APP_TAXES_XP:"//span[text()='Approve taxes']",//апрув такс в агримент лайн
    APP_PRICE_XP:"//span[text()='Approve prices']",//апрув прайс в агримент лайн
    ONE_AGR_XP:'//tr[@class="o_data_row"][1]',//выбираем первый агримент в списке

    PRODUCT_FLD: 'div[name="product_id"] input', // поле выбора продуктов
    UNIT_PR_FLD: 'td input[name="price_unit"]', // Unit Price
    VEND_TAX_FLD: 'div[name="tax_id"] input', // Vendor Tax
    TAX_15_BTN: "//a[normalize-space(:'Tax 15.00%']", // 15% tax By.XPATH
    START_D_FLD:'input[name="start_date"]',// start date
    END_D_FLD:'input[name="actual_end_date"]',//end date
    VEND_PRCODE_FLD: 'td input[name="product_code"]', // Vendor Product code
    APPROVE_ALL_BTN: 'button[name="approve_all_lines"]', // Approve all 
    LAV_AV_BTN: 'ul[class="nav nav-tabs"] a[class="nav-link"]', // Lavka.Autoorder 
    STOCK_FLD: 'tr[data-id="stock.warehouse.tag_2"] div', // чекбокс геометки
    SELECT_TAG_BTN: 'button[class="btn btn-primary o_select_button"]', // Select геометки 
    CONFIRM_BTN: 'button[name="action_in_progress"] span', // Confirm 
    SAVE_BTN: 'button[class="btn btn-primary o_form_button_save"]', // Save 

    IMP_LIN_BTN:'[class="fa fa-fw o_button_icon fa-cloud-upload"]', //Импорт документа с товарами
    NAME_FILE_BTN:'.o_input_file',//выбор файла для загрузки
    LOAD_F_BTN:'[name="load_lines"]',//загрузка файла
    OK_BTN:'[class="modal-content"] [class="btn btn-primary"]',// кнопка ок в сообщении что у вендора уже есть агримент
    APP_PR_BTN:'[name="set_approve_price"]',//approve_price
    //Переменные
    NAME_AGR1:'price_ag-v2.xlsx',// файл агримента
    NAME_AGR_390_1:'price_list_390-1.xlsx',// файл агримента 390-1
    NAME_AGR_390_2:'price_list_390-2.xlsx',// файл агримента 390-2
    NAME_AGR_390_3:'price_list_390-3.xlsx',// файл агримента 390-3
    NAME_AGR_390_4:'price_list_390-4.xlsx',// файл агримента 390-4 price_ag-v2_0%.xls
    NAME_AGR_LT_92_1:'price_ag-92_1.xlsx',// файл агримента LT_92_1 price_ag-v2_lt-35
    NAME_AGR_LT_35_1:'price_ag-v2_lt-35.xlsx',// файл агримента lt-35 
    NAME_AGR_LT_57_1:'price_ag-LT-57-1.xlsx',// файл агримента LT-57-1.xls
    NAME_AGR_LT_67_1:'agr_3_box_LT_67.xlsx',//файл агримента LT-67_1.xls
    NAME_AGR_LT_67_2:'agr_3_box_LT_67_2.xlsx',//файл агримента LT-67_2.xls
    NAME_AGR_LT_67_3:'agr_3_box_LT_67_3.xlsx',//файл агримента LT-67_3.xls
    NAME_AGR_LT_67_4:'agr_3_box_LT_67_4.xlsx',//файл агримента LT-67_4.xls
    PROD5:'tr:nth-child(5) > td.o_list_record_selector > div',//пятый и след продукты для апрува цены
    PROD6:'tr:nth-child(6) > td.o_list_record_selector > div',
    PROD7:'tr:nth-child(7) > td.o_list_record_selector > div',
    PROD1APP:'table > tbody > tr:nth-child(1) > td:nth-child(7) > div > input',//элементы для проверки отметки апрува прайса - первый чекбокс в списке
    PROD2APP:'table > tbody > tr:nth-child(1) > td:nth-child(13) > div > input',//элементы для проверки отметки апрува all - первый чекбокс в списке
    PROD3APP:'table > tbody > tr:nth-child(1) > td:nth-child(14) > div > input',//элементы для проверки отметки апрува tax - первый чекбокс в списке
    TABL_APPR_BTN:'[title="Approve Price"]',//сортировка по прайсу в таблице
    STR5:'tbody > tr:nth-child(5) > td.o_data_cell.o_field_cell.o_boolean_toggle_cell input',//Проверка чекбокса задача 390
    STR4:'tr:nth-child(4) > td.o_data_cell.o_field_cell.o_boolean_toggle_cell > div>input',//Проверка чекбокса задача 390
    STR2:'tr:nth-child(2) > td.o_data_cell.o_field_cell.o_boolean_toggle_cell > div>input',//Проверка чекбокса задача 390
    STR1:'tr:nth-child(1) > td.o_data_cell.o_field_cell.o_boolean_toggle_cell > div>input',//Проверка чекбокса задача 390
    STR67_3:'tr.o_data_row > td:nth-child(10)'//проверка строки в тестах LT_67
};

export const SettingsPageLocators = {
    SETTINGS_BTN: '[data-menu-xmlid="base.menu_administration"]', // Settings
    MAN_USER_TXT: '[class="btn btn-link o_web_settings_access_rights"] [class="fa fa-fw o_button_icon fa-arrow-right"]', // Manage Users 
    CREATE_BTN:'[title="Create"]',// Create
    NAME_FLD: '[name="name"]',//Name
    LOGIN_FLD:'[name="login"]',//Login
    SAVE_BTN:'[title="Save"]',//Save
    ACTION_TXT:'Action',//Action txt span
    CHA_PASS_XP:'//a[text()="Change Password"]',//Change Password
    NEW_PASS_FLD:'[class="o_data_cell o_field_cell o_list_char o_required_modifier"]',//New Password
    SAVE_PASSW_BTN:'[name="change_password_button"]',//Change Password
    USER_ROLE_SEL:'#notebook_page_990 > table:nth-child(3) > tbody > tr:nth-child(3) > td:nth-child(2)',//User Role
    CATMAN_XP:"//option[text()='Category manager']",//Category manager роль
};

export const AutoordPageLocators = {
    AUTOORD_BTN: '[data-menu-xmlid="lavka.autoorder_config_menuitem"]', // Autoorder
    DELIV_SH_BTN:'[data-menu-xmlid="lavka.delivery_shedule_menuitem"]',//Delivery Schedule
    VEND_ID:'[name="vendor_id"]',//Vendor
    DAYS_BO_FLD:'[name="days_before_order"]',//Days Before Order
    NAME_D_SH:'[class="breadcrumb-item active"]',//название нового ордера
    OR_WE2_BTN:'[name="order_weekday_2"]',//Order Weekdays Order on Wed
    OR_WE3_BTN:'[name="order_weekday_4"]',//Order Weekdays
    DE_WE_BTN:'[name="delivery_weekday_3"]',//Delivery Weekdays
    ADD_DELIV_BTN:'tbody > tr:nth-child(1) > td > a',//Add a line
    ORDER_DATE_FLD:'input[name="order_date"]',//Order Date
    DELIV_DATE_FLD:'input[name="delivery_date"]',//Delivery Date

    SAF_ST_BTN:'[data-menu-xmlid="lavka.safety_stock_menuitem"]',//safety_stock
    WAR_TAG_FLD:'div[name="warehouse_tag_ids"] div[name="warehouse_tag_ids"]',//выбор геометки
    WAR_ASS_FLD:'div[name="warehouse_product_tag_ids"] div[name="warehouse_product_tag_ids"]',//выбор ассортимента
    WAREH_FLD:'div[name="warehouse_ids"] div[name="warehouse_ids"]',//выбор склада из вып списка

    CORR_COEFF_BTN:'[data-menu-xmlid="lavka.correction_coefficient_menuitem"]',//Correction Coefficient
    START_D_FLD:'input[name="start_date"]',//Start date
    END_D_FLD:'input[name="end_date"]',//End date
    REASON_FLD:'[name="reason"]',//REASON
    WAREH_TAG_BTN:'div[name="warehouse_tag_id"]',//Target Warehouse Group
    VAL_FLD:'[name="value"]',//Value
    SAVE_BTN:'[title="Save"]',//сохранить
    
    FIX_ORD_SET_BTN:'[data-menu-xmlid="lavka.fixed_order_menuitem"]',//Fixed Order Settings
    MIN_ST_FLD:'input[name="min_stock"]',// Min Stock
    MAX_ST_FLD:'input[name="max_stock"]',//Max Stock

};

export const TeamsPageLocators = {
    TEAMS_BTN: '[data-menu-xmlid="lavka.lavka_team_config"]', // Teams
    SAL_TEA_FLD:'[name="name"]',//name Teams
    TEAM_LID_FLD:'[name="user_id"]',//Team Leader
    LID_BTN:'[class="ui-menu-item"]',//вып список 
    AD_MEM_TXT:'Add a member',// тег a
    USER_FLD:'div.table-responsive > table > tbody > tr:nth-child(1)',// клик по полю выбора юзеров
    VOICE_BTN1:'tr:nth-child(1) > td.o_data_cell.o_field_cell.o_boolean_toggle_cell > div',//кнопка назначить замом первого юзера
    DEL_BTN:'table > tbody > tr:nth-child(1) > td.o_list_record_remove > button',//удалить пользователя
    PURCHASE1:'[title="Purchase1"]',

    //Переменные
    User1:"User1",
};

export const ProductPageLocators = {
    PRODUCT_BTN: '[data-menu-xmlid="purchase.menu_purchase_products"]', // Products
    PRODUCT2_BTN:'[data-menu-xmlid="purchase.menu_procurement_partner_contact_form"]',// Products2
    XP_7UP_BTN:".//span[text()='7Up']",//продукт 7up xpath
};

export const PurInstPageLocators = {
    PUR_INSR_BTN:'[data-menu-xmlid="lavka.purchase_instruments"]',//Purchase Instruments
    IMP_TR_BTN:'[data-menu-xmlid="lavka.import_transfers"]',//Import Transfers
    IMP_PUR_OR_BTN:'[data-menu-xmlid="lavka.import_purchase_order"]',//Import Orders
    LOAD_BTN:'[name="load_orders"]',//кнопка загрузки файла ордера.
    LOAD_BTNSC:'[name="import_data"]',//кнопка загрузки файла Import Schedule
    IMP_SCH_BTN:'[data-menu-xmlid="lavka.import_schedule"]',//Import Schedule
};

export const InvoicPageLoc = {
    INVOICING_BTN:'[data-menu-xmlid="account.menu_finance"]',//Invoicing
        CUSTOMERS_BTN:'[data-menu-xmlid="account.menu_finance_receivables"]',//Customers
            INVOICES_BTN:'[data-menu-xmlid="account.menu_action_move_out_invoice_type"]',//Invoices
            CREDIT_NOTE_BTN:'[data-menu-xmlid="account.menu_action_move_out_refund_type"]',//Credit Notes
            PAYMENTS_BTN:'[data-menu-xmlid="account.menu_action_account_payments_receivable"]',//Payments
            PRODUCTS_BTN:'[data-menu-xmlid="account.product_product_menu_sellable"]',//Products
            CUSTOMERS_CUS_BTN:'[data-menu-xmlid="account.menu_account_customer"]',//Customers

        INVOIC_VEND_BTN:'[data-menu-xmlid="account.menu_finance_payables"]',//Vendors
            BILLS_BTN:'[data-menu-xmlid="account.menu_action_move_in_invoice_type"]',//Bills
            REFUNDS_BTN:'[data-menu-xmlid="account.menu_action_move_in_refund_type"]',//Refunds
            PAYMENTS_BTN:'[data-menu-xmlid="account.menu_action_account_payments_payable"]',//Payments
            INVOIC_PRODUCT_BTN:'[data-menu-xmlid="account.product_product_menu_purchasable"]',//Products
            VENDORS_BTN:'[data-menu-xmlid="account.menu_account_supplier"]',//Vendors

        REPORTING_BTN:'[data-menu-xmlid="account.menu_finance_reports"]',//Reporting
            INVOICE_ANALYSIS_BTN:'[data-menu-xmlid="account.menu_action_account_invoice_report_all"]',//Invoice Analysis

        INVOIC_CONF_BTN:'[data-menu-xmlid="account.menu_finance_configuration"]',//Сonfiguration
            SETTING_BTN:'[data-menu-xmlid="account.menu_account_config"]',//Settings
            PAY_TERMS_BTN:'[data-menu-xmlid="account.menu_action_payment_term_form"]',//Payment Terms
            INCOTERMS_BTN:'[data-menu-xmlid="account.menu_action_incoterm_open"]',//Incoterms
            ADD_A_BANK_BTN:'[data-menu-xmlid="account.menu_action_account_bank_journal_form"]',//Add a Bank Account
            RECON_MODEL_BTN:'[data-menu-xmlid="account.action_account_reconcile_model_menu"]',//Reconciliation Models
            TAXES_BTN:'[data-menu-xmlid="account.menu_action_tax_form"]',//Taxes
            JOURNAL_BTN:'[data-menu-xmlid="account.menu_action_account_journal_form"]',//Journals
            FISCAL_POS_BTN:'[data-menu-xmlid="account.menu_action_account_fiscal_position_form"]',//Fiscal Positions
            JOURNAL_GR_BTN:'[data-menu-xmlid="account.menu_action_account_journal_group_list"]',//Journal Groups
            PAYMENT_ACG_BTN:'[data-menu-xmlid="payment.payment_acquirer_menu"]',//Payment Acquirers
            PRODUCT_CAT_BTN:'[data-menu-xmlid="account.menu_product_product_categories"]',//Product Categories
            INPUT_BALANCES_BTN:'[data-menu-xmlid="lavka.menu_invoicing_input_balance"]',//Input Balances

    INVOIC_BILL_BTN:'[data-menu-xmlid="account.menu_action_move_in_invoice_type"]',//bill
    INVOIC_SEARCH_FLD:'[placeholder="Search..."]',//Search...
    INVOIC_REMOVE_BTN:'[title="Remove"]',//Remove в поле search
    INVOIC_FILTER_BTN:'[class="btn-group o_dropdown o_filter_menu"]',//filter
    INVOIC_TO_VAL_BTN:'To Validate',// To Validate-text
    INVOIC_PRODUCT1_XP:'//td[@title="178007"]/preceding-sibling::td[@class="o_list_record_selector"]',//чекбокс продукта для теста 522-1
    INVOIC_TAX_VAL_DEN_BTN:'[name="validation_failure"]',//Tax validation denied
    
    INVOIC_CONFIRM_BTN:'[name="approve"]:nth-child(1)',//confirm
    INVOIC_MANY_CONF_BTN:'[name="confirm"]',// confirm в окне оплаты
    INVOIC_TAX_BTN:'[data-menu-xmlid="account.menu_action_tax_form"]',//tax
    INVOIC_TAX_NAME_FLD:'[name="name"]',//tax name
    INVOIC_OEBS_TAX_FLD:'[name="oebs_tax_code"]',//tax code
    INVOIC_TAX_TIPE_BTN:'td [name="type_tax_use"]',//tax type
    INVOIC_AMOUNT_FLD:'[name="amount"]',//amount
    INVOIC_ZERO_BTN:'[title="0%"]',//нулевая ставка налога
    BILL_REF_FLD_XP:'//table[@class="o_group o_inner_group o_group_col_6"]//tr[8]//input[@class="o_field_char o_field_widget o_input"]',//Bill Reference поле xpath
    INVOIC_REG_PAY_BTN:'[id="account_invoice_payment_btn"]',//Register Payment
    INVOIC_CREATE_PAY_BTN:'[name="action_create_payments"]',//Create Payment
    CHECK_105:'//td[@title="PO105"]/preceding-sibling::td[@class="o_list_record_selector"]',//105 чекбокс
    CHECK_106:'//td[@title="PO106"]/preceding-sibling::td[@class="o_list_record_selector"]',
    CHECK_107:'//td[@title="PO107"]/preceding-sibling::td[@class="o_list_record_selector"]',
    CHECK_108:'//td[@title="PO108"]/preceding-sibling::td[@class="o_list_record_selector"]',
    CHECK_109:'//td[@title="PO109"]/preceding-sibling::td[@class="o_list_record_selector"]',
    CHECK_110:'//td[@title="PO110"]/preceding-sibling::td[@class="o_list_record_selector"]',
    CHECK_102:'//td[@title="PO102"]/preceding-sibling::td[@class="o_list_record_selector"]',
    CHECK_101:'//td[@title="PO101"]/preceding-sibling::td[@class="o_list_record_selector"]',

    BILL_PRICE_FLD_XP:'//div[@class="tab-pane active"]/descendant::td[@title="178002"]/following-sibling::td[text()="5.25"]',//поле с ценой в билле
    BILL_QUANT_FLD_XP:'//div[@class="tab-pane active"]/descendant::td[@title="178002"]/following-sibling::td[@title="5.0"][3]',//поле с количеством в билле
    APP_BILL_XP:'//li[@class="breadcrumb-item o_back_button"]',//открытие била из полей апрува изменений
    APPRUV_BTN_XP:"//a[text()='Approvals']",// кнопка открытия appruv
    CHECK_APP_XP_188_1:'//span[text()="Administrator"]/ancestor::tr[@class="o_data_row"]/descendant::div[@name="to_approve"]',//чекбокс апрува изменений количества
    CHECK_APP_XP_188_2:'//span[text()="User5"]/ancestor::tr[@class="o_data_row"]/descendant::div[@name="to_approve"]',//чекбокс апрува изменений цены
    CONFIRM_BTN_XP:"//span[text()='Confirm']",//confirm bill
    NEW_BILL_BTN:'[name="button_open_bills"]',// кнопка перехода к биллу после оплаты

    //TEXT
    CREATE_VEND_BILL_TXT:'Create Vendor Bills',
    IMP_FROM_EX_TXT:'Import from Excel',
    LOAD_LINE_FR_F_TXT:'Load lines from file',
    CONF_CHANGE_TXT:'Confirm Changes',
};

export const YandexWMSPageLoc = {
    WMS_BTN:'[data-menu-xmlid="lavka.wms_root_menu"]',//WMS
        ORDERS_BTN:'[data-menu-xmlid="lavka.orders"]',//Orders
        STOCK_LOGS_BTN:'[data-menu-xmlid="lavka.wms_stock_logs"]',//Stock Logs
        WMS_CURSOR_BTN:'[data-menu-xmlid="lavka.wms_stock_logs_cursors"',//WMS Cursors
        WMS_LOCKS_BTN:'[data-menu-xmlid="lavka.wms_locks"]',//WMS Locks

    QUEUE_BTN:'[data-menu-xmlid="lavka.job_queue_action_menu_item"]',//QUEUE
    SHEDULE_ACT_BTN:'[data-menu-xmlid="lavka.scheduled_action"]',//Scheduled Action
    SISTEM_PARAMETRS_BTN:'[data-menu-xmlid="lavka.sys_parameters"',//System Parameters
    APPROVALS_BTN:'[data-menu-xmlid="lavka.approval"]',//Approvals
    WAREHAUSES_BTN:'[data-menu-xmlid="lavka.warehouse_action"]',//Warehouses

    DOCUMENTS_BTN:'[data-menu-xmlid="lavka.documents_from_odoo"]',//Documents
        PURSHASE_ORD_BTN:'[data-menu-xmlid="lavka.purschase_orders_lavka"]',//Purchase Orders
        TRANSFER_ORD_BTN:'[data-menu-xmlid="lavka.transfer_lavka"]',//Transfer Orders
        PURSHASE_AGR_BTN:'[data-menu-xmlid="lavka.lavka_vendor_agreements_wms"]',//Purchase Agreements
        PURSHASE_AGR_LINE_BTN:'[data-menu-xmlid="lavka.lavka_vendor_agreements_lines"]',//Purchase Agreements Lines
        STOCK_MOVES_BTN:'[data-menu-xmlid="lavka.lavka_sale_prices"]',//Stock Moves
        SALE_ORDER_BTN:'[data-menu-xmlid="lavka.lavka_sale_orders"]',//Sale Order

    AUTOTESTS_BTN:'[data-menu-xmlid="lavka.autotests_menu_item"]',//Autotests
        CREATE_USERS_BTN:'[data-menu-xmlid="lavka.autotest_create_users"]',//Create users
};

export const SalesPageLoc = {
    ORDERS_BTN:'[data-menu-xmlid="sale.sale_order_menu"]',//Orders
        QUOTATION_BTN:'[data-menu-xmlid="sale.menu_sale_quotations"]',//Quotations
        ORDER_BTN:'[data-menu-xmlid="sale.menu_sale_order"]',//Orders
        SALES_TEAMS_BTN:'[data-menu-xmlid="sale.report_sales_team"]',//Sales Teams
        CUSTOMERS_BTN:'[data-menu-xmlid="sale.res_partner_menu"]',//Customers

    TO_INVOICE_BTN:'[data-menu-xmlid="sale.menu_sale_invoicing"]',//To Invoice
        ORD_TO_INV_BTN:'[data-menu-xmlid="sale.menu_sale_order_invoice"]',//Orders to Invoice
        ORD_TO_UPSELL:'[data-menu-xmlid="sale.menu_sale_order_upselling"]',//Orders to Upsell

    PRODUCT_BTN:'[data-menu-xmlid="sale.product_menu_catalog"]',//Products
        PRODUCTS_BTN:'[data-menu-xmlid="sale.menu_product_template_action"]',//Products

    REPORTING_BTN:'[data-menu-xmlid="sale.menu_sale_report"]',//Reporting
        SALES_BTN:'[data-menu-xmlid="sale.menu_report_product_all"]',//Sales

    CONFIG_BTN:'[data-menu-xmlid="sale.menu_sale_config"]',//Configuration
        SETTINGS_BTN:'[data-menu-xmlid="sale.menu_sale_general_settings"]',//Settings
        SALE_TEAM_BTN:'[data-menu-xmlid="sale.sales_team_config"]',//Sales Teams
        TAGS_BTN:'[data-menu-xmlid="sale.menu_tag_config"]',//Tags
};

export const OpenAPIPageLoc = {
    OPEN_API_BTN:'[data-menu-xmlid="openapi.openapi_menu"]',//OpenAPI
        INTEGRATIONS_BTN:'[data-menu-xmlid="openapi.namespaces_menu"]',//Intergrations
};

export const JobQueuePageLoc = {
    QUEUE_BTN:'[data-menu-xmlid="queue_job.menu_queue"]',//Queue
        JOBS_BTN:'[data-menu-xmlid="queue_job.menu_queue_job"]',//Jobs
        CHANNELS_BTN:'[data-menu-xmlid="queue_job.menu_queue_job_channel"]',//Channels
        JOB_FUNCT_BTN:'[data-menu-xmlid="queue_job.menu_queue_job_function"]',//Job Functions
};