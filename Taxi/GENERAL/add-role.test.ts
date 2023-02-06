import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import {getUserByLogin} from '@/src/entities/user/api/get-user-by-login';
import type {UserEntity} from '@/src/entities/user/entity';
import {getUserRolesByUid} from '@/src/entities/user-roles/api/get-user-role-by-uid';
import {FEATURE_ACCESS_NONE} from 'constants/idm';
import type {BaseApiRequestContext} from 'server/routes/api/api-context';
import {AnalystEntity} from 'types/analyst';
import {AccessToOptions, IdmCode, Role} from 'types/idm';

import {addRoleHandler} from './add-role';

describe('addRoleHandler', () => {
    let user: UserEntity;
    let context: BaseApiRequestContext;

    beforeEach(async () => {
        user = await TestFactory.createUser({skipRoleCreation: true});
        context = await TestFactory.createBaseApiContext();
    });

    it('should save global role and return OK', async () => {
        const res = await addRoleHandler.handle({
            data: {
                body: {
                    role: {project: 'group', role: Role.FULL_ACCESS},
                    login: user.login,
                    uid: user.uid,
                    path: '/project/group/role/full_access/',
                    fields: null
                }
            },
            context
        });
        const userRoles = await getUserRolesByUid(user.uid);

        expect(res.code).toEqual(IdmCode.OK);
        expect(userRoles).toHaveLength(1);
        expect(userRoles[0]).toMatchObject({
            userId: user.uid,
            role: Role.FULL_ACCESS,
            path: 'project.group.role.full_access'
        });
    });

    it('should create user and save role if user not exists', async () => {
        const login = 'fake-login';
        const uid = '666';
        const res = await addRoleHandler.handle({
            data: {
                body: {
                    role: {project: 'group', role: Role.FULL_ACCESS},
                    login,
                    uid,
                    path: '/project/group/role/full_access/',
                    fields: null
                }
            },
            context
        });
        const user = await getUserByLogin(login);

        expect(res.code).toEqual(IdmCode.OK);
        expect(user).toMatchObject({
            login,
            uid
        });
        expect(user?.roles).toHaveLength(1);
        expect(user?.roles?.[0]).toMatchObject({
            userId: uid,
            role: Role.FULL_ACCESS,
            path: 'project.group.role.full_access'
        });
    });

    it('should save role with fields', async () => {
        const res = await addRoleHandler.handle({
            data: {
                body: {
                    role: {project: 'group', role: Role.MANAGER},
                    login: user.login,
                    uid: user.uid,
                    path: '/project/group/role/manager/',
                    fields: JSON.stringify({
                        ...FEATURE_ACCESS_NONE,
                        [AnalystEntity.EDA_ORDERS_AVG_PRICE]: true,
                        [AnalystEntity.EDA_ORDERS_COUNT]: true,
                        [AccessToOptions.EXPORT]: true,
                        [AccessToOptions.ANALYST_FORECAST_ORDER]: true,
                        [AnalystEntity.SOCDEM_C1C2RES]: true
                    })
                }
            },
            context
        });
        const userRoles = await getUserRolesByUid(user.uid);

        expect(res.code).toEqual(IdmCode.OK);
        expect(userRoles).toHaveLength(1);
        expect(userRoles[0]).toMatchObject({
            userId: user.uid,
            role: Role.MANAGER,
            path: 'project.group.role.manager',
            fields: {
                [AnalystEntity.EDA_ORDERS_AVG_PRICE]: true,
                [AnalystEntity.EDA_ORDERS_COUNT]: true,
                [AccessToOptions.EXPORT]: true,
                [AccessToOptions.ANALYST_FORECAST_ORDER]: true,
                [AnalystEntity.SOCDEM_TTL_RESIDENTS_REAL]: false
            }
        });
    });
});
