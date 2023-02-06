import {describe, expect, it} from 'tests/jest.globals';
import {TestFactory} from 'tests/unit/test-factory';

import type {BaseApiRequestContext} from 'server/routes/api/api-context';
import {getRoleFromIdmPath} from 'server/utils/path-helper';
import {IdmCode, Role} from 'types/idm';

import {getRolesHandler} from './get-roles';

describe('getRolesHandler', () => {
    let context: BaseApiRequestContext;

    beforeEach(async () => {
        context = await TestFactory.createBaseApiContext();
    });

    it('should return code OK and all created users if called with default params', async () => {
        await TestFactory.createUser({role: Role.FULL_ACCESS});
        await TestFactory.createUser({role: Role.MANAGER});
        const res = await getRolesHandler.handle({
            data: {},
            context
        });

        expect(res.code).toEqual(IdmCode.OK);
        expect(res.roles).toHaveLength(2);

        const roles = res.roles.map(({path}) => getRoleFromIdmPath(path));
        expect(roles).toContain(Role.FULL_ACCESS);
        expect(roles).toContain(Role.MANAGER);
    });
});
