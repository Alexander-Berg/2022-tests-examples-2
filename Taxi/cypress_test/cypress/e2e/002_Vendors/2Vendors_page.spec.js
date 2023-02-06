import { HomePage } from '../../pageobjects/HomePage'
import { VendorsPage } from '../../pageobjects/VendorPage'
import {AuthPageLocators, BasePageLocators,VendorsPageLocators,OrdersPageLocators} from '../../pageobjects/LocatorsPage'


describe('Тесты создания vendors woody', () => {
    it('LT-196-4 Создание vendors при всех обязательных значениях', () => {
        VendorsPage.VendorGreate(VendorsPageLocators.Name_Vendor1,VendorsPageLocators.City_UK,VendorsPageLocators.Country_UK,
            VendorsPageLocators.Email_UK,VendorsPageLocators.Tax_ID_UK)
        HomePage.clicks_on_the_button(OrdersPageLocators.Save_ORD_BTN)
        HomePage.cont_text(VendorsPageLocators.Name_Vendor1,'Edit')     
    });

    it('LT-196-5 Создание sub_vendors к вендору', () => {
        VendorsPage.Sub_VendorGreate(VendorsPageLocators.Sub1,VendorsPageLocators.Sub_Email1,VendorsPageLocators.Sub2,VendorsPageLocators.Sub_Email2,'1234567') 
    });
    
    it('Тест LT-59-1 Создаем вендора с TaxID == TaxID существующего вендора', () => {
        VendorsPage.VendorGreate(VendorsPageLocators.Name_Vendor1,VendorsPageLocators.City_UK,VendorsPageLocators.Country_UK,
            VendorsPageLocators.Email_UK,VendorsPageLocators.Tax_ID_UK)
        HomePage.clicks_on_the_button(OrdersPageLocators.Save_ORD_BTN)
        HomePage.element_cycle('Partner with Tax ID "12345" already exists.')  
    });

    it('Тест LT-59-2 Изменяем TaxID вендора == с существующего вендора', () => {
        VendorsPage.LT_59_2_VendorGreate()
    });

    it(' LT-59-3 Невозможность создать вендора с TaxID==TaxID вендора в архиве', () => {
        VendorsPage.VendorGreate(VendorsPageLocators.Name_Vendor1,VendorsPageLocators.City_UK,VendorsPageLocators.Country_UK,
            VendorsPageLocators.Email_UK,"77777")
        HomePage.clicks_on_the_button(OrdersPageLocators.Save_ORD_BTN)
        HomePage.element_cycle('Partner with Tax ID "77777" already exists.')  
    });

    it.skip('LT-196-6 Создание OEBS контракта', () => {
        VendorsPage.OEBSGreate('Контракт',48) //  название контракта и добавленное время
    });

    it.skip('LT-196-7 Привязка контракта к вендору', () => {
        VendorsPage.VendorReference('1_Vendortest','Контракт') //  кому добавляем контракт и название контракта
    });

})

    