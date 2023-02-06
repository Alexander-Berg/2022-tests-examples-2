import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Region} from '@/src/entities/region/entity';
import type {Role} from '@/src/entities/role/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {CodeIdm} from 'types/idm';

import {removeRoleHandler} from './remove-role';

describe('remove role', () => {
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

    it('should remove role from user and return code OK when given valid user role', async () => {
        const user = await context.getUser();
        await TestFactory.createUserRole({userId: user.id, roleId: role.id});

        const res = await removeRoleHandler.handle({
            data: {
                body: {
                    role: {roles: role.code},
                    login: user.login,
                    path: '',
                    fields: 'null'
                }
            },
            context
        });

        const userRole = await TestFactory.getUserRole(user.id);

        expect(userRole).toBeUndefined();

        expect(res.code).toEqual(CodeIdm.OK);
    });

    it('should not remove global role when removing region role', async () => {
        await TestFactory.createUserRole({userId: user.id, roleId: role.id});
        const res = await removeRoleHandler.handle({
            data: {
                body: {
                    role: {roles: role.code, region: region.isoCode},
                    login: user.login,
                    path: '',
                    fields: 'null'
                }
            },
            context
        });

        const userRole = await TestFactory.getUserRole(user.id);

        expect(userRole).toBeDefined();

        expect(res.code).toEqual(CodeIdm.OK);
    });

    it('should not remove region role when removing global role', async () => {
        await TestFactory.createUserRole({userId: user.id, roleId: role.id, regionId: region.id});
        const res = await removeRoleHandler.handle({
            data: {
                body: {
                    role: {roles: role.code},
                    login: user.login,
                    path: '',
                    fields: 'null'
                }
            },
            context
        });

        const userRole = await TestFactory.getUserRole(user.id);

        expect(userRole).toBeDefined();

        expect(res.code).toEqual(CodeIdm.OK);
    });
});
