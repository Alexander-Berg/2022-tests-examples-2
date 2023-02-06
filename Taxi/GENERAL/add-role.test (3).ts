import {sortBy} from 'lodash';
import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {Region} from '@/src/entities/region/entity';
import type {Role} from '@/src/entities/role/entity';
import type {User} from '@/src/entities/user/entity';
import type {ApiRequestContext} from 'server/routes/api/api-handler';
import {CodeIdm} from 'types/idm';

import {addRoleHandler} from './add-role';

describe('add role', () => {
    let user: User;
    let region: Region;
    let context: ApiRequestContext;
    let roles: Role[];

    beforeEach(async () => {
        user = await TestFactory.createUser();
        region = await TestFactory.createRegion();
        context = await TestFactory.createApiContext({region, user});
        roles = await Promise.all([TestFactory.createRole(), TestFactory.createRole()]);
    });

    it('should return code OK', async () => {
        const res = await addRoleHandler.handle({
            data: {
                body: {
                    role: {roles: roles[0].code},
                    login: user.login,
                    path: '',
                    fields: 'null'
                }
            },
            context
        });

        expect(res.code).toEqual(CodeIdm.OK);
    });

    it('should create user if user not exist', async () => {
        const res = await addRoleHandler.handle({
            data: {
                body: {
                    role: {roles: roles[0].code},
                    login: 'fake-login',
                    path: '',
                    fields: ''
                }
            },
            context
        });

        expect(res.code).toBe(CodeIdm.OK);

        const users = await TestFactory.getUsers();
        expect(users).toHaveLength(2);

        const user = users.find((user) => user.login === 'fake-login');
        expect(user).toBeDefined();

        const userRole = await TestFactory.getUserRole(user?.id as number);
        expect(userRole?.role.code).toEqual(roles[0].code);
    });

    it('should replace role if user has another role', async () => {
        await addRoleHandler.handle({
            data: {
                body: {
                    role: {roles: roles[0].code},
                    login: user.login,
                    path: '',
                    fields: 'null'
                }
            },
            context
        });

        const userRole1 = await TestFactory.getUserRole(user.id);
        expect(userRole1?.role.code).toEqual(roles[0].code);

        await addRoleHandler.handle({
            data: {
                body: {
                    role: {roles: roles[1].code},
                    login: user.login,
                    path: '',
                    fields: 'null'
                }
            },
            context
        });

        const userRole2 = await TestFactory.getUserRole(user.id);
        expect(userRole2?.role.code).toEqual(roles[1].code);
    });

    it('should not replace region role if user has global role', async () => {
        await addRoleHandler.handle({
            data: {
                body: {
                    role: {roles: roles[0].code},
                    login: user.login,
                    path: '',
                    fields: 'null'
                }
            },
            context
        });

        {
            const userRoles = await TestFactory.getUserRoles(user.id);
            expect(userRoles).toHaveLength(1);
            expect(userRoles[0].regionId).toEqual(null);
        }

        await addRoleHandler.handle({
            data: {
                body: {
                    role: {roles: roles[1].code, region: region.isoCode},
                    login: user.login,
                    path: '',
                    fields: 'null'
                }
            },
            context
        });

        {
            const userRoles = await TestFactory.getUserRoles(user.id);
            expect(userRoles).toHaveLength(2);
            expect(userRoles).toMatchObject([
                {roleId: roles[0].id, regionId: null},
                {roleId: roles[1].id, regionId: region.id}
            ]);
        }
    });

    it('should not replace global role if user has region role', async () => {
        await addRoleHandler.handle({
            data: {
                body: {
                    role: {roles: roles[0].code, region: region.isoCode},
                    login: user.login,
                    path: '',
                    fields: 'null'
                }
            },
            context
        });

        {
            const userRoles = await TestFactory.getUserRoles(user.id);
            expect(userRoles).toHaveLength(1);
            expect(userRoles[0].regionId).toEqual(region.id);
        }

        await addRoleHandler.handle({
            data: {
                body: {
                    role: {roles: roles[1].code},
                    login: user.login,
                    path: '',
                    fields: 'null'
                }
            },
            context
        });

        {
            const userRoles = await TestFactory.getUserRoles(user.id);
            expect(userRoles).toHaveLength(2);
            expect(userRoles).toMatchObject([
                {roleId: roles[0].id, regionId: region.id},
                {roleId: roles[1].id, regionId: null}
            ]);
        }
    });

    it('should replace global role', async () => {
        await addRoleHandler.handle({
            data: {
                body: {
                    role: {roles: roles[0].code},
                    login: user.login,
                    path: '',
                    fields: 'null'
                }
            },
            context
        });

        {
            const userRoles = await TestFactory.getUserRoles(user.id);
            expect(userRoles).toHaveLength(1);
            expect(userRoles[0].regionId).toEqual(null);
            expect(userRoles[0].role.code).toEqual(roles[0].code);
        }

        await addRoleHandler.handle({
            data: {
                body: {
                    role: {roles: roles[1].code},
                    login: user.login,
                    path: '',
                    fields: 'null'
                }
            },
            context
        });

        {
            const userRoles = await TestFactory.getUserRoles(user.id);
            expect(userRoles).toHaveLength(1);
            expect(userRoles[0].regionId).toEqual(null);
            expect(userRoles[0].role.code).toEqual(roles[1].code);
        }
    });

    it('should replace region role', async () => {
        await addRoleHandler.handle({
            data: {
                body: {
                    role: {roles: roles[0].code, region: region.isoCode},
                    login: user.login,
                    path: '',
                    fields: 'null'
                }
            },
            context
        });

        {
            const userRoles = await TestFactory.getUserRoles(user.id);
            expect(userRoles).toHaveLength(1);
            expect(userRoles[0].regionId).toEqual(region.id);
            expect(userRoles[0].role.code).toEqual(roles[0].code);
        }

        await addRoleHandler.handle({
            data: {
                body: {
                    role: {roles: roles[1].code, region: region.isoCode},
                    login: user.login,
                    path: '',
                    fields: 'null'
                }
            },
            context
        });

        {
            const userRoles = await TestFactory.getUserRoles(user.id);
            expect(userRoles).toHaveLength(1);
            expect(userRoles[0].regionId).toEqual(region.id);
            expect(userRoles[0].role.code).toEqual(roles[1].code);
        }
    });

    it('should not replace region role in another regions', async () => {
        const region1 = await TestFactory.createRegion();

        const suites = [
            {
                role: {roles: roles[0].code, region: region.isoCode},
                expected: [{roleId: roles[0].id, regionId: region.id}]
            },

            {
                role: {roles: roles[0].code, region: region1.isoCode},
                expected: [
                    {roleId: roles[0].id, regionId: region.id},
                    {roleId: roles[0].id, regionId: region1.id}
                ]
            },

            {
                role: {roles: roles[1].code, region: region.isoCode},
                expected: [
                    {roleId: roles[1].id, regionId: region.id},
                    {roleId: roles[0].id, regionId: region1.id}
                ]
            },

            {
                role: {roles: roles[1].code, region: region1.isoCode},
                expected: [
                    {roleId: roles[1].id, regionId: region.id},
                    {roleId: roles[1].id, regionId: region1.id}
                ]
            }
        ];

        for (const suite of suites) {
            await addRoleHandler.handle({
                data: {
                    body: {
                        role: suite.role,
                        login: user.login,
                        path: '',
                        fields: 'null'
                    }
                },
                context
            });

            const userRoles = await TestFactory.getUserRoles(user.id);
            expect(userRoles).toHaveLength(suite.expected.length);
            expect(sortBy(userRoles, ({regionId}) => regionId)).toMatchObject(suite.expected);
        }
    });
});
