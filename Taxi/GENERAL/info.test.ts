import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Region} from '@/src/entities/region/entity';
import type {Role} from '@/src/entities/role/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';

import {getInfoHandler} from './info';

describe('roles info', () => {
    let user: User;
    let region: Region;
    let context: ApiRequestContext;
    let role: Role;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createApiContext({region, user});
        role = await TestFactory.createRole();
        await TestFactory.createUserRole({userId: user.id, roleId: role.id});
    });

    it('should return role with regions', async () => {
        const info = await getInfoHandler.handle({context, data: {}});

        expect(info.code).toEqual(0);

        expect(info.roles.values.global.roles?.values[role.code]).toMatchObject({set: role.code});
        expect(
            info.roles.values.region.roles?.values[region.isoCode.toLowerCase()].roles?.values?.[role.code]
        ).toMatchObject({
            set: role.code
        });
    });
});
