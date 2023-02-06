import {ROUTES} from '@/src/constants/routes';
import type {RegionCode} from 'types/region';

const masterCategoryPath = {
    RU: [1, 5, 25],
    FR: [3, 15, 45],
    IL: [4, 20, 55],
    GB: [2, 10, 35]
};

export async function chooseMasterCategory(
    browser: WebdriverIO.Browser,
    region: keyof typeof masterCategoryPath = 'RU'
) {
    for (const id of masterCategoryPath[region]) {
        await browser.clickInto(['parent-category-modal__tree-list', `row_master_category_code_${id}_0`], {
            waitRender: true,
            waitForClickable: true
        });
    }
}

type CreateUnusedAttributeOptions = {
    region?: Lowercase<RegionCode> | null;
    infoModelCode?: string;
    attributeCode?: string;
};

export async function createUnusedAttribute(browser: WebdriverIO.Browser, options?: CreateUnusedAttributeOptions) {
    const {region, infoModelCode = 'info_model_code_1_1', attributeCode = 'image_attribute_code_1_0'} = options ?? {};

    await browser.openPage(ROUTES.CLIENT.INFOMODELS, {region});
    await browser.clickInto(`im_row_${infoModelCode}`, {waitRender: true, waitNavigation: true});
    await browser.clickInto('\\#rc-tabs-0-tab-custom-attributes-tab', {waitRender: true});
    if (attributeCode === 'text_attribute_code_6_2_loc') {
        await browser.clickInto(['infomodel-groups-table', 'im_attribute-group_row_undefined']);
    }
    await browser.clickInto([`im_attribute_row_${attributeCode}`, 'delete']);
    await browser.clickInto(['header-panel', 'submit-button'], {waitRender: true});
}
