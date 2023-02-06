import { HomePage } from '../../pageobjects/HomePage'
import { WarehausesPage } from '../../pageobjects/WarehPage'
import {AuthPageLocators, BasePageLocators,WarePageLocators} from '../../pageobjects/LocatorsPage'

// before(() => {
//     cy.exec('make drop_db')
//     cy.exec('make start_db')
// })

describe('Тесты создания склада woody', () => {
    it('LT-196-1 Активация полей WMS', () => {
            WarehausesPage.WarehAuthYAMS()           
        });
        
    it('LT-196-2 Редактирование Английского склада. Добавление геометок', () => {
            WarehausesPage.Wareh_GEO_ADD('UK',WarePageLocators.GEO_UK,WarePageLocators.ASSORT_UK)//геометка
        });

    it('LT-149-1 Проверка невозможности дубля геометки', () => {
        WarehausesPage.Wareh_GEO_NO_DOUBLE('UK')//геометка
    });

    it('LT-149-2 Проверка невозможности дубля метки ассортимента', () => {
        WarehausesPage.Wareh_ASSORT_NO_DOUBLE('UK')//метка ассортимента
    });

    it('LT-196-3 Проверка что невозможно создать новый склад и отредактировать название текущего', () => {
            WarehausesPage.Wareh_No_Create()
        });
})
