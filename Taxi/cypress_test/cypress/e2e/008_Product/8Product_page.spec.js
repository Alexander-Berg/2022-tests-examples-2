import { HomePage } from '../../pageobjects/HomePage'
import { ProductPage } from '../../pageobjects/ProductPage'
import {AuthPageLocators, BasePageLocators,OrdersPageLocators, WarePageLocators,TeamsPageLocators} from '../../pageobjects/LocatorsPage'


describe('Проверка что невозможно создать продукт', () => {
    it('LT-196-36 Проверка что невозможно создать продукт', () => {
        ProductPage.No_Create()
        });
})