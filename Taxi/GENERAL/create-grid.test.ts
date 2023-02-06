/* eslint-disable @typescript-eslint/no-non-null-assertion */
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Lang} from '@/src/entities/lang/entity';
import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {CatalogStatus} from 'types/catalog/base';
import type {NewGrid} from 'types/catalog/grid';

import {createGridHandler} from './create-grid';

describe('create grid', () => {
    let user: User;
    let regions: Region[];
    let langs: Lang[];
    let langCodes: string[];
    let context: ApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser({rules: {catalog: {canEdit: true}}});
        regions = await Promise.all([TestFactory.createRegion(), TestFactory.createRegion()]);
        langs = await Promise.all([TestFactory.createLang(), TestFactory.createLang()]);
        langCodes = langs.map(({isoCode}) => isoCode);
        context = await TestFactory.createApiContext({user, region: regions[0], lang: langs[0]});
    });

    it('should create gird', async () => {
        const gridParams: NewGrid = {
            code: 'grid',
            status: CatalogStatus.ACTIVE,
            shortTitleTranslations: {
                [langCodes[0]]: 'сетка',
                [langCodes[1]]: 'grid'
            },
            longTitleTranslations: {
                [langCodes[0]]: 'сетка',
                [langCodes[1]]: 'grid'
            },
            meta: {foo: 'bar'},
            description: 'description'
        };

        const result = await createGridHandler.handle({context, data: {body: gridParams}});
        const createdGrid = (await TestFactory.getGrids()).find(({id}) => id === result.id)!;

        expect(createdGrid).toBeTruthy();
        expect(result).toEqual({
            ...gridParams,
            id: createdGrid.id,
            legacyId: createdGrid.legacyId,
            region: {
                id: regions[0].id,
                isoCode: regions[0].isoCode
            },
            groups: [],
            author: {
                login: user.login,
                firstName: user.staffData.name.first,
                lastName: user.staffData.name.last
            },
            createdAt: expect.any(Date),
            updatedAt: expect.any(Date)
        });
    });
});
