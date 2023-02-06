import {Companies} from '@/src/entities/companies/entity';
import {Stores} from '@/src/entities/stores/entity';
import {Tasks} from '@/src/entities/tasks/entity';
import {ensureConnection} from 'service/db';
import * as erp from 'service/helper/get-tasks-from-erp';
import type {WoodyErpResponse} from 'types/erp';

import {updateErpData} from './index';

const getTasksFromErp = jest.spyOn(erp, 'getTasksFromErp');

describe('Schedulers', () => {
    beforeEach(async () => {
        const conn = await ensureConnection();

        await conn.getRepository(Companies).insert({
            externalId: 'company_external_id_1',
            title: 'Лавка Израиль',
            endpoint: 'http://lavka.il/',
            envTokenVariable: 'company_external_id_1_env',
            cursor: '0'
        });

        process.env['company_external_id_1_env'] = 'token';
    });
    it('should not mutate tasks after checking updates with same cursor', async () => {
        const conn = await ensureConnection();

        const erpResponse: WoodyErpResponse = {
            orders: [
                {
                    id: '11',
                    number: 'PO000000000000002',
                    supply_date: '2021-06-22',
                    warehouse: {
                        id: 'company_external_id_1',
                        wms_id: '33e45753daa84a298edc4f1789f9ba24000200010000',
                        name: 'Яндекс Лавка Тель Авив'
                    },
                    supplier: {
                        id: 376000011,
                        inn: '23143242',
                        kpp: '23143242',
                        name: 'TEST PURCHASER',
                        edo: false
                    },
                    items: [
                        {
                            id: '11',
                            wms_id: 'cadb876979ee46f2953b1a49e9d4068d000300020002',
                            supplier_id: '634073',
                            name: 'Greek salad',
                            quantity: 4.0,
                            price: 5.0,
                            vat: 17.0,
                            sum: 20.0,
                            vat_sum: 3.4,
                            total_sum: 23.4
                        }
                    ],
                    wms_orders: []
                },
                {
                    id: '22',
                    number: 'PO000000000000002',
                    supply_date: '2021-06-22',
                    warehouse: {
                        id: 'company_external_id_1',
                        wms_id: '33e45753daa84a298edc4f1789f9ba24000200010000',
                        name: 'Яндекс Лавка Тель Авив'
                    },
                    supplier: {
                        id: 376000011,
                        inn: '23143242',
                        kpp: '23143242',
                        name: 'TEST PURCHASER',
                        edo: false
                    },
                    items: [
                        {
                            id: '22',
                            wms_id: 'cadb876979ee46f2953b1a49e9d4068d000300020002',
                            supplier_id: '634073',
                            name: 'Greek salad',
                            quantity: 4.0,
                            price: 5.0,
                            vat: 17.0,
                            sum: 20.0,
                            vat_sum: 3.4,
                            total_sum: 23.4
                        }
                    ],
                    wms_orders: []
                }
            ],
            cursor: '1'
        };

        getTasksFromErp.mockResolvedValue(erpResponse);

        await updateErpData();

        const stores1 = await conn.getRepository(Stores).find();
        expect(stores1).toHaveLength(1);

        const tasks1 = await conn.getRepository(Tasks).find();
        expect(tasks1).toHaveLength(2);

        await updateErpData();

        const stores2 = await conn.getRepository(Stores).find();
        expect(stores2).toHaveLength(1);

        const tasks2 = await conn.getRepository(Tasks).find();
        expect(tasks2).toHaveLength(2);
    });

    it('should update one of tasks', async () => {
        const tasksIds = ['task_external_id_1', 'task_external_id_2'];
        const itemsIds = ['item_id_1', 'item_id_2'];
        const firstErpResponse: WoodyErpResponse = {
            orders: [
                {
                    id: tasksIds[0],
                    number: 'PO000000000000002',
                    supply_date: '2021-06-22',
                    warehouse: {
                        id: 'store_external_id_1',
                        wms_id: '33e45753daa84a298edc4f1789f9ba24000200010000',
                        name: 'Яндекс Лавка Тель Авив'
                    },
                    supplier: {
                        id: 376000011,
                        inn: '23143242',
                        kpp: '23143242',
                        name: 'TEST PURCHASER',
                        edo: false
                    },
                    items: [
                        {
                            id: itemsIds[0],
                            wms_id: 'cadb876979ee46f2953b1a49e9d4068d000300020002',
                            supplier_id: '634073',
                            name: 'Greek salad',
                            quantity: 4.0,
                            price: 5.0,
                            vat: 17.0,
                            sum: 20.0,
                            vat_sum: 3.4,
                            total_sum: 23.4
                        }
                    ],
                    wms_orders: []
                },
                {
                    id: tasksIds[1],
                    number: 'PO000000000000002',
                    supply_date: '2021-06-22',
                    warehouse: {
                        id: 'store_external_id_1',
                        wms_id: '33e45753daa84a298edc4f1789f9ba24000200010000',
                        name: 'Яндекс Лавка Тель Авив'
                    },
                    supplier: {
                        id: 376000011,
                        inn: '23143242',
                        kpp: '23143242',
                        name: 'TEST PURCHASER',
                        edo: false
                    },
                    items: [
                        {
                            id: itemsIds[0], // это не ошибка
                            wms_id: 'cadb876979ee46f2953b1a49e9d4068d000300020002',
                            supplier_id: '634073',
                            name: 'Greek salad',
                            quantity: 4.0,
                            price: 5.0,
                            vat: 17.0,
                            sum: 20.0,
                            vat_sum: 3.4,
                            total_sum: 23.4
                        }
                    ],
                    wms_orders: []
                }
            ],
            cursor: '1'
        };

        getTasksFromErp.mockReturnValue(
            new Promise((resolve) => {
                resolve(firstErpResponse);
            })
        );

        const conn = await ensureConnection();

        await updateErpData();

        const tasks1 = await conn.getRepository(Tasks).find();

        const expected1 = tasks1.filter((t) => tasksIds.includes(t.externalId));

        expect(expected1[1].data.items[0].id).toBe(itemsIds[0]);

        const secondErpResponse: WoodyErpResponse = {
            orders: [
                {
                    id: tasksIds[0],
                    number: 'PO000000000000002',
                    supply_date: '2021-06-22',
                    warehouse: {
                        id: 'store_external_id_1',
                        wms_id: '33e45753daa84a298edc4f1789f9ba24000200010000',
                        name: 'Яндекс Лавка Тель Авив'
                    },
                    supplier: {
                        id: 376000011,
                        inn: '23143242',
                        kpp: '23143242',
                        name: 'TEST PURCHASER',
                        edo: false
                    },
                    items: [
                        {
                            id: itemsIds[0],
                            wms_id: 'cadb876979ee46f2953b1a49e9d4068d000300020002',
                            supplier_id: '634073',
                            name: 'Greek salad',
                            quantity: 4.0,
                            price: 5.0,
                            vat: 17.0,
                            sum: 20.0,
                            vat_sum: 3.4,
                            total_sum: 23.4
                        }
                    ],
                    wms_orders: []
                },
                {
                    id: tasksIds[1],
                    number: 'PO000000000000002',
                    supply_date: '2021-06-22',
                    warehouse: {
                        id: 'store_external_id_1',
                        wms_id: '33e45753daa84a298edc4f1789f9ba24000200010000',
                        name: 'Яндекс Лавка Тель Авив'
                    },
                    supplier: {
                        id: 376000011,
                        inn: '23143242',
                        kpp: '23143242',
                        name: 'TEST PURCHASER',
                        edo: false
                    },
                    items: [
                        {
                            id: itemsIds[1],
                            wms_id: 'cadb876979ee46f2953b1a49e9d4068d000300020002',
                            supplier_id: '634073',
                            name: 'Greek salad',
                            quantity: 4.0,
                            price: 5.0,
                            vat: 17.0,
                            sum: 20.0,
                            vat_sum: 3.4,
                            total_sum: 23.4
                        }
                    ],
                    wms_orders: []
                }
            ],
            cursor: '2'
        };

        getTasksFromErp.mockReturnValue(
            new Promise((resolve) => {
                resolve(secondErpResponse);
            })
        );

        await updateErpData();

        const tasks2 = await conn.getRepository(Tasks).find();
        const expected2 = tasks2.filter((t) => tasksIds.includes(t.externalId));

        expect(expected2[1].data.items[0].id).toBe(itemsIds[1]);
    });

    it('should update stores', async () => {
        const storesIds = ['store_id_1', 'store_id_2'];
        const storesNames1 = ['Название склада 1', 'Название склада 2'];

        const firstErpResponse: WoodyErpResponse = {
            orders: [
                {
                    id: 'task_external_id_1',
                    number: 'PO000000000000002',
                    supply_date: '2021-06-22',
                    warehouse: {
                        id: storesIds[0],
                        wms_id: '33e45753daa84a298edc4f1789f9ba24000200010000',
                        name: storesNames1[0]
                    },
                    supplier: {
                        id: 376000011,
                        inn: '23143242',
                        kpp: '23143242',
                        name: 'TEST PURCHASER',
                        edo: false
                    },
                    items: [
                        {
                            id: '11',
                            wms_id: 'cadb876979ee46f2953b1a49e9d4068d000300020002',
                            supplier_id: '634073',
                            name: 'Greek salad',
                            quantity: 4.0,
                            price: 5.0,
                            vat: 17.0,
                            sum: 20.0,
                            vat_sum: 3.4,
                            total_sum: 23.4
                        }
                    ],
                    wms_orders: []
                },
                {
                    id: 'task_external_id_2',
                    number: 'PO000000000000002',
                    supply_date: '2021-06-22',
                    warehouse: {
                        id: storesIds[1],
                        wms_id: '33e45753daa84a298edc4f1789f9ba24000200010000',
                        name: storesNames1[1]
                    },
                    supplier: {
                        id: 376000011,
                        inn: '23143242',
                        kpp: '23143242',
                        name: 'TEST PURCHASER',
                        edo: false
                    },
                    items: [
                        {
                            id: '22',
                            wms_id: 'cadb876979ee46f2953b1a49e9d4068d000300020002',
                            supplier_id: '634073',
                            name: 'Greek salad',
                            quantity: 4.0,
                            price: 5.0,
                            vat: 17.0,
                            sum: 20.0,
                            vat_sum: 3.4,
                            total_sum: 23.4
                        }
                    ],
                    wms_orders: []
                }
            ],
            cursor: '1'
        };

        getTasksFromErp.mockReturnValue(
            new Promise((resolve) => {
                resolve(firstErpResponse);
            })
        );

        const conn = await ensureConnection();

        await updateErpData();

        const stores1 = await conn.getRepository(Stores).find();

        const expected1 = stores1.filter((store) => storesIds.includes(store.externalId));

        expect(expected1[0].externalId).toBe(storesIds[0]);
        expect(expected1[1].externalId).toBe(storesIds[1]);

        expect(expected1[0].name).toBe(storesNames1[0]);
        expect(expected1[1].name).toBe(storesNames1[1]);

        const storesNames2 = ['Название склада 111', 'Название склада 222'];

        const secondErpResponse: WoodyErpResponse = {
            orders: [
                {
                    id: 'task_external_id_1',
                    number: 'PO000000000000002',
                    supply_date: '2021-06-22',
                    warehouse: {
                        id: storesIds[0],
                        wms_id: '33e45753daa84a298edc4f1789f9ba24000200010000',
                        name: storesNames2[0]
                    },
                    supplier: {
                        id: 376000011,
                        inn: '23143242',
                        kpp: '23143242',
                        name: 'TEST PURCHASER',
                        edo: false
                    },
                    items: [
                        {
                            id: '11',
                            wms_id: 'cadb876979ee46f2953b1a49e9d4068d000300020002',
                            supplier_id: '634073',
                            name: 'Greek salad',
                            quantity: 4.0,
                            price: 5.0,
                            vat: 17.0,
                            sum: 20.0,
                            vat_sum: 3.4,
                            total_sum: 23.4
                        }
                    ],
                    wms_orders: []
                },
                {
                    id: 'task_external_id_2',
                    number: 'PO000000000000002',
                    supply_date: '2021-06-22',
                    warehouse: {
                        id: storesIds[1],
                        wms_id: '33e45753daa84a298edc4f1789f9ba24000200010000',
                        name: storesNames2[1]
                    },
                    supplier: {
                        id: 376000011,
                        inn: '23143242',
                        kpp: '23143242',
                        name: 'TEST PURCHASER',
                        edo: false
                    },
                    items: [
                        {
                            id: '22',
                            wms_id: 'cadb876979ee46f2953b1a49e9d4068d000300020002',
                            supplier_id: '634073',
                            name: 'Greek salad',
                            quantity: 4.0,
                            price: 5.0,
                            vat: 17.0,
                            sum: 20.0,
                            vat_sum: 3.4,
                            total_sum: 23.4
                        }
                    ],
                    wms_orders: []
                }
            ],
            cursor: '2'
        };

        getTasksFromErp.mockReturnValue(
            new Promise((resolve) => {
                resolve(secondErpResponse);
            })
        );

        await updateErpData();

        const stores2 = await conn.getRepository(Stores).find();

        const expected2 = stores2.filter((store) => storesIds.includes(store.externalId));

        expect(expected2[0].externalId).toBe(storesIds[0]);
        expect(expected2[1].externalId).toBe(storesIds[1]);

        expect(expected2[0].name).toBe(storesNames2[0]);
        expect(expected2[1].name).toBe(storesNames2[1]);
    });

    it('should ignore response with the same cursor value', async () => {
        const tasksIds = ['task_external_id_1', 'task_external_id_2'];
        const itemsIds = ['item_id_1', 'item_id_2'];
        const firstErpResponse: WoodyErpResponse = {
            orders: [
                {
                    id: tasksIds[0],
                    number: 'PO000000000000002',
                    supply_date: '2021-06-22',
                    warehouse: {
                        id: 'store_external_id_1',
                        wms_id: '33e45753daa84a298edc4f1789f9ba24000200010000',
                        name: 'Яндекс Лавка Тель Авив'
                    },
                    supplier: {
                        id: 376000011,
                        inn: '23143242',
                        kpp: '23143242',
                        name: 'TEST PURCHASER',
                        edo: false
                    },
                    items: [
                        {
                            id: itemsIds[0],
                            wms_id: 'cadb876979ee46f2953b1a49e9d4068d000300020002',
                            supplier_id: '634073',
                            name: 'Greek salad',
                            quantity: 4.0,
                            price: 5.0,
                            vat: 17.0,
                            sum: 20.0,
                            vat_sum: 3.4,
                            total_sum: 23.4
                        }
                    ],
                    wms_orders: []
                },
                {
                    id: tasksIds[1],
                    number: 'PO000000000000002',
                    supply_date: '2021-06-22',
                    warehouse: {
                        id: 'store_external_id_1',
                        wms_id: '33e45753daa84a298edc4f1789f9ba24000200010000',
                        name: 'Яндекс Лавка Тель Авив'
                    },
                    supplier: {
                        id: 376000011,
                        inn: '23143242',
                        kpp: '23143242',
                        name: 'TEST PURCHASER',
                        edo: false
                    },
                    items: [
                        {
                            id: itemsIds[0], // это не ошибка
                            wms_id: 'cadb876979ee46f2953b1a49e9d4068d000300020002',
                            supplier_id: '634073',
                            name: 'Greek salad',
                            quantity: 4.0,
                            price: 5.0,
                            vat: 17.0,
                            sum: 20.0,
                            vat_sum: 3.4,
                            total_sum: 23.4
                        }
                    ],
                    wms_orders: []
                }
            ],
            cursor: '1'
        };

        getTasksFromErp.mockReturnValue(
            new Promise((resolve) => {
                resolve(firstErpResponse);
            })
        );

        const conn = await ensureConnection();

        await updateErpData();

        const tasks1 = await conn.getRepository(Tasks).find();

        const expected1 = tasks1.filter((t) => tasksIds.includes(t.externalId));

        expect(expected1[1].data.items[0].id).toBe(itemsIds[0]);

        const secondErpResponse: WoodyErpResponse = {
            orders: [
                {
                    id: tasksIds[0],
                    number: 'PO000000000000002',
                    supply_date: '2021-06-22',
                    warehouse: {
                        id: 'store_external_id_1',
                        wms_id: '33e45753daa84a298edc4f1789f9ba24000200010000',
                        name: 'Яндекс Лавка Тель Авив'
                    },
                    supplier: {
                        id: 376000011,
                        inn: '23143242',
                        kpp: '23143242',
                        name: 'TEST PURCHASER',
                        edo: false
                    },
                    items: [
                        {
                            id: itemsIds[0],
                            wms_id: 'cadb876979ee46f2953b1a49e9d4068d000300020002',
                            supplier_id: '634073',
                            name: 'Greek salad',
                            quantity: 4.0,
                            price: 5.0,
                            vat: 17.0,
                            sum: 20.0,
                            vat_sum: 3.4,
                            total_sum: 23.4
                        }
                    ],
                    wms_orders: []
                },
                {
                    id: tasksIds[1],
                    number: 'PO000000000000002',
                    supply_date: '2021-06-22',
                    warehouse: {
                        id: 'store_external_id_1',
                        wms_id: '33e45753daa84a298edc4f1789f9ba24000200010000',
                        name: 'Яндекс Лавка Тель Авив'
                    },
                    supplier: {
                        id: 376000011,
                        inn: '23143242',
                        kpp: '23143242',
                        name: 'TEST PURCHASER',
                        edo: false
                    },
                    items: [
                        {
                            id: itemsIds[1],
                            wms_id: 'cadb876979ee46f2953b1a49e9d4068d000300020002',
                            supplier_id: '634073',
                            name: 'Greek salad',
                            quantity: 4.0,
                            price: 5.0,
                            vat: 17.0,
                            sum: 20.0,
                            vat_sum: 3.4,
                            total_sum: 23.4
                        }
                    ],
                    wms_orders: []
                }
            ],
            cursor: '1' // тот же курсор, это не ошибка
        };

        getTasksFromErp.mockReturnValue(
            new Promise((resolve) => {
                resolve(secondErpResponse);
            })
        );

        await updateErpData();

        const tasks2 = await conn.getRepository(Tasks).find();
        const expected2 = tasks2.filter((t) => tasksIds.includes(t.externalId));

        expect(expected2[1].data.items[0].id).toBe(itemsIds[0]);
    });
});
