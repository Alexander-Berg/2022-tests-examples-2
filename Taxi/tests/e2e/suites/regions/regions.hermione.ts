import type {OpenPageOptions} from 'tests/e2e/config/commands/open-page';
import {assertMapWithoutControls, hideHexagons} from 'tests/e2e/utils/common';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';
import {
    BaseLayoutTestId,
    CitySelectTestId,
    formatCitySelectOptionTestId,
    formatRegionSelectOptionTestId,
    RegionSelectTestId
} from 'types/test-id';

describe('Регионы и переход по прямой ссылке', function () {
    it('Открыть по прямой ссылке Израиль', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT, {region: 'il'});
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(RegionSelectTestId.ROOT);
        await assertMapWithoutControls(this);
    });

    it('Изменить город в России', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT);
        await hideHexagons(this);

        await this.browser.assertImage(CitySelectTestId.ROOT);
        await this.browser.clickInto(CitySelectTestId.ROOT, {waitForClickable: true, waitRender: true});
        await this.browser.clickInto(formatCitySelectOptionTestId(2), {waitForClickable: true, waitRender: true});

        const {pathname} = new URL(await this.browser.getUrl());
        expect(pathname.toLowerCase()).to.equal('/ru');

        await this.browser.assertImage(CitySelectTestId.ROOT);
        await assertMapWithoutControls(this);
    });

    it('Изменить регион на Белоруссию', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT);
        await this.browser.assertImage(RegionSelectTestId.ROOT);
        await this.browser.clickInto(RegionSelectTestId.ROOT, {waitForClickable: true, waitRender: true});
        await this.browser.clickInto(formatRegionSelectOptionTestId('BY'), {waitForClickable: true, waitRender: true});

        const {pathname} = new URL(await this.browser.getUrl());
        expect(pathname.toLowerCase()).to.equal('/by');

        await this.browser.assertImage(RegionSelectTestId.ROOT);
        await assertMapWithoutControls(this);
    });

    it('Ошибка 404 при переходе в некорректный регион', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT, {region: 'wrong' as OpenPageOptions['region']});
        await this.browser.waitUntilRendered();
        await this.browser.assertImage(BaseLayoutTestId.CONTENT);
    });
});
