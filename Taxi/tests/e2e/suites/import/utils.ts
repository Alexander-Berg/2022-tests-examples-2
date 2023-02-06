import {isEqual} from 'lodash';

export async function getConfirmedAttributes(browser: WebdriverIO.Browser, productIdentifier: number) {
    const langs = await browser.executeSql(
        `SELECT lang_id
        FROM locale
        JOIN product ON product.region_id = locale.region_id
        WHERE product.identifier = ${productIdentifier}`
    );

    const attributes = await browser.executeSql(
        `SELECT attribute_id,
            CASE WHEN AVG(lang_id) IS NOT NULL THEN
                CASE WHEN COUNT(is_confirmed) = ${(langs as []).length}
                    THEN true
                    ELSE false
                END
                ELSE true
            END as is_confirmed
        FROM product_attribute_value pav
        JOIN product ON product.id = pav.product_id
        WHERE TRUE
            AND product.identifier = ${productIdentifier}
            AND pav.is_confirmed = TRUE
        GROUP BY attribute_id
        ORDER BY attribute_id
        `
    );

    return (attributes as Array<{attribute_id: number; is_confirmed: boolean}>)
        .filter((attribute) => attribute.is_confirmed)
        .map((el) => el.attribute_id);
}

export async function areAttributesConfirmed(
    browser: WebdriverIO.Browser,
    productIdentifier: number,
    attributesIds: number[]
) {
    const confirmedAttributes = await getConfirmedAttributes(browser, productIdentifier);

    return isEqual(
        confirmedAttributes,
        attributesIds.sort((a, b) => a - b)
    );
}
