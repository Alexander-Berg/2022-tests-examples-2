import { test } from "@playwright/test";

import { localStorageData } from "../data";
import { addToLocalStorage, authorize } from "../lib";

test('Auth', async ({ browser }) => {
    const context = await browser.newContext({ ignoreHTTPSErrors: true });
    const page = await context.newPage();
    await authorize(page, "yndx-robot-metrika-test");
    await page.goto("/");
    await addToLocalStorage(page, localStorageData);
    await context.storageState({ path: 'state.json' });
});
