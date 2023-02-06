import { HomePage } from '../../pageobjects/HomePage'
import { PurInstPage } from '../../pageobjects/PurchInstrPage'
import {AuthPageLocators, BasePageLocators,VendorsPageLocators,OrdersPageLocators} from '../../pageobjects/LocatorsPage'


describe('Тесты Purchase Instruments - Import Transfers', () => {
    it('LT-196-37 Создание Import Transfers товара в файле меньше чем на складе', () => {
        PurInstPage.Create_TR('import_transfer.xlsx','Deli - Cudworth 25A','77 Queens Circus')//Название файла который грузим,склады откуда и куда      
        });

    it('LT-196-38 Создание Import Transfers товара в файле больше чем на складе', () => {
        PurInstPage.Create_TR_MAX('import_transfer_2.xlsx','Deli - Cudworth 25A','77 Queens Circus')//Название файла который грузим,склады откуда и куда      
        });
})

describe('Тесты Purchase Instruments - Import Orders', () => {
    it('LT-196-39 Создание Import Orders все данные валидны', () => {
        PurInstPage.Create_PUR_OR('import_purchase_orders.xlsx','315.00')
        //Название файла который грузим,итоговая сумма
        });

    it('LT-57-1 Создание Import Orders все данные валидны в файле разные даты', () => {
        PurInstPage.Create_PUR_OR_N('import_purchase_orders_date_n.xlsx','126.00')
        //Название файла который грузим,итоговая сумма
        });

    it('LT-57-2 Создание Import Orders с пустой строкой в файле', () => {
        PurInstPage.Create_PUR_OR('imp_pur_ord_LT_57_2.xlsx',"Warning: 'qty_multiple' with value '0'. Product: 178002. Will not be created")
        //Название файла который грузим,сообщение об нулевой строке
        });

    it('LT-57-3 Создание Import Orders с датой больше чем год от сегодня', () => {
        PurInstPage.Create_PUR_OR_LT_57_3_4('imp_pur_ord_LT_57_3.xlsx',"Wrong date '2024-12-29 00:00:00'. Date more than one year.Product: 178001")
        //Название файла который грузим,сообщение об нулевой строке
        });

    it('LT-57-4 Создание Import Orders с одной строкой с нулевым количеством', () => {
        PurInstPage.Create_PUR_OR_LT_57_3_4('imp_pur_ord_LT_54_4.xlsx',"Zero quantity in all lines")
        //Название файла который грузим,сообщение об нулевой строке
        });

    it('LT-196-40 Создание Import Schedule из файла с валидными значениями', () => {
        PurInstPage.Create_IMP_SCH('import_delivery_schedules541.xlsx','geo: UK','Deli - Cudworth 25A','77','88')
        //Название файла который грузим,итоговая сумма
        });
    
})


