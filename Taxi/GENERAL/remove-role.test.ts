import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {UserEntity} from '@/src/entities/user/entity';
import type {BaseApiRequestContext} from 'server/routes/api/api-context';
import {IdmCode, Role} from 'types/idm';

import {getRolesHandler} from './get-roles';
import {removeRoleHandler} from './remove-role';

describe('removeRoleHandler', () => {
    let user: UserEntity;
    let context: BaseApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser();
        context = await TestFactory.createBaseApiContext();
    });

    it('should remove role from user and return code OK when given valid user role', async () => {
        const res = await removeRoleHandler.handle({
            data: {
                body: {
                    role: {project: 'group', role: Role.FULL_ACCESS},
                    login: user.login,
                    uid: user.uid,
                    path: '/project/group/role/full_access/',
                    fields: ''
                }
            },
            context
        });

        const resRoles = await getRolesHandler.handle({
            data: {},
            context
        });

        expect(res.code).toEqual(IdmCode.OK);

        expect(resRoles.roles).toHaveLength(0);
    });

    it("should return code OK even if user doesn't have the role", async () => {
        const res = await removeRoleHandler.handle({
            data: {
                body: {
                    role: {project: 'group', role: Role.ADMIN},
                    login: user.login,
                    uid: user.uid,
                    path: '/project/group/role/admin/',
                    fields: ''
                }
            },
            context
        });

        expect(res.code).toEqual(IdmCode.OK);
    });
});
