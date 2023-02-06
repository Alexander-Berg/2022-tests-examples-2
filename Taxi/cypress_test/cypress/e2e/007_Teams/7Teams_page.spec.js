import { HomePage } from '../../pageobjects/HomePage'
import { TeamsPage } from '../../pageobjects/TeamsPage'
import {AuthPageLocators, BasePageLocators,OrdersPageLocators, WarePageLocators,TeamsPageLocators, AgrementsPageLocators} from '../../pageobjects/LocatorsPage'


describe('Создание teams при всех обязательных значениях', () => {
    it('LT-196-23 Создание teams при всех обязательных значениях', () => {
            TeamsPage.TeamsCreate('Testqr','Administrator','Admin2')// название группы, лидер, пользователь
        });
        
    it('LT-196-24 Редактирование teams - удаление пользователя из группы', () => {
            TeamsPage.TeamsEdit('Testqr','Admin2')// название группы, пользователь который будет удален
        });

    })


describe('Тесты прав в группе', () => {
    it('LT-196-25 Создание teams Purchase1 при всех обязательных значениях', () => {
        TeamsPage.TeamsCreate_Purchase('Purchase1','Admin2','Catman4','Commerce5')
        // название группы, лидер, пользователи
    });

    // ошибка.убрать плашку тестового сервера
    it.skip('LT-196-26 Смена группы у вендора', () => {
        TeamsPage.TEAM_VEND_ADD('User1',BasePageLocators.PASS,'2_Vendortest_in_sab','Purchase1','price_ag-v2.xlsx')
        // ник,пароль,вендор,название группы,название файла
    });
     // ошибка.убрать плашку тестового сервера
    it.skip('LT-196-27 Создание под User1 агримента апрув прайс', () => {
        TeamsPage.TEAM_AGR_USER1('User1',BasePageLocators.PASS,'2_Vendortest_in_sab','price_ag-v2.xlsx')
        // ник,пароль,вендор,название группы,название файла
    });
     // ошибка.убрать плашку тестового сервера
    it.skip('LT-196-28 Апрувим прайс продуктов под User2', () => {
        TeamsPage.TeamsApprov_price('User2',BasePageLocators.PASS)
        // ник,пароль
    });
     // ошибка.убрать плашку тестового сервера
    it.skip('LT-196-29 Заливаем новые цены под User3', () => {
        TeamsPage.NEW_price('User3',BasePageLocators.PASS,'Admin2','price_ag-v3.xlsx','55','66','77')
        // ник,пароль,ник для прайса,агримент
    });
     // ошибка.убрать плашку тестового сервера
    it.skip('LT-196-30 Апрувим прайс продуктов-1', () => {
        TeamsPage.TeamsApprov_price2('User2',BasePageLocators.PASS,AgrementsPageLocators.PROD7APP)
        // ник,пароль
    });
     // ошибка.убрать плашку тестового сервера
    it.skip('LT-196-31 Апрувим прайс продуктов-2', () => {//блок ошибкой
        TeamsPage.TeamsApprov_price3('User1',BasePageLocators.PASS)
        // ник,пароль
    });
     // ошибка.убрать плашку тестового сервера
    it.skip('LT-196-32 Проверяем что User3 не видит кнопки approve price', () => {
        TeamsPage.TeamsNot_Approv_price('User3',BasePageLocators.PASS)
        // ник,пароль
    });

    //блок багом.сейчас кнопка видна
    it.skip('LT-196-33 Проверяем что User2 и User3 не могут редактировать группу', () => {
        TeamsPage.TeamsNot_Edit('User2',BasePageLocators.PASS,'Purchase1','User3',BasePageLocators.PASS)
        // ник,пароль
    });
     // ошибка.убрать плашку тестового сервера
    it.skip('LT-196-34 Проверка что user может быть только в одной группе', () => {
        TeamsPage. TeamsCreate_Purchase2('User1',BasePageLocators.PASS,'Purchase2','User2',TeamsPageLocators.PURCHASE1)
        // ник,пароль
    });

    //блок багом.сейчас кнопка видна
    it.skip('LT-196-35 Потеря прав лидером на редактирование группы после смены лидера', () => {
        TeamsPage.TeamsNot_Edit_Lid('User1',BasePageLocators.PASS,'Purchase1','User3')
        // ник,пароль,название группы
    });

    })

   