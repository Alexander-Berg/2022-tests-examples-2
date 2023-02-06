import {times} from 'lodash';
import {TestFactory} from 'tests/unit/test-factory';

import {Role} from '@/src/entities/role/entity';
import {User} from '@/src/entities/user/entity';
import {UserRole} from '@/src/entities/user-role/entity';

import {UserRoleSaver} from './user-role-saver';

function dropId<T extends {id: number | string}>({id: _, ...rest}: T) {
    return rest;
}

describe('user role saver', () => {
    let userRoleSaver: UserRoleSaver;

    beforeEach(() => {
        userRoleSaver = new UserRoleSaver();
    });

    it('should save and restore users', async () => {
        const oldUsers = await Promise.all(times(3, () => TestFactory.createUser()));

        await userRoleSaver.save();

        const manager = await TestFactory.getManager();
        await manager.createQueryBuilder().delete().from(User).execute();

        expect(await TestFactory.getUsers()).toHaveLength(0);

        const newUsers = await Promise.all(times(5, () => TestFactory.createUser()));

        await userRoleSaver.restore();

        const totalUsers = await TestFactory.getUsers();

        expect(totalUsers).toHaveLength(8);
        expect(totalUsers.map(dropId)).toMatchObject([...newUsers.map(dropId), ...oldUsers.map(dropId)]);
    });

    it('should ignore users with same login', async () => {
        const oldUsers = await Promise.all(times(3, () => TestFactory.createUser()));

        await userRoleSaver.save();

        const newUsers = await Promise.all(times(5, () => TestFactory.createUser()));

        await userRoleSaver.restore();

        const totalUsers = await TestFactory.getUsers();

        expect(totalUsers).toHaveLength(8);
        expect(totalUsers.map(dropId)).toMatchObject([...oldUsers.map(dropId), ...newUsers.map(dropId)]);
    });

    it('should save and restore roles', async () => {
        const oldRoles = await Promise.all(times(3, () => TestFactory.createRole({canDebug: true})));

        await userRoleSaver.save();

        const manager = await TestFactory.getManager();
        await manager.createQueryBuilder().delete().from(Role).execute();

        expect(await TestFactory.getRoles()).toHaveLength(0);

        await Promise.all(times(5, () => TestFactory.createRole({canBulk: true})));

        await userRoleSaver.restore();

        const totalRoles = await TestFactory.getRoles();

        expect(totalRoles).toHaveLength(3);
        expect(totalRoles.map(dropId)).toMatchObject([...oldRoles.map(dropId)]);
    });

    it('should remove new roles', async () => {
        const oldRoles = await Promise.all(times(3, () => TestFactory.createRole({canDebug: true})));

        await userRoleSaver.save();

        await Promise.all(times(5, () => TestFactory.createRole({canBulk: true})));

        await userRoleSaver.restore();

        const totalRoles = await TestFactory.getRoles();

        expect(totalRoles).toHaveLength(3);
        expect(totalRoles.map(dropId)).toMatchObject([...oldRoles.map(dropId)]);
    });

    it('should save and restore user roles', async () => {
        const oldUsers = await Promise.all(times(3, () => TestFactory.createUser({rules: {canDebug: true}})));
        const oldRoles = await TestFactory.getRoles();

        await userRoleSaver.save();

        const manager = await TestFactory.getManager();

        await manager.createQueryBuilder().delete().from(UserRole).execute();

        await Promise.all([
            manager.createQueryBuilder().delete().from(User).execute(),
            manager.createQueryBuilder().delete().from(Role).execute()
        ]);

        expect(await TestFactory.getRoles()).toHaveLength(0);
        expect(await TestFactory.getUsers()).toHaveLength(0);

        const newUsers = await Promise.all(times(5, () => TestFactory.createUser({rules: {canBulk: true}})));

        await userRoleSaver.restore();

        const totalUsers = await TestFactory.getUsers();

        expect(totalUsers).toHaveLength(8);
        expect(totalUsers.map(dropId)).toMatchObject([...newUsers.map(dropId), ...oldUsers.map(dropId)]);

        const totalRoles = await TestFactory.getRoles();

        expect(totalRoles).toHaveLength(3);
        expect(totalRoles.map(dropId)).toMatchObject([...oldRoles.map(dropId)]);
    });
});
