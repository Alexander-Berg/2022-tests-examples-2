import { HomePage } from '../../pageobjects/HomePage'
import { InvoicingPage } from '../../pageobjects/InvoicingPage'
import {AuthPageLocators, BasePageLocators,AgrementsPageLocators,InvoicPageLoc, ProductPageLocators} from '../../pageobjects/LocatorsPage'
import { AgremPage } from '../../pageobjects/AgremPage'


describe('Тесты страницы ордеров', () => {
    it('LT-71-1 Информирование об отмене налоговой ставки продукта', () => {
        InvoicingPage.InvoisingTaxNotValidate('BO00001')//вводим проверочное название агримента
    });
    
    it('LT-196-8 Создание Purchase Agreements при всех обязательных значениях', () => {
        AgremPage.AgremCreate('BO00002',15,12345)//вводим проверочное название агримента цену и код
    });

    it('LT-196-9 Создание Purchase Agreements при всех обязательных значениях с файлом excel', () => { 
        AgremPage.Agrement_Create_xls(60,66,'Еда1',AgrementsPageLocators.NAME_AGR1)
        // лесенкой проверяем данные в агрименте, номер агримента,вводим имя файла для загрузки
        });

    it('LT-196-10 Аппрув агримента и добавление геометки', () => { 
        AgremPage.AgremEdit_1('BO00003','geo: UK')
        // номер агримента,выбор геометки
        });

    it('LT-180-1 Создание Purchase Agreements при дубле в файле excel с разными датами', () => { 
        AgremPage.Agrement_Create_xls_duble('Еда1','Еда3','price_agrem_dubl.xlsx')
        // вводим имя файла для загрузки
        });

    it('LE-390-1 Создание Purchase Agreements при всех обязательных значениях с файлом excel - некоторые строки неактивны', () => { 
        AgremPage.Agrement_Active_and_not_active(100,77,'Еда1',AgrementsPageLocators.NAME_AGR_390_1)
        // лесенкой проверяем данные в агрименте, номер агримента,вводим имя файла для загрузки
        });

    it('LE-390-2 Изменение цен в существующем агрименте.Строки неактивны', () => { 
        AgremPage.AgremEdit_390_2('BO00005',AgrementsPageLocators.NAME_AGR_390_2,'88','111',
        AgrementsPageLocators.STR5,AgrementsPageLocators.STR4,'not.be.checked')
        // номер агримента,файл,цены,checkbox1-2,meaning-значение чекбокса
        });

    it('LE-390-3 Изменение цен в существующем агрименте.Строки активны', () => { 
        AgremPage.AgremEdit_390_2('BO00005',AgrementsPageLocators.NAME_AGR_390_3,'775','99',
        AgrementsPageLocators.STR1,AgrementsPageLocators.STR2,'be.checked')
        // номер агримента,файл,цены,checkbox1-2,meaning-значение чекбокса
        });

    it('LE-390-4 Изменение активности строк в агрименте', () => { 
        AgremPage.AgremEdit_390_4('BO00005',AgrementsPageLocators.NAME_AGR_390_4)
        // номер агримента,файл
        });

    it.skip('LT-92-1 Создание агримента через файл.Есть нулевые ставки налога', () => { 
        AgremPage.Agrement_Create_xls_0taxes(AgrementsPageLocators.NAME_AGR_LT_92_1,
            "Couldn't find the tax with value '0.0' and type 'purchase' in woody. Product: 178001")
        });

    it('LT-92-2 Создаем нулевую ставку налога', () => { 
        InvoicingPage.InvoiTaxesEdit_0(InvoicPageLoc.INVOIC_ZERO_BTN,0)
        // вводим название и ставку налога
        });

    it.skip('LT-92-3 Создание агримента через файл.Есть нулевые ставки налога.Проверка что ставка принята', () => { 
        AgremPage.Agrement_Create_xls_0taxes_True(AgrementsPageLocators.NAME_AGR_LT_92_1,
            "Price list attach")
        });

    it('LT-58-1 Проверка отсутствия поля create в OEBS контракт', () => { 
        AgremPage.Agrem_Not_OEBS_Create('BO00003')
        // номер агримента,выбор геометки
        });

    it.skip('LT-35-1 Создание агримента с нулевой ставкой налога', () => { 
        AgremPage.Agrement_Create_xls(777,'Вода','634973',AgrementsPageLocators.NAME_AGR_LT_35_1)
        // лесенкой проверяем данные в агрименте, номер агримента,вводим имя файла для загрузки
        HomePage.elem_cycle_click(ProductPageLocators.PRODUCT_BTN,ProductPageLocators.PRODUCT2_BTN)
        HomePage.clicks_button_clear_enter(BasePageLocators.SEARCH_FLD,'634973')
        HomePage.xpath_clicks_on_the_button(ProductPageLocators.XP_7UP_BTN)
        HomePage.element_cycle('New customer Taxes:')
        });

    it.skip('LT-57-1 Создание Purchase Agreements через файл с данными записанными различным методом', () => { 
        AgremPage.Agrement_Create_xls(5.5,40,'Tax 15.00%',AgrementsPageLocators.NAME_AGR_LT_57_1)
        // лесенкой проверяем данные в агрименте, номер агримента,вводим имя файла для загрузки
        });

    it.skip('LT-196-11 Создание Purchase Agreements при пустой ставке в файле', () => { 
        AgremPage.Agrement_Create_180_2('User Error',
        "Errors while loading prices:",'imp_pur_agr_LT_57_5.xlsx')
        // проверяем надписи в ошибке,вводим имя файла для загрузки
        });

    it('LT-67-1 создаем агримент с заполненным полем qty_in_box', () => { 
        AgremPage.Agrement_Create_xls(50,15,'Продукт-LT-67',AgrementsPageLocators.NAME_AGR_LT_67_1)
        // лесенкой проверяем данные в агрименте, номер агримента,вводим имя файла для загрузки
        AgremPage.APP_ALL()
    });

    it('LT-67-2 создаем агримент с заполненным полем qty_in_box: qty_multiple не кратно qty_in_box', () => { 
        AgremPage.Agrement_Create_xls_0taxes(AgrementsPageLocators.NAME_AGR_LT_67_2,
            '"Vendor Quantity Multiple" 1.0 is not multiple by "Vendor Quantity in Box" 5.0')
    });

    //баг, нет автоподстановки в поле 
    it.skip('LT-67-3 создаем агримент с заполненным полем qty_in_box == 0 Проверяем что поле изменилось на 1', () => { 
        AgremPage.Agrement_Create_xls('LT-67_3',15,'Продукт-LT-67_3',AgrementsPageLocators.NAME_AGR_LT_67_3)
        // лесенкой проверяем данные в агрименте, номер агримента,вводим имя файла для загрузки
        HomePage.should_text(AgrementsPageLocators.STR67_3,'1.0')
        AgremPage.APP_ALL()
    });
    
    it.skip('LT-67-4 создаем агримент с пустым полем qty_in_box Проверяем что поле изменилось на 1', () => { 
        AgremPage.Agrement_Create_xls('LT-67_4',15,'Продукт-LT-67_4',AgrementsPageLocators.NAME_AGR_LT_67_4)
        // лесенкой проверяем данные в агрименте, номер агримента,вводим имя файла для загрузки
        HomePage.should_text(AgrementsPageLocators.STR67_3,'1.0')
        AgremPage.APP_ALL()
    });

})

    
