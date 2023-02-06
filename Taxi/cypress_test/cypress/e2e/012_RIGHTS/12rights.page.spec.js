import { HomePage } from '../../pageobjects/HomePage'
import { InvoicingPage } from '../../pageobjects/InvoicingPage'
import { RightsPage } from '../../pageobjects/RightsPage'
import {AuthPageLocators, BasePageLocators,VendorsPageLocators,OrdersPageLocators,InvoicPageLoc} from '../../pageobjects/LocatorsPage'

describe('Тесты Проверки прав ADMIN', () => {
    it('LT-218-1 Проверка основных плашек главного меню', () => {
        RightsPage.Right_218_1('admin',BasePageLocators.AD_PASS)
        });

    it('LT-218-2 Проверяем что есть все элементы выбора основных разделов Purchase', () => {
        RightsPage.Right_218_2('admin',BasePageLocators.AD_PASS)
        });

        //баг нет поля Creator of bill
    it.skip('LT-218-3 Проверяем что есть все элементы выбора основных разделов Purchase - Orders', () => {
        RightsPage.Right_218_3('admin',BasePageLocators.AD_PASS)
        });

    it('LT-218-4 Проверяем что есть все элементы выбора основных разделов Purchase - Products', () => {
        RightsPage.Right_218_4('admin',BasePageLocators.AD_PASS)
        });

    it('LT-218-5 Проверяем что есть все элементы выбора основных разделов Purchase - Vendors', () => {
        RightsPage.Right_218_5('admin',BasePageLocators.AD_PASS)
        });

    it('LT-218-6 Проверяем что есть все элементы выбора основных разделов Purchase - Autoorder', () => {
        RightsPage.Right_218_6('admin',BasePageLocators.AD_PASS)
        });
    
    it('LT-218-7 Проверяем что есть все элементы выбора основных разделов Purchase - Purchase Instruments', () => {
        RightsPage.Right_218_7('admin',BasePageLocators.AD_PASS)
        });

    it('LT-218-8 Проверяем что есть все элементы выбора основных разделов Purchase - Configuration', () => {
        RightsPage.Right_218_8('admin',BasePageLocators.AD_PASS)
        });

    it('LT-219-1 Проверка основных меню верхнего ряда Yandex.WMS', () => {
        RightsPage.Right_219_1('admin',BasePageLocators.AD_PASS)
        });

    it('LT-219-2 Проверка основных меню Yandex.WMS - WMS', () => {
        RightsPage.Right_219_2('admin',BasePageLocators.AD_PASS)
        });

    it('LT-219-3 Проверка основных меню Yandex.WMS - Documents', () => {
        RightsPage.Right_219_3('admin',BasePageLocators.AD_PASS)
        });
    
    it('LT-219-4 Проверка основных меню Yandex.WMS - Autotests', () => {
        RightsPage.Right_219_4('admin',BasePageLocators.AD_PASS)
        });

    it('LT-233-1 Проверка что верхний ряд заполнен Invoicing', () => {
        RightsPage.Right_233_1('admin',BasePageLocators.AD_PASS)
        });
        
    it('LT-233-2 Проверка что в Invoicing-Customers есть все пункты', () => {
        RightsPage.Right_233_2('admin',BasePageLocators.AD_PASS)
        });

    it('LT-233-3 Проверка что в Invoicing-Vendors есть все пункты', () => {
        RightsPage.Right_233_3('admin',BasePageLocators.AD_PASS)
        });

    it('LT-233-4 Проверка что в Invoicing-Reporting есть все пункты', () => {
        RightsPage.Right_233_4('admin',BasePageLocators.AD_PASS)
        });

    it('LT-233-5 Проверка что в Invoicing-Configuration есть все пункты', () => {
        RightsPage.Right_233_5('admin',BasePageLocators.AD_PASS)
        });

    it('LT-236-1 Проверка что верхний ряд заполнен Sales', () => {
        RightsPage.Right_236_1('admin',BasePageLocators.AD_PASS)
        });

    it('LT-236-2 Проверка что в Sales-Orders есть все пункты', () => {
        RightsPage.Right_236_2('admin',BasePageLocators.AD_PASS)
        });

    it('LT-236-3 Проверка что в Sales-To Invoice есть все пункты', () => {
        RightsPage.Right_236_3('admin',BasePageLocators.AD_PASS)
        });

    it('LT-236-4 Проверка что в Sales-Products есть все пункты', () => {
        RightsPage.Right_236_4('admin',BasePageLocators.AD_PASS)
        });

    it('LT-236-5 Проверка что в Sales-Reporting есть все пункты', () => {
        RightsPage.Right_236_5('admin',BasePageLocators.AD_PASS)
        });

    it('LT-236-6 Проверка что в Sales-Configuration есть все пункты', () => {
        RightsPage.Right_236_6('admin',BasePageLocators.AD_PASS)
        });

    it('LT-237-1 Проверка есть все меню OpenAPI', () => {
        RightsPage.Right_237_1('admin',BasePageLocators.AD_PASS)
        });

    it(' LT-238-1 Проверка что верхний ряд заполнен Job Queue', () => {
        RightsPage.Right_238_1('admin',BasePageLocators.AD_PASS)
        });
        
    })


  