import {DbTable} from '@/src/entities/const';

export default function makeAttributeConfirmable(browser: WebdriverIO.Browser, attributeId: number) {
    return browser.executeSql(`UPDATE ${DbTable.ATTRIBUTE} set is_confirmable = true WHERE id = ${attributeId}`);
}
