import {expect} from '@playwright/test';

import test from '../../playwright/fixtures.js';

test.describe.serial('example 2', () => {
    test('main', async ({p}) => {
        await p.goto('/');
        await expect(p).toHaveURL('https://dev.go.tst.yandex.net/');
    });

    test('vacancies', async ({p}) => {
        await p.goto('/vacancies');
        await expect(p).toHaveURL('https://dev.go.tst.yandex.net/vacancies');
    });

    test('office', async ({p}) => {
        await p.goto('/office');
        await expect(p).toHaveURL('https://dev.go.tst.yandex.net/office');
    });
});
