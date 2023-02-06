import pMap from 'p-map';
import {beforeEach, describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Region} from '@/src/entities/region/entity';
import type {User} from '@/src/entities/user/entity';
import {config} from 'service/cfg';
import {CatalogStatus} from 'types/catalog/base';

import {getGroups} from './index';

describe('get groups', () => {
    let user: User;
    let region: Region;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
    });

    it('should return groups', async () => {
        const groups = await pMap(
            [
                {
                    userId: user.id,
                    regionId: region.id
                },
                {
                    userId: user.id,
                    regionId: region.id,
                    status: CatalogStatus.DISABLED
                },
                {
                    userId: user.id,
                    regionId: region.id,
                    meta: {foo: 'bar'}
                }
            ],
            TestFactory.createGroup,
            {concurrency: 1}
        );

        await expect(getGroups({lastCursor: 0, limit: 2})).resolves.toEqual({
            lastCursor: 2,
            items: [
                {
                    id: groups[0].id,
                    legacyId: groups[0].legacyId,
                    alias: groups[0].code,
                    shortTitleTankerKey: {
                        keyset: config.tankerExport.catalogKeyset,
                        key: `group:${region.isoCode}:${groups[0].code}:short`
                    },
                    longTitleTankerKey: {
                        keyset: config.tankerExport.catalogKeyset,
                        key: `group:${region.isoCode}:${groups[0].code}:long`
                    },
                    meta: {}
                },
                {
                    id: groups[2].id,
                    legacyId: groups[2].legacyId,
                    alias: groups[2].code,
                    shortTitleTankerKey: {
                        keyset: config.tankerExport.catalogKeyset,
                        key: `group:${region.isoCode}:${groups[2].code}:short`
                    },
                    longTitleTankerKey: {
                        keyset: config.tankerExport.catalogKeyset,
                        key: `group:${region.isoCode}:${groups[2].code}:long`
                    },
                    meta: {foo: 'bar'}
                }
            ]
        });
    });
});
