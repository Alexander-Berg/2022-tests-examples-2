import {Stores} from '@/src/entities/stores/entity';
import {Tasks} from '@/src/entities/tasks/entity';
import {ensureConnection} from 'service/db';
import * as erp from 'service/helper/get-tasks-from-1c-erp';
import {startOfDay} from 'service/utils/date-helper';
import type {ErpSupply} from 'types/erp';

import {updateErpData} from './index';

const getTasksFrom1cErp = jest.spyOn(erp, 'getTasksFrom1cErp');
const getDateRangesForErpUpdate = jest.spyOn(erp, 'getDateRangesForErpUpdate');

describe('Schedulers', () => {
    const date = startOfDay(new Date());
    it('should remove task that absent in second erp response', async () => {
        const erpIds = ['11', '22'];
        const firstErpResponse: ErpSupply[] = [
            {
                id: erpIds[0],
                number: '1',
                warehouse: {
                    id: '42',
                    wms_id: '1',
                    name: 'ул. Тестовская, д. 0'
                },
                supplier: {
                    inn: '',
                    name: '',
                    id: '',
                    kpp: ''
                },
                items: [
                    {
                        id: '1',
                        wms_id: '',
                        supplier_id: 1,
                        name: 'сырок Б. Ю. Александров',
                        quantity: 0,
                        price: 47.99,
                        sum: 0,
                        vat: 10,
                        vat_sum: 4.799,
                        total_sum: 0
                    }
                ],
                wms_orders: []
            },
            {
                id: erpIds[1],
                number: '1',
                warehouse: {
                    id: '42',
                    wms_id: '',
                    name: 'ул. Тестовская, д. 0'
                },
                supplier: {
                    inn: '',
                    name: '',
                    id: '',
                    kpp: ''
                },
                items: [
                    {
                        id: '1',
                        wms_id: '',
                        supplier_id: 1,
                        name: 'сырок Б. Ю. Александров',
                        quantity: 0,
                        price: 47.99,
                        sum: 0,
                        vat: 10,
                        vat_sum: 4.799,
                        total_sum: 0
                    }
                ],
                wms_orders: []
            }
        ];

        getTasksFrom1cErp.mockReturnValue(
            new Promise((resolve) => {
                resolve(firstErpResponse);
            })
        );

        getDateRangesForErpUpdate.mockReturnValue([date]);

        const conn = await ensureConnection();

        await conn.getRepository(Stores).insert({externalId: '42', name: 'ул. Тестовская, д. 0'});

        await updateErpData();

        const tasks = await conn.getRepository(Tasks).find();
        const expected1 = tasks.filter((t) => erpIds.includes(t.externalId));

        expect(expected1).toHaveLength(2);

        const secondErpResponse: ErpSupply[] = [
            {
                id: erpIds[0],
                number: '1',
                warehouse: {
                    id: '42',
                    wms_id: '',
                    name: 'ул. Тестовская, д. 0'
                },
                supplier: {
                    inn: '',
                    name: '',
                    id: '',
                    kpp: ''
                },
                items: [
                    {
                        id: '1',
                        wms_id: '',
                        supplier_id: 1,
                        name: 'сырок Б. Ю. Александров',
                        quantity: 0,
                        price: 47.99,
                        sum: 0,
                        vat: 10,
                        vat_sum: 4.799,
                        total_sum: 0
                    }
                ],
                wms_orders: []
            }
        ];

        getTasksFrom1cErp.mockReturnValue(
            new Promise((resolve) => {
                resolve(secondErpResponse);
            })
        );

        await updateErpData();

        const tasks2 = await conn.getRepository(Tasks).find();
        const expected2 = tasks2.filter((t) => erpIds.includes(t.externalId));

        expect(expected2).toHaveLength(1);
    });

    it("should don't mutate tasks after checking updates", async () => {
        const conn = await ensureConnection();

        await conn.getRepository(Stores).insert({externalId: '42', name: 'ул. Тестовская, д. 0'});

        const erpResponse: ErpSupply[] = [
            {
                id: '11',
                number: '1',
                warehouse: {
                    id: '42',
                    wms_id: '1',
                    name: 'ул. Тестовская, д. 0'
                },
                supplier: {
                    inn: '',
                    name: '',
                    id: '',
                    kpp: ''
                },
                items: [
                    {
                        id: '1',
                        wms_id: '',
                        supplier_id: 1,
                        name: 'сырок Б. Ю. Александров',
                        quantity: 0,
                        price: 47.99,
                        sum: 0,
                        vat: 10,
                        vat_sum: 4.799,
                        total_sum: 0
                    }
                ],
                wms_orders: []
            },
            {
                id: '22',
                number: '1',
                warehouse: {
                    id: '42',
                    wms_id: '',
                    name: 'ул. Тестовская, д. 0'
                },
                supplier: {
                    inn: '',
                    name: '',
                    id: '',
                    kpp: ''
                },
                items: [
                    {
                        id: '1',
                        wms_id: '',
                        supplier_id: 1,
                        name: 'сырок Б. Ю. Александров',
                        quantity: 0,
                        price: 47.99,
                        sum: 0,
                        vat: 10,
                        vat_sum: 4.799,
                        total_sum: 0
                    }
                ],
                wms_orders: []
            }
        ];

        getTasksFrom1cErp.mockReturnValue(
            new Promise((resolve) => {
                resolve(erpResponse);
            })
        );

        getDateRangesForErpUpdate.mockReturnValue([date]);

        await updateErpData();

        const tasks1 = await conn.getRepository(Tasks).find();
        expect(tasks1).toHaveLength(2);

        await updateErpData();

        const tasks2 = await conn.getRepository(Tasks).find();
        expect(tasks2).toHaveLength(2);
    });

    it('should update one of tasks', async () => {
        const erpIds = ['11', '22'];
        const firstErpResponse: ErpSupply[] = [
            {
                id: erpIds[0],
                number: '1',
                warehouse: {
                    id: '42',
                    wms_id: '1',
                    name: 'ул. Тестовская, д. 0'
                },
                supplier: {
                    inn: '',
                    name: '',
                    id: '',
                    kpp: ''
                },
                items: [
                    {
                        id: '1',
                        wms_id: '',
                        supplier_id: 1,
                        name: 'сырок Б. Ю. Александров',
                        quantity: 0,
                        price: 47.99,
                        sum: 0,
                        vat: 10,
                        vat_sum: 4.799,
                        total_sum: 0
                    }
                ],
                wms_orders: []
            },
            {
                id: erpIds[1],
                number: '1',
                warehouse: {
                    id: '42',
                    wms_id: '',
                    name: 'ул. Тестовская, д. 0'
                },
                supplier: {
                    inn: '',
                    name: '',
                    id: '',
                    kpp: ''
                },
                items: [
                    {
                        id: '1',
                        wms_id: '',
                        supplier_id: 1,
                        name: 'сырок Б. Ю. Александров',
                        quantity: 0,
                        price: 47.99,
                        sum: 0,
                        vat: 10,
                        vat_sum: 4.799,
                        total_sum: 0
                    }
                ],
                wms_orders: []
            }
        ];

        getTasksFrom1cErp.mockReturnValue(
            new Promise((resolve) => {
                resolve(firstErpResponse);
            })
        );

        getDateRangesForErpUpdate.mockReturnValue([date]);

        const conn = await ensureConnection();

        await conn.getRepository(Stores).insert({externalId: '42', name: 'ул. Тестовская, д. 0'});

        await updateErpData();

        const tasks = await conn.getRepository(Tasks).find();
        const expected1 = tasks.filter((t) => erpIds.includes(t.externalId));

        expect(expected1[1].data.items[0].id).toBe('1');

        const secondErpResponse: ErpSupply[] = [
            {
                id: erpIds[0],
                number: '1',
                warehouse: {
                    id: '42',
                    wms_id: '1',
                    name: 'ул. Тестовская, д. 0'
                },
                supplier: {
                    inn: '',
                    name: '',
                    id: '',
                    kpp: ''
                },
                items: [
                    {
                        id: '1',
                        wms_id: '',
                        supplier_id: 1,
                        name: 'сырок Б. Ю. Александров',
                        quantity: 0,
                        price: 47.99,
                        sum: 0,
                        vat: 10,
                        vat_sum: 4.799,
                        total_sum: 0
                    }
                ],
                wms_orders: []
            },
            {
                id: erpIds[1],
                number: '1',
                warehouse: {
                    id: '42',
                    wms_id: '',
                    name: 'ул. Тестовская, д. 0'
                },
                supplier: {
                    inn: '',
                    name: '',
                    id: '',
                    kpp: ''
                },
                items: [
                    {
                        id: '2',
                        wms_id: '',
                        supplier_id: 1,
                        name: 'сырок Б. Ю. Александров',
                        quantity: 0,
                        price: 47.99,
                        sum: 0,
                        vat: 10,
                        vat_sum: 4.799,
                        total_sum: 0
                    }
                ],
                wms_orders: []
            }
        ];

        getTasksFrom1cErp.mockReturnValue(
            new Promise((resolve) => {
                resolve(secondErpResponse);
            })
        );

        await updateErpData();

        const tasks2 = await conn.getRepository(Tasks).find();
        const expected2 = tasks2.filter((t) => t.externalId === erpIds[1])[0];

        expect(expected2.data.items[0].id).toBe('2');
    });
});
