import { HomePage } from '../../pageobjects/HomePage'
import { InvoicingPage } from '../../pageobjects/InvoicingPage'
import {AuthPageLocators, BasePageLocators,VendorsPageLocators,OrdersPageLocators,InvoicPageLoc} from '../../pageobjects/LocatorsPage'

describe('Тесты Vendors - Bills', () => {
    it('LT-144-1 Confirm и оплата билла - права админ', () => {
        InvoicingPage.Bill_Confirm_144_1('0000001','LT-144-1')
        //номер билла и код Bill Reference
        });

    it('LT-144-2 Confirm и оплата билла - права бухгалтер', () => {
        InvoicingPage.Bill_Confirm_144_2('Acc1',BasePageLocators.PASS,'0000002','LT-144-2')
        //номер билла и код Bill Reference
        });

    it('LT-144-3 Confirm и оплата билла утвержденного бухгалтером - права бухгалтер', () => {
        InvoicingPage.Bill_Confirm_144_3('Acc2',BasePageLocators.PASS,'0000002')
        //номер билла 
        });

    it('LT-124-1 Импорт копии ордера', () => {
        InvoicingPage.Bill_Import_124_1('LT_124_1','bill_LT_124_1.xlsx')
        //номер билла 
        });

    it.skip('LT-124-2 В билле изменили цену,количество,налог', () => {
        InvoicingPage.Bill_Import_124_2('LT_124_1','bill_LT_124_2.xlsx','88.75','104.69','15%')
        //номер билла -не изменяется ставка 20%
        });

    it('LT-124-3 В билле убрали строку', () => {
        InvoicingPage.Bill_Import_124_2('LT_124_1','bill_LT_124_3.xlsx','105.00','126.00','20%')
        //номер билла,файл
        });

    it('LT-124-4 Вводим неверную итоговую сумму в продукт', () => {
        InvoicingPage.Bill_Import_124_4('LT_124_1','bill_LT_124_4.xlsx','Vat in row: 5.25 Calculated: 6.0')
        //номер билла,файл
        });

    it('LT-158-1 Группировка по коду', () => {
        InvoicingPage.Bill_Group_158_1('LT_158_1','bill_LT_158_1.xlsx')
        //код,файл
        });

    it('LT-158-2 Удаление сгруппированного товара', () => {
        InvoicingPage.Bill_Group_158_2('LT_158_2','bill_LT_158_2.xlsx')
        //код,файл
        });

    it('LT-188-1 Проверка что можно апрувнуть измененения в билле', () => {
        InvoicingPage.Bill_Appruv_188_1('LT_188_1')
        //код
        });

    it('LT-188-2 Проверка что можно апрувнуть измененения в билле под менеджером', () => {
        InvoicingPage.Bill_Appruv_188_2('Acc2',BasePageLocators.PASS,'LT_188_1')
        //никнейм,пароль,код
        });

    it('LT-188-3 Проверка что можно апрувнуть измененения в билле через файл', () => {
        InvoicingPage.Bill_Appruv_188_3('LT_188_3','bill_LT_188_3.xlsx')
        //код,файл
        });

    it('LT-188-4 Проверка что можно апрувнуть измененения в билле из файла под менеджером', () => {
        InvoicingPage.Bill_Appruv_188_2('Acc2',BasePageLocators.PASS,'LT_188_3')
        //никнейм,пароль,код
        });
    

})