import * as fs from 'fs';
import * as path from 'path';

import { updateDump } from '../../../../../lib/dump';
import { ordersReducer } from '../orders';

const needUpdateDump = process.env.UPDATE_DUMP === '1';

describe('Orders reducer', () => {
    describe('list dumps', () => {
        const filesDirectory = path.resolve(__dirname, './data/list');
        const files = fs.readdirSync(filesDirectory);

        files.forEach((name) => {
            it(`dump ${name}`, () => {
                // eslint-disable-next-line @typescript-eslint/no-var-requires
                const { context, test, expectation } = require(path.resolve(
                    __dirname,
                    './data/list',
                    name,
                ));

                const result = ordersReducer(test, {
                    services: context.services,
                    payServicesEnabled: context.payServicesEnabled,
                    payServices: context.payServices,
                    discounts: new Set(context.discounts),
                    servicesOrder: context.servicesOrder,
                    plusServiceData: context.plusServiceData,
                    yandexPayEnabled: false,
                    newHelpdesk: false,
                    newSecurity: false,
                    withChecks: () => false,
                    withDetails: () => false,
                    getServiceById: () => undefined,
                });

                needUpdateDump &&
                    updateDump(path.resolve(filesDirectory, name), test, context, () => result);

                expect(result).toEqual(expectation);
            });
        });
    });

    describe('listPlus dumps', () => {
        const filesDirectory = path.resolve(__dirname, './data/plus');
        const files = fs.readdirSync(filesDirectory);

        files.forEach((name) => {
            it(`dumps ${name}`, () => {
                // eslint-disable-next-line @typescript-eslint/no-var-requires
                const { context, test, expectation } = require(path.resolve(
                    __dirname,
                    './data/plus',
                    name,
                ));

                const result = ordersReducer(
                    test,
                    {
                        services: context.services,
                        payServicesEnabled: context.payServicesEnabled,
                        payServices: context.payServices,
                        discounts: new Set(context.discounts),
                        servicesOrder: context.servicesOrder,
                        plusServiceData: context.plusServiceData,
                        yandexPayEnabled: false,
                        newHelpdesk: false,
                        newSecurity: false,
                        withChecks: () => false,
                        withDetails: () => false,
                        getServiceById: () => undefined,
                    },
                    { notIgnoreTrust: true },
                );

                needUpdateDump &&
                    updateDump(path.resolve(filesDirectory, name), test, context, () => result);

                expect(result).toEqual(expectation);
            });
        });
    });
});
