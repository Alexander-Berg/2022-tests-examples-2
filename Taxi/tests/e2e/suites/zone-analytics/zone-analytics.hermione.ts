import {clickObjectOnMap, openPageAndWaitRendered} from 'tests/e2e/utils/map-actions';
import {describe, expect, it} from 'tests/hermione.globals';

import {MapEntity} from 'client/store/entities/types';
import {AnalystEntity} from 'types/analyst';
import {MapMenuAnalyticTestId} from 'types/test-id';

import {
    assertEntityDescription,
    currencyFormatter,
    numberFormatter,
    replaceNbsp,
    toggleSectionAudience,
    toggleSectionEda,
    toggleSectionLavka,
    toggleSectionTaxi
} from './utils';

describe('Аналитика зон', function () {
    afterEach(async function (this) {
        await this.browser.execute('window.localStorage.clear()');
    });

    it('Расчет целевой аудитории черновика зоны', async function () {
        await openPageAndWaitRendered(this);

        await clickObjectOnMap(this, MapEntity.ZONE_DRAFTS, '5');

        await toggleSectionAudience(this);

        const itemValue = await this.browser.assertBySelector(MapMenuAnalyticTestId.ITEM_VALUE_TARGET_AUDIENCE);

        expect(await itemValue.getText()).to.include(replaceNbsp(numberFormatter.format(1145)));
    });

    it('Расчет общей аудитории черновика зоны', async function () {
        await openPageAndWaitRendered(this);

        await clickObjectOnMap(this, MapEntity.ZONE_DRAFTS, '5');

        await toggleSectionAudience(this);

        const itemValue = await this.browser.assertBySelector(MapMenuAnalyticTestId.ITEM_VALUE_TOTAL_AUDIENCE);

        expect(await itemValue.getText()).to.include(replaceNbsp(numberFormatter.format(12588)));
    });

    it('Расчет цены за метр черновика зоны', async function () {
        await openPageAndWaitRendered(this);

        await clickObjectOnMap(this, MapEntity.ZONE_DRAFTS, '5');

        await toggleSectionAudience(this);

        const itemValue = await this.browser.assertBySelector(MapMenuAnalyticTestId.ITEM_VALUE_COST_ON_METER);

        expect(await itemValue.getText()).to.include(replaceNbsp(currencyFormatter.format(139367.67)));
    });

    it('Расчет количества заказов Такси и среднего чека Такси черновика зоны', async function () {
        await openPageAndWaitRendered(this);

        await clickObjectOnMap(this, MapEntity.ZONE_DRAFTS, '5');

        await toggleSectionTaxi(this);

        const ordersItemValue = await this.browser.assertBySelector(MapMenuAnalyticTestId.ITEM_VALUE_TAXI_ORDERS);
        const averageItemValue = await this.browser.assertBySelector(
            MapMenuAnalyticTestId.ITEM_VALUE_TAXI_AVERAGE_RECEIPT
        );

        expect(await ordersItemValue.getText()).to.include(replaceNbsp(numberFormatter.format(288)));
        expect(await averageItemValue.getText()).to.include(replaceNbsp(currencyFormatter.format(377.55)));
    });

    it('Расчет количества заказов Лавки и среднего чека Лавки черновика зоны', async function () {
        await openPageAndWaitRendered(this);

        await clickObjectOnMap(this, MapEntity.ZONE_DRAFTS, '5');

        await toggleSectionLavka(this);

        const ordersItemValue = await this.browser.assertBySelector(MapMenuAnalyticTestId.ITEM_VALUE_DELI_ORDERS);
        const averageItemValue = await this.browser.assertBySelector(
            MapMenuAnalyticTestId.ITEM_VALUE_DELI_AVERAGE_RECEIPT
        );

        expect(await ordersItemValue.getText()).to.include(replaceNbsp(numberFormatter.format(6)));
        expect(await averageItemValue.getText()).to.include(replaceNbsp(currencyFormatter.format(1016)));
    });

    it('Расчет количества заказов Еды и среднего чека Еды черновика зоны', async function () {
        await openPageAndWaitRendered(this);

        await clickObjectOnMap(this, MapEntity.ZONE_DRAFTS, '5');

        await toggleSectionEda(this);

        const ordersItemValue = await this.browser.assertBySelector(MapMenuAnalyticTestId.ITEM_VALUE_MEAL_ORDERS);
        const averageItemValue = await this.browser.assertBySelector(
            MapMenuAnalyticTestId.ITEM_VALUE_MEAL_AVERAGE_RECEIPT
        );

        expect(await ordersItemValue.getText()).to.include(replaceNbsp(numberFormatter.format(11)));
        expect(await averageItemValue.getText()).to.include(replaceNbsp(currencyFormatter.format(1439.09)));
    });

    it('Расчет целевой аудитории зоны', async function () {
        await openPageAndWaitRendered(this);

        await clickObjectOnMap(this, MapEntity.WMS_ZONES, '9');

        await toggleSectionAudience(this);

        const itemValue = await this.browser.assertBySelector(MapMenuAnalyticTestId.ITEM_VALUE_TARGET_AUDIENCE);

        expect(await itemValue.getText()).to.include(replaceNbsp(numberFormatter.format(1914)));
    });

    it('Расчет общей аудитории зоны', async function () {
        await openPageAndWaitRendered(this);

        await clickObjectOnMap(this, MapEntity.WMS_ZONES, '9');

        await toggleSectionAudience(this);

        const itemValue = await this.browser.assertBySelector(MapMenuAnalyticTestId.ITEM_VALUE_TOTAL_AUDIENCE);

        expect(await itemValue.getText()).to.include(replaceNbsp(numberFormatter.format(19321)));
    });

    it('Расчет цены за метр зоны', async function () {
        await openPageAndWaitRendered(this);

        await clickObjectOnMap(this, MapEntity.WMS_ZONES, '9');

        await toggleSectionAudience(this);

        const itemValue = await this.browser.assertBySelector(MapMenuAnalyticTestId.ITEM_VALUE_COST_ON_METER);

        expect(await itemValue.getText()).to.include(replaceNbsp(currencyFormatter.format(147749.75)));
    });

    it('Расчет количества заказов Такси и среднего чека Такси зоны', async function () {
        await openPageAndWaitRendered(this);

        await clickObjectOnMap(this, MapEntity.WMS_ZONES, '9');

        await toggleSectionTaxi(this);

        const ordersItemValue = await this.browser.assertBySelector(MapMenuAnalyticTestId.ITEM_VALUE_TAXI_ORDERS);
        const averageItemValue = await this.browser.assertBySelector(
            MapMenuAnalyticTestId.ITEM_VALUE_TAXI_AVERAGE_RECEIPT
        );

        expect(await ordersItemValue.getText()).to.include(replaceNbsp(numberFormatter.format(605)));
        expect(await averageItemValue.getText()).to.include(replaceNbsp(currencyFormatter.format(356)));
    });

    it('Расчет количества заказов Лавки и среднего чека Лавки зоны', async function () {
        await openPageAndWaitRendered(this);

        await clickObjectOnMap(this, MapEntity.WMS_ZONES, '9');

        await toggleSectionLavka(this);

        const ordersItemValue = await this.browser.assertBySelector(MapMenuAnalyticTestId.ITEM_VALUE_DELI_ORDERS);
        const averageItemValue = await this.browser.assertBySelector(
            MapMenuAnalyticTestId.ITEM_VALUE_DELI_AVERAGE_RECEIPT
        );

        expect(await ordersItemValue.getText()).to.include(replaceNbsp(numberFormatter.format(10)));
        expect(await averageItemValue.getText()).to.include(replaceNbsp(currencyFormatter.format(1131)));
    });

    it('Click to eat зоны', async function () {
        await openPageAndWaitRendered(this, {
            z: '14',
            ll: '37.50987099965221,55.94074826940243'
        });

        await clickObjectOnMap(this, MapEntity.WMS_ZONES, '7');

        await toggleSectionLavka(this);

        const cteItemValue = await this.browser.assertBySelector(MapMenuAnalyticTestId.ITEM_VALUE_LAVKA_AVERAGE_CTE);

        expect(await cteItemValue.getText()).to.include(replaceNbsp(numberFormatter.format(10)));
    });

    it('Расчет количества заказов Еды и среднего чека Еды зоны', async function () {
        await openPageAndWaitRendered(this);

        await clickObjectOnMap(this, MapEntity.WMS_ZONES, '9');

        await toggleSectionEda(this);

        const ordersItemValue = await this.browser.assertBySelector(MapMenuAnalyticTestId.ITEM_VALUE_MEAL_ORDERS);
        const averageItemValue = await this.browser.assertBySelector(
            MapMenuAnalyticTestId.ITEM_VALUE_MEAL_AVERAGE_RECEIPT
        );

        expect(await ordersItemValue.getText()).to.include(replaceNbsp(numberFormatter.format(15)));
        expect(await averageItemValue.getText()).to.include(replaceNbsp(currencyFormatter.format(1361)));
    });

    it('Описания аналитических метрик для меню зоны', async function () {
        await openPageAndWaitRendered(this);

        await clickObjectOnMap(this, MapEntity.WMS_ZONES, '9');

        await toggleSectionAudience(this);
        await assertEntityDescription(this, AnalystEntity.SOCDEM_C1C2RES);
        await assertEntityDescription(this, AnalystEntity.SOCDEM_P4P5RES);
        await assertEntityDescription(this, AnalystEntity.SOCDEM_TTL_RESIDENTS_REAL);
        await assertEntityDescription(this, AnalystEntity.SOCDEM_COST_ON_METER);
        await toggleSectionAudience(this);

        await toggleSectionTaxi(this);
        await assertEntityDescription(this, AnalystEntity.TAXI_ORDERS_COUNT);
        await assertEntityDescription(this, AnalystEntity.TAXI_ORDERS_AVG_PRICE);
        await toggleSectionTaxi(this);

        await toggleSectionEda(this);
        await assertEntityDescription(this, AnalystEntity.EDA_ORDERS_COUNT);
        await assertEntityDescription(this, AnalystEntity.EDA_ORDERS_AVG_PRICE);
        await toggleSectionEda(this);

        await toggleSectionLavka(this);
        await assertEntityDescription(this, AnalystEntity.LAVKA_ORDERS_COUNT);
        await assertEntityDescription(this, AnalystEntity.LAVKA_ORDERS_AVG_PRICE);
        await assertEntityDescription(this, AnalystEntity.LAVKA_ORDERS_AVG_CTE);
        await assertEntityDescription(this, AnalystEntity.LAVKA_ORDERS_GMV);
    });
});
