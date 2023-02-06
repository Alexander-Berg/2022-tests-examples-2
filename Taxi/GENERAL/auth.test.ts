/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable no-async-promise-executor */
import mockdate from 'mockdate';
import moment from 'moment';
import {describe, expect, it} from 'tests/jest.globals';

import * as CreateUser from '@/src/entities/user/api/create-user';
import * as UpdateUser from '@/src/entities/user/api/update-user';
import {TestFactory} from '@/src/tests/unit/test-factory';
import * as TVM from 'service/tvm';

import authMiddleware, {staffClient} from './auth';

function executeAuthMiddleware(login: string): Promise<any> {
    return new Promise((resolve) => {
        authMiddleware(
            {
                blackbox: {
                    status: 'VALID',
                    uid: 'som_uid',
                    userTicket: 'some_user_ticket',
                    raw: {
                        login
                    }
                }
            } as any,
            {} as any,
            resolve
        );
    });
}

describe('test auth middleware', () => {
    beforeEach(() => {
        jest.spyOn(TVM, 'getServiceTicket').mockImplementation(async () => {
            return 'service-ticket-response';
        });
    });

    it('should create user if it does not exist', async () => {
        jest.spyOn(staffClient, 'getPerson').mockImplementationOnce(
            async () =>
                ({
                    staff: {data: 1}
                } as any)
        );

        const login = 'some_user';

        const results = await Promise.all([
            new Promise<void>((resolve) => {
                const createUser = CreateUser.createUser;

                jest.spyOn(CreateUser, 'createUser').mockImplementationOnce(async (...args) => {
                    const result = await createUser(...args);

                    resolve();

                    return result;
                });
            }),
            executeAuthMiddleware(login)
        ]);

        const error = results[1];

        expect(error).toBeFalsy();

        const users = await TestFactory.getUsers();

        expect(users).toHaveLength(1);

        expect(users[0]).toMatchObject({
            login,
            staffData: {staff: {data: 1}}
        });
    });

    it('should not change user data if ttl is not expired', async () => {
        const user = await TestFactory.createUser();

        const error = await executeAuthMiddleware(user.login);

        expect(error).toBeFalsy();

        const users = await TestFactory.getUsers();

        expect(users).toHaveLength(1);
        expect(users[0]).toMatchObject({
            login: user.login,
            staffData: user.staffData
        });
        expect(users[0].staffDataUpdatedAt.getTime()).toEqual(user.staffDataUpdatedAt.getTime());
    });

    it('should update user data if ttl was expired', async () => {
        const user = await TestFactory.createUser();

        mockdate.set(moment().add(2, 'days').toDate());

        const newStaffData = {someNewStaffData: Math.random()};

        jest.spyOn(staffClient, 'getPerson').mockImplementationOnce(async () => newStaffData as any);

        const updateUserStaffData = UpdateUser.updateUserStaffData;

        await Promise.all([
            new Promise<void>((resolve) => {
                jest.spyOn(UpdateUser, 'updateUserStaffData').mockImplementationOnce(async (...args) => {
                    const result = await updateUserStaffData(...args);

                    resolve();

                    return result;
                });
            }),
            executeAuthMiddleware(user.login)
        ]);

        const users = await TestFactory.getUsers();

        expect(users).toHaveLength(1);
        expect(users[0]).toMatchObject({
            login: user.login,
            staffData: newStaffData
        });

        expect(users[0].staffDataUpdatedAt.getTime()).toBeGreaterThan(user.staffDataUpdatedAt.getTime());
    });
});
