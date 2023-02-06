import { HomePage } from '../../pageobjects/HomePage'
import { PurOrdersPage } from '../../pageobjects/OrdersPage'
import { AgremPage } from '../../pageobjects/AgremPage'
import {AuthPageLocators, BasePageLocators,OrdersPageLocators, WarePageLocators, AgrementsPageLocators} from '../../pageobjects/LocatorsPage'


describe('Тесты проверки джобы по отмене просроченных ордеров', () => {
    it.skip('LT-196-12 Запуск Ya.WMS Automatic cancellation of orders', () => {
        PurOrdersPage.Aut_Cansell_Orders()// Вводим количество, выбираем агримент
        // сейчас нельзя создать просроченные ордера
    });
})

describe('Тесты создания orders woody', () => {

    it('LT-203-1 Создание Purchase Agreements с файлом excel для тестов ордеров', () => { 
        AgremPage.Agrement_Create_xls("Еда1","Еда2",'Еда4','price_ag_203_1.xlsx')
        // лесенкой проверяем данные в агрименте, номер агримента,вводим имя файла для загрузки
        HomePage.clicks_on_the_button(BasePageLocators.EDIT_BTN)
        HomePage.two_clicks_in_the_fields(AgrementsPageLocators.LAV_AV_BTN,AgrementsPageLocators.ADD_A_LINE_BTN)//Выбираем геометку
        HomePage.elem_cycle_click(AgrementsPageLocators.GEO_UK_BTN)
        HomePage.elem_cycle_click(AgrementsPageLocators.SAVE_BTN)//Сохраняем 
        AgremPage.APP_ALL()
        });

    //нет кнопки загрузки ордера
    it.skip('LT-181-1 Создание orders при всех обязательных значениях', () => {
        PurOrdersPage.Pur_Ord_Create('import_purchase_orders_180_1.xlsx',OrdersPageLocators.TOTAL_SUM,'Nothing to Bill')
        // Выбираем файл,итоговая цена,статус
    });
    //нет кнопки загрузки ордера
    it.skip('LT-181-2 Создание orders у одного товара разные даты', () => {
        PurOrdersPage.Pur_Ord_Create('import_purchase_orders_180_2.xlsx',OrdersPageLocators.TOTAL_SUM,'$ 220.50')
        // Выбираем файл,две итоговых цены в ордерах
    });
    //нет кнопки загрузки ордера
    it.skip('LT-181-3 Создание orders и отправка в wms', () => {
        PurOrdersPage.Pur_Ord_Create('import_purchase_orders_180_1.xlsx',OrdersPageLocators.TOTAL_SUM,'Nothing to Bill')
        // Выбираем файл,итоговая цена,статус
        HomePage.contains_click('span',BasePageLocators.BASE_VENDOR)
        HomePage.elem_cycle_click(BasePageLocators.ACTION_BTN,BasePageLocators.SEND_WMS_BTN)
        HomePage.element_cycle('Sending purchase order')
    });
    //нет кнопки загрузки ордера
    it.skip('LT-148-1 Проверка создания Duplicate Draft RFQ', () => {
        PurOrdersPage.Draft_Duplicate_148_1('000009',OrdersPageLocators.TOTAL_SUM)
        //Выбираем ордер -- баг нет кнопки дубликат
    });
    //нет кнопки загрузки ордера
    it('LT-148-2 Проверка отмены PO Сancel', () => {
        PurOrdersPage.Pur_Ord_Create('import_purchase_orders_180_1.xlsx',OrdersPageLocators.TOTAL_SUM,'Nothing to Bill')
        // Выбираем файл,итоговая цена,статус
        HomePage.contains_click('span',BasePageLocators.BASE_VENDOR)
        HomePage.elem_cycle_click(BasePageLocators.ACTION_BTN)
        HomePage.xpath_elem_cycle_click(BasePageLocators.CANCEL_XP_BTN)
        HomePage.element_cycle('Edit','set to canceled')
    });
    //нет кнопки загрузки ордера
    it('LT_132_1 Проверка невозможности править цену', () => {
        PurOrdersPage.Dont_Edit_Price('import_purchase_orders_180_1.xlsx',OrdersPageLocators.TOTAL_SUM,'Nothing to Bill')
        // Выбираем файл,итоговая цена,статус
    });
    //нет кнопки загрузки ордера
    it.skip('LT_132_2 Проверка что возможно править количество товара', () => {
        PurOrdersPage.Edit_Price('import_purchase_orders_180_1.xlsx','$ 3,578,777.00','77,777.000')
        // Выбираем файл,итоговая цена,статус
    });
})

describe('Тесты создания transfer_orders woody', () => {
    it('LT-196-13 Создание transfer_orders при всех обязательных значениях', () => {
        PurOrdersPage.Pur_Transf_Create(OrdersPageLocators.WAREH_OUT1,OrdersPageLocators.WAREH_IN1,7,
                178001,24)// Склад откуда-куда,количество,сокращенное id продукта,часы к дате
    });

    it('LT-196-14 Добавление товаров в transfer_orders через файл', () => {
        PurOrdersPage.Pur_Transf_Edit_xls('transfer_ord_1.xlsx','178005','178001','178002')
    });

    it.skip('LE-458-1 Проверка отмены ордера имеющего статус shipment', () => {
        PurOrdersPage.Cansell_Transfer_Shipment(OrdersPageLocators.WAREH_OUT1,OrdersPageLocators.WAREH_IN1,7,
                178001,24)// Склад откуда-куда,количество,сокращенное id продукта,часы к дате
    });
        
    it('LE-589-1 Проверка невозможности создать ТО на вчерашнюю дату', () => {
        PurOrdersPage.Date_TO_Expiried(OrdersPageLocators.WAREH_OUT1,OrdersPageLocators.WAREH_IN1,999,
            178001,-24)// Склад откуда-куда,количество,сокращенное id продукта,часы к дате
    });

    it.skip('LE-589-2 Проверка невозможности создать ТО на вчерашнюю дату через файл', () => {
        PurOrdersPage.Date_TO_Expiried_xls(OrdersPageLocators.WAREH_OUT1,OrdersPageLocators.WAREH_IN1,-24
        )// Склад откуда-куда,часы к дате
        // баг.сейчас создать можно
    });

    it('LE-590-1 Проверка удаления ТО через delit', () => {
        PurOrdersPage.TransOrderDelit(OrdersPageLocators.WAREH_OUT1,OrdersPageLocators.WAREH_IN1,777,
                178001,24)// Склад откуда-куда,количество,сокращенное id продукта,часы к дате
    });

    it('LE-590-2 Проверка удаления ТО через delit - можно отменить удаление', () => {
        PurOrdersPage.TransOrderDelit(OrdersPageLocators.WAREH_OUT1,OrdersPageLocators.WAREH_IN1,666,
                178001,24)// Склад откуда-куда,количество,сокращенное id продукта,часы к дате
    });

    it('LE-590-3 Проверка отмены ТО через cansell из action', () => {
        PurOrdersPage.TransOrderDelit(OrdersPageLocators.WAREH_OUT1,OrdersPageLocators.WAREH_IN1,888,
                178001,24)// Склад откуда-куда,количество,сокращенное id продукта,часы к дате
    });
        
})

describe('Тесты создания Requests for Quotation woody', () => {
    it.skip('LT-181-4 Создание Requests for Quotation при всех обязательных значениях', () => {
        PurOrdersPage.Request_F_Quat_Create('import_purchase_orders_180_1.xlsx',OrdersPageLocators.TOTAL_SUM,'Nothing to Bill')
        // Выбираем файл,итоговая цена,статус
    });
})


describe('Тесты проверки невозможности редактирования номера ордера', () => {
    it.skip('LT-196-15 Тесты проверки невозможности редактирования номера ордера', () => {
        PurOrdersPage.Drafr_Not_Edit()
    });
})


describe('Тесты проверки цветовой индикации ордера', () => {
    it.skip('LT-196-16 Тесты проверки цветовой индикации ордера', () => {
        PurOrdersPage.Color_Date()
    });
})

//нет кнопки загрузки ордера
describe('Проверка на невозможность удаления товаров из ордера отправленного в wms', () => {
    it.skip('LT-196-17 Проверка на невозможность удаления товаров из ордера отправленного в wms', () => {
        PurOrdersPage.Not_Del_Product('000008')
        // выбираем ордер
    });
})
