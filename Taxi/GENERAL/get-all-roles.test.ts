import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Region} from '@/src/entities/region/entity';
import type {Role} from '@/src/entities/role/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {CodeIdm} from 'types/idm';

import {getAllRolesHandler} from './get-all-roles';

describe('get all roles', () => {
    let user: User;
    let region: Region;
    let context: ApiRequestContext;
    let role: Role;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createApiContext({region, user});
        role = await TestFactory.createRole();
    });

    it('should return code OK and all created users if called with default params', async () => {
        const res1 = await getAllRolesHandler.handle({
            data: {},
            context
        });

        expect(res1.code).toEqual(CodeIdm.OK);
        expect(res1.users).toHaveLength(0);

        await TestFactory.createUserRole({userId: user.id, roleId: role.id});

        const res2 = await getAllRolesHandler.handle({
            data: {},
            context
        });

        expect(res2.code).toEqual(CodeIdm.OK);
        expect(res2.users).toHaveLength(1);

        const user1 = await TestFactory.createUser();
        await TestFactory.createUserRole({userId: user1.id, roleId: role.id});

        const res3 = await getAllRolesHandler.handle({
            data: {},
            context
        });

        expect(res3.code).toEqual(CodeIdm.OK);
        expect(res3.users).toHaveLength(2);
    });

    it('should return user with region role', async () => {
        await TestFactory.createUserRole({userId: user.id, roleId: role.id, regionId: region.id});
        const res = await getAllRolesHandler.handle({
            data: {},
            context
        });

        expect(res.code).toEqual(CodeIdm.OK);
        expect(res.users).toHaveLength(1);
        expect(res.users[0].roles).toMatchObject([{region: region.isoCode.toLowerCase(), roles: role.code}]);
    });

    it('should return user with global role', async () => {
        await TestFactory.createUserRole({userId: user.id, roleId: role.id});
        const res = await getAllRolesHandler.handle({
            data: {},
            context
        });

        expect(res.code).toEqual(CodeIdm.OK);
        expect(res.users).toHaveLength(1);
        expect(res.users[0].roles).toMatchObject([{roles: role.code}]);
        expect(res.users[0].roles[0].region).toBeUndefined();
    });
});
