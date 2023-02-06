import {DbTable} from '@/src/entities/const';

interface Props {
    browser: WebdriverIO.Browser;
    productIdentifier: number;
    attributeId: number;
    langId?: number;
    value?: boolean;
}

export default function setAttributeConfirmationValue({
    browser,
    productIdentifier,
    attributeId,
    langId,
    value = true
}: Props) {
    return browser.executeSql(
        `UPDATE ${DbTable.PRODUCT_ATTRIBUTE_VALUE} set is_confirmed = ${value}
            WHERE TRUE
                AND attribute_id = ${attributeId}
                AND product_id = (select id from ${DbTable.PRODUCT} where identifier = ${productIdentifier})
                AND ${langId ? `lang_id = ${langId}` : 'TRUE'}`
    );
}
