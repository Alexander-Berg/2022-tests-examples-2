import {Companies} from '@/src/entities/companies/entity';
import {ensureConnection} from 'service/db';
import type {CompanyDataFromWms} from 'service/helper/get-companies-from-wms';
import * as wms from 'service/helper/get-companies-from-wms';

import {fetchCompanies} from './index';

const getCompaniesFromWms = jest.spyOn(wms, 'getCompaniesFromWms');

describe('Schedulers', () => {
    it('should insert stores from wms', async () => {
        const wmsResponse: CompanyDataFromWms[] = [
            {
                externalId: 'b3d892aa29e14e199ac08974b49d9bdb000200010000',
                title: 'ООО "Яндекс.Лавка"',
                updated: new Date('2022-02-22T11:53:39.000Z')
            },
            {
                externalId: 'b316f05d34954c70898978b790b6e28f000300010000',
                title: 'Yandex Lavka',
                updated: new Date('2022-02-08T13:31:05.000Z')
            },
            {
                externalId: 'dd6d5789ec4d4283844c3aad91bc032d000500020002',
                title: 'YanGo France',
                updated: new Date('2021-11-11T14:25:44.000Z')
            },
            {
                externalId: '6490c0508a8c4370be75096d9f0ef615000200010001',
                title: 'ООО "Яндекс.Лавка"',
                updated: new Date('2022-01-20T14:02:26.000Z')
            },
            {
                externalId: 'b8c2a41aea0e45d8a106adb743fcbb85000400020002',
                title: 'Тест',
                updated: new Date('2021-08-31T09:52:33.000Z')
            },
            {
                externalId: 'a59c379797e34240b68e0a85bf1a8430000500020002',
                title: 'Лавка Англия',
                updated: new Date('2021-07-15T08:46:07.000Z')
            },
            {
                externalId: '61f541e2c6ae4f94b494fa95d6f3adb0000200010001',
                title: 'Лавка Израиль ',
                updated: new Date('2021-06-21T10:58:15.000Z')
            }
        ];

        getCompaniesFromWms.mockReturnValue(
            new Promise((resolve) => {
                resolve(wmsResponse);
            })
        );

        await fetchCompanies();

        const conn = await ensureConnection();
        const companies1 = await conn.getRepository(Companies).find();

        expect(companies1).toHaveLength(wmsResponse.length);
    });
});
