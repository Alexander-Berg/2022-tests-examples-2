import { HomePage } from '../../pageobjects/HomePage'
import { AutoorderPage } from '../../pageobjects/AutoorderPage'
import {AuthPageLocators, BasePageLocators,OrdersPageLocators, WarePageLocators,AutoordPageLocators} from '../../pageobjects/LocatorsPage'


describe('Тесты создания Delivery Schedule', () => {
    it('LT-196-18 Создание Delivery Schedule при всех обязательных значениях', () => {
        AutoorderPage.Deliv_Schedule(7,'autoorder.delivery.schedule')
        //вводим количество дней,проверка создания ордера
        });

    it('LT-196-19 Создание Delivery Schedule при всех обязательных значениях и Order Exception Days', () => {
        AutoorderPage.Deliv_Schedule_EX_D(14,'autoorder.delivery.schedule',0,48)
        //вводим количество дней,проверка создания ордера,дни исключения заказа
        });

    it('LT-222_1 Проверка что Delivery Schedule нельзя создать без указания склада или геометки', () => {
        AutoorderPage.Deliv_Schedule_222_1(7)
        //вводим количество дней,проверка создания ордера,дни исключения заказа
        });

    it('LT-222_2 Создание Delivery Schedule при всех обязательных значениях и выборе склада', () => {
        AutoorderPage.Deliv_Schedule_222_2(7,'autoorder.delivery.schedule')
        //вводим количество дней,проверка создания ордера
        });
    })
    

describe('Тесты создания Safety Stock', () => {
    it('LT-196-20 Создание Safety Stock при всех обязательных значениях', () => {
        AutoorderPage.Safety_Stock(5,'autoorder.safety.stock')
        });
    })

describe('Тесты создания Correction Coefficient', () => {
    it('LT-196-21 Создание Correction Coefficient при всех обязательных значениях', () => {
        AutoorderPage.Corr_Coeff(48,1.5,'Новый год')
        });
    })

describe('Тесты создания Fixed Order Settings', () => {
    it('LT-196-22 Создание Fixed Order Settings при всех обязательных значениях', () => {
        AutoorderPage.Fix_Ord_Setting(10,40)
        });
    })
