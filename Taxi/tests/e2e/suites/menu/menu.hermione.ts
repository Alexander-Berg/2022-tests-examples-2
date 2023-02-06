import {assertMapAndSidebarWithoutControls} from 'tests/e2e/utils/common';
import {describe, expect, it} from 'tests/hermione.globals';

import {ROUTES} from '@/src/constants/routes';
import {LogoTestId, MenuToggleIconTestId, SidebarTestId} from 'types/test-id';

describe('Меню', function () {
    it('Клик в лого возвращает на страницу товаров', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT);
        await this.browser.clickInto(LogoTestId.ROOT);
        expect(await this.browser.getUrl()).to.match(new RegExp(ROUTES.CLIENT.ROOT));
    });

    it('Свернуть и развернуть боковое меню', async function () {
        await this.browser.openPage(ROUTES.CLIENT.ROOT);

        await this.browser.clickInto(MenuToggleIconTestId.ROOT, {
            waitForClickable: true,
            waitRender: true
        });
        await assertMapAndSidebarWithoutControls(this);

        await this.browser.clickInto(MenuToggleIconTestId.ROOT, {
            waitForClickable: true,
            waitRender: true
        });
        await this.browser.assertImage(SidebarTestId.ROOT);
    });
});
