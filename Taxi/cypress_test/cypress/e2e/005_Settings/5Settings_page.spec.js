import { HomePage } from '../../pageobjects/HomePage'
import { PurOrdersPage } from '../../pageobjects/OrdersPage'
import { SettingsPage } from '../../pageobjects/SettingsPage'
import {AuthPageLocators, BasePageLocators,SettingsPageLocators} from '../../pageobjects/LocatorsPage'


describe('Тесты создания пользователей woody', () => {
    it.skip('LT_191_1 Создаем нового пользователя', () => {
        SettingsPage.CREATE_USER_191('USER_LT_191','USER191@yandex.ruu')
        // имя пользователя и емайл
    });

})

describe('Тесты проверки прав read only', () => {
    it.skip('LT-130-1 Автотесты на права read only - пользователь админ', () => { 
        SettingsPage.SettAuthReadOnly('RD_1',BasePageLocators.PASS)
        HomePage.elem_cycle_click(BasePageLocators.MENU_BTN)
        HomePage.contains_click('span','Job Queue')
        HomePage.cont_text('Jobs')
        // временно не работают юзеры кроме админа.убрать плашку тестового сервера.
    });

    it.skip('LT-130-2 Автотесты на права read only - пользователь аналитик', () => { 
        SettingsPage.SettAuthReadOnly('RD_2',BasePageLocators.PASS)
        // временно не работают юзеры кроме админа.убрать плашку тестового сервера.
    });
})
    
