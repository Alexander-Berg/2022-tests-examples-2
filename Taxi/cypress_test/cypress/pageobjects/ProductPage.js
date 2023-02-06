import {AuthPageLocators, BasePageLocators,OrdersPageLocators,ProductPageLocators} from './LocatorsPage'
import { HomePage } from './HomePage'


export class ProductPage {
    
    static ProductAuth() {
        HomePage.login()
        HomePage.clicks_on_the_button(BasePageLocators.MENU_BTN)
        HomePage.clicks_on_the_button(BasePageLocators.PURCHASE_BTN)
        HomePage.clicks_on_the_button(ProductPageLocators.PRODUCT_BTN) // Product
    };

    static No_Create() {
        ProductPage.ProductAuth()
        HomePage.clicks_on_the_button(ProductPageLocators.PRODUCT2_BTN)
        HomePage.not_cont_text('Create')
    };

}
