import {AuthPageLocators, BasePageLocators,OrdersPageLocators,VendorsPageLocators} from './LocatorsPage'
import { HomePage } from './HomePage'


export class VendorsPage {
    
    static VendorAuth() {
        HomePage.login()
        HomePage.elem_cycle_click(BasePageLocators.MENU_BTN,BasePageLocators.PURCHASE_BTN,VendorsPageLocators.VEND1_BTN)
        HomePage.clicks_on_the_button(VendorsPageLocators.VEND2_BTN) // vendor
        HomePage.not_odoo_error()
        };

    static OEBSAuth() {
        HomePage.login()
        HomePage.elem_cycle_click(BasePageLocators.MENU_BTN,BasePageLocators.PURCHASE_BTN,VendorsPageLocators.VEND1_BTN)
        HomePage.clicks_on_the_button(VendorsPageLocators.OEBS_BTN) // OEBS
        HomePage.not_odoo_error()
        };

    static VendorGreate(Vendor,City,Country,Email,Tax_ID) {
        VendorsPage.VendorAuth()
        HomePage.clicks_on_the_button(VendorsPageLocators.CREATEVEN_BTN)//create
        HomePage.find_click_and_fill_in(VendorsPageLocators.VEND_NAME,Vendor)// Name
        HomePage.find_click_and_fill_in(VendorsPageLocators.VEND_CITY,City)// City
        HomePage.click_write_enter(VendorsPageLocators.VEND_COUNT,Country)// Country
        HomePage.find_click_and_fill_in(VendorsPageLocators.VEND_EMAIL,Email)// email
        HomePage.find_click_and_fill_in(VendorsPageLocators.VEND_TAX_ID,Tax_ID)// Tax ID
        HomePage.two_clicks_in_the_fields(VendorsPageLocators.SP_BTN,VendorsPageLocators.Team_FLD)//Sales & Purchase,Team поле
        HomePage.enter_click()
        HomePage.not_odoo_error()         
        };

    // Создание sub_vendors к вендору
    static Sub_VendorGreate(Sub1,Sub_Email1,Sub2,Sub_Email2,tax_id) {
        VendorsPage.VendorGreate(VendorsPageLocators.Name_Vendor2,VendorsPageLocators.City_UK,VendorsPageLocators.Country_UK,
                VendorsPageLocators.Email_UK,tax_id)
        HomePage.contains_click('a',VendorsPageLocators.CONTACTS) //CONTACTS
        HomePage.clicks_on_the_button(VendorsPageLocators.ADD) //ADD
        HomePage.find_click_and_fill_in(VendorsPageLocators.CONT_NAME_FLD,Sub1)// Contact name
        HomePage.find_click_and_fill_in(VendorsPageLocators.EMAILSAB_FLD,Sub_Email1)// Email
        HomePage.contains_click('span',VendorsPageLocators.SAVE_NEW_BTN) //Save & New
        HomePage.contains_click('label',VendorsPageLocators.DELIVERY_BTN) //Delivery Address
        HomePage.find_click_and_fill_in(VendorsPageLocators.SUB_VEN_NAME_FLD,Sub2)// Contact name
        HomePage.find_click_and_fill_in(VendorsPageLocators.EMAILSAB_FLD,Sub_Email2)// Email
        HomePage.contains_click('span',VendorsPageLocators.S_CL_SABV_BTN) //Save & Close text span
        HomePage.clicks_on_the_button(OrdersPageLocators.Save_ORD_BTN)//save
        HomePage.element_cycle(Sub1,Sub2,VendorsPageLocators.Name_Vendor2,Sub_Email1,Sub_Email2) 
        HomePage.not_odoo_error()   
        };
    
    // Создание OEBS контракта
    static OEBSGreate(text,n) {
        VendorsPage.OEBSAuth()
        HomePage.clicks_on_the_button(VendorsPageLocators.CREATEVEN_BTN)//create
        HomePage.click_write_enter(VendorsPageLocators.SUPPLIER_FLD,text)
        HomePage.click_write_enter(VendorsPageLocators.EXP_DATE_FLD,HomePage.date_local_n(0))
        HomePage.click_write_enter(VendorsPageLocators.END_DATE_FLD,HomePage.date_local_n(n))
        HomePage.click_write_enter(VendorsPageLocators.START_DATE_FLD,HomePage.date_local_n(0))
        HomePage.click_write_enter(VendorsPageLocators.AGR_DATE_FLD,HomePage.date_local_n(0))
        HomePage.clicks_on_the_button(OrdersPageLocators.Save_ORD_BTN)//save
        HomePage.element_cycle(text,'Edit')  
        HomePage.not_odoo_error()
        };

    static VendorReference(name,contr) {
        VendorsPage.VendorAuth()
        HomePage.contains_click('span',name)
        HomePage.elem_cycle_click(BasePageLocators.EDIT_BTN,VendorsPageLocators.SP_BTN)
        HomePage.click_write_enter(VendorsPageLocators.REFERENCE_FLD,contr)
        HomePage.clicks_on_the_button(OrdersPageLocators.Save_ORD_BTN)//save
        HomePage.element_cycle(name,'Edit',contr) 
        HomePage.not_odoo_error()
        };

    static LT_59_2_VendorGreate() {
        VendorsPage.VendorGreate('Vendor-LT-59-2',VendorsPageLocators.City_UK,VendorsPageLocators.Country_UK,
        VendorsPageLocators.Email_UK,'77777')
        HomePage.elem_cycle_click(OrdersPageLocators.Save_ORD_BTN,BasePageLocators.EDIT_BTN)
        HomePage.contains_click('a',VendorsPageLocators.CONTACTS) //CONTACTS
        HomePage.clicks_on_the_button(VendorsPageLocators.ADD) //ADD
        HomePage.find_click_and_fill_in(VendorsPageLocators.CONT_NAME_FLD,'Sub1')// Contact name
        HomePage.find_click_and_fill_in(VendorsPageLocators.EMAILSAB_FLD,'Sub_Email1')// Email
        HomePage.contains_click('span',VendorsPageLocators.S_CL_SABV_BTN)
        HomePage.clicks_button_clear_enter(VendorsPageLocators.VEND_TAX_ID,'1234567')
        HomePage.clicks_on_the_button(OrdersPageLocators.Save_ORD_BTN)
        HomePage.element_cycle('Partner with Tax ID "1234567" already exists.')
        HomePage.reload()
        HomePage.xpath_elem_cycle_click(BasePageLocators.ACTION_XP_BTN,BasePageLocators.ARCHIVE_XP_BTN,BasePageLocators.OK_XP_BTN)
        HomePage.not_odoo_error()
        };

}
