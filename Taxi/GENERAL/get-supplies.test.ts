import casual from 'casual';
import {addDays, compareAsc, compareDesc, isAfter, subDays} from 'date-fns';
import {groupBy, keys, times} from 'lodash';

import {Tasks} from '@/src/entities/tasks/entity';
import {generateStores, generateTasks, generateUsersTasks} from '@/src/test/test-factory';
import {getSupplies} from 'server/routes/api/v1/supplies/get-supplies';
import type {ApiRequestContext} from 'server/routes/api-handler';
import * as GetUserStores from 'server/routes/utils/get-user-stores';
import {ensureConnection} from 'service/db';
import {startOfDay} from 'service/utils/date-helper';
import {RecognitionRequestStatus} from 'types/task';

const getUserStores = jest.spyOn(GetUserStores, 'getUserStores');

const RecognitionRequestNotNewStatus = Object.values(RecognitionRequestStatus).filter(
    (status) => status !== RecognitionRequestStatus.NEW
);

describe('should get supplies correctly', () => {
    casual.seed(123);

    const tasksNumber = 10000;
    const startOfDayInPast = startOfDay(addDays(new Date(), -1000), true);
    const suppliersNames = times(10, () => casual.company_name);

    const randomNumbersArray = times(5, () => casual.array_of_digits(4).join(''));
    const randomWordsArray = times(5, () =>
        times(5, () => (casual.integer(0, 1) === 0 ? casual.letter.toLowerCase() : casual.letter.toUpperCase())).join(
            ''
        )
    );

    const suppliersInn = times(tasksNumber, () => times(3, () => casual.random_element(randomNumbersArray)).join(''));
    const suppliesNumbers = times(tasksNumber, () => times(3, () => casual.random_element(randomWordsArray)).join(''));

    beforeEach(async () => {
        const stores = await generateStores(5, () => ({}));
        await generateTasks(tasksNumber, (index) => ({
            storeId: () => stores.raw[index % 5].id,
            date: () => addDays(startOfDayInPast, casual.integer(0, 100)),
            recognition_request_status: () => {
                if (index % 3 === 0) {
                    return RecognitionRequestStatus.NEW;
                }
                if (index % 3 === 1) {
                    return RecognitionRequestStatus.FINISHED;
                }
                return RecognitionRequestStatus.VERIFIED;
            },
            recognized_at: () => addDays(new Date(), index),
            data: {
                supplier: () => ({
                    id: index.toString(),
                    name: casual.random_element(suppliersNames),
                    kpp: index.toString(),
                    inn: casual.random_element(suppliersInn)
                }),
                number: () => casual.random_element(suppliesNumbers)
            }
        }));

        await generateUsersTasks([
            {user: {login: 'vasya'}, takenUntil: addDays(new Date(), 1)},
            {user: {login: 'petya'}, takenUntil: subDays(new Date(), 1)}
        ]);

        getUserStores.mockResolvedValue({
            allStoresAccess: true,
            storesIds: []
        });
    });

    it('just works', async () => {
        const connection = await ensureConnection();

        const result = await getSupplies(
            connection.manager,
            {
                body: {
                    offset: 0,
                    limit: tasksNumber,
                    filters: {
                        dateRange: [undefined, undefined],
                        storeIds: [],
                        statuses: [RecognitionRequestStatus.NEW],
                        onlyInProgress: false
                    },
                    order: undefined
                }
            },
            ({
                getUser: async () => {
                    return {
                        id: 0
                    };
                }
            } as unknown) as ApiRequestContext
        );

        const allTasks = await connection.getRepository(Tasks).find();
        const expectedTasks = allTasks.filter(
            (task) => task.recognition_request_status === RecognitionRequestStatus.NEW
        );

        expect(result.totalCount).toBe(expectedTasks.length);
        expect(result.list).toHaveLength(result.totalCount);
        expect(result.suppliersNames.sort((first, second) => first.localeCompare(second))).toStrictEqual(
            keys(groupBy(result.list.map((supply) => supply.supplier.name))).sort((first, second) =>
                first.localeCompare(second)
            )
        );
    });

    describe('filters', () => {
        it('supplier filter', async () => {
            const connection = await ensureConnection();
            const allTasks = await connection.getRepository(Tasks).find();

            await Promise.all(
                times(3, async () => {
                    const supplierNameToFind = casual.random_element(suppliersNames);

                    const result = await getSupplies(
                        connection.manager,
                        {
                            body: {
                                offset: 0,
                                limit: tasksNumber,
                                filters: {
                                    dateRange: [undefined, undefined],
                                    supplierName: supplierNameToFind,
                                    storeIds: [],
                                    statuses: [RecognitionRequestStatus.NEW],
                                    onlyInProgress: false
                                }
                            }
                        },
                        ({
                            getUser: async () => {
                                return {
                                    id: 0
                                };
                            }
                        } as unknown) as ApiRequestContext
                    );

                    const expectedTasks = allTasks.filter(
                        (task) =>
                            task.recognition_request_status === RecognitionRequestStatus.NEW &&
                            task.data.supplier?.name === supplierNameToFind
                    );

                    // проверяем валидность теста
                    expect(expectedTasks.length).toBeGreaterThan(10);

                    expect(result.totalCount).toBe(expectedTasks.length);

                    for (const supply of result.list) {
                        expect(supply.supplier.name).toBe(supplierNameToFind);
                    }
                })
            );
        });

        describe('date filter', () => {
            it('just works', async () => {
                const connection = await ensureConnection();
                const allTasks = await connection.getRepository(Tasks).find();

                await Promise.all(
                    times(3, async () => {
                        const firstDate = addDays(startOfDayInPast, casual.integer(0, 50));
                        const secondDate = addDays(startOfDayInPast, casual.integer(51, 100));
                        const dateRange: [Date, Date] = [firstDate, secondDate];

                        const result = await getSupplies(
                            connection.manager,
                            {
                                body: {
                                    offset: 0,
                                    limit: tasksNumber,
                                    filters: {
                                        dateRange,
                                        storeIds: [],
                                        statuses: [RecognitionRequestStatus.NEW],
                                        onlyInProgress: false
                                    },
                                    order: undefined
                                }
                            },
                            ({
                                getUser: async () => {
                                    return {
                                        id: 0
                                    };
                                }
                            } as unknown) as ApiRequestContext
                        );

                        const expectedTasks = allTasks.filter(
                            (task) =>
                                task.recognition_request_status === RecognitionRequestStatus.NEW &&
                                compareAsc(new Date(task.date), firstDate) !== -1 &&
                                compareDesc(new Date(task.date), addDays(secondDate, 1)) === 1
                        );

                        // проверяем валидность теста
                        expect(expectedTasks.length).toBeGreaterThan(10);

                        expect(result.totalCount).toBe(expectedTasks.length);

                        for (const supply of result.list) {
                            expect(new Date(supply.date).valueOf()).toBeGreaterThanOrEqual(firstDate.valueOf());
                            expect(new Date(supply.date).valueOf()).toBeLessThan(addDays(secondDate, 1).valueOf());
                        }
                    })
                );
            });

            it.skip('interval boundaries', async () => {
                const connection = await ensureConnection();
                const allTasks = await connection.getRepository(Tasks).find();

                await Promise.all(
                    times(3, async () => {
                        const firstBoundary = addDays(startOfDayInPast, casual.integer(1, 50));
                        const secondBoundary = addDays(startOfDayInPast, casual.integer(51, 100));
                        for (let i = -1; i <= 0; ++i) {
                            for (let j = -1; j <= 0; j++) {
                                const firstDate = addDays(firstBoundary, i);
                                const secondDate = addDays(secondBoundary, j);

                                const dateRange: [Date, Date] = [firstDate, secondDate];

                                const result = await getSupplies(
                                    connection.manager,
                                    {
                                        body: {
                                            offset: 0,
                                            limit: tasksNumber,
                                            filters: {
                                                dateRange,
                                                storeIds: [],
                                                statuses: [RecognitionRequestStatus.NEW],
                                                onlyInProgress: false
                                            },
                                            order: undefined
                                        }
                                    },
                                    ({
                                        getUser: async () => {
                                            return {
                                                id: 0
                                            };
                                        }
                                    } as unknown) as ApiRequestContext
                                );

                                const expectedTasks = allTasks.filter(
                                    (task) =>
                                        task.recognition_request_status === RecognitionRequestStatus.NEW &&
                                        compareAsc(new Date(task.date), firstDate) !== -1 &&
                                        compareDesc(new Date(task.date), addDays(secondDate, 1)) === 1
                                );

                                // проверяем валидность теста
                                expect(expectedTasks.length).toBeGreaterThan(10);

                                expect(result.totalCount).toBe(expectedTasks.length);

                                for (const supply of result.list) {
                                    expect(new Date(supply.date).valueOf()).toBeGreaterThanOrEqual(firstDate.valueOf());
                                    expect(new Date(supply.date).valueOf()).toBeLessThan(
                                        addDays(secondDate, 1).valueOf()
                                    );
                                }
                            }
                        }
                    })
                );
            });
        });

        it('document name filter', async () => {
            const connection = await ensureConnection();

            const allTasks = await connection.getRepository(Tasks).find();

            await Promise.all(
                times(3, async () => {
                    const documentNumberToFind = times(3, () =>
                        casual.boolean ? casual.random_element(randomWordsArray) : ''
                    )
                        .join('')
                        .split('')
                        .map((letter) => (casual.boolean ? letter.toLocaleLowerCase() : letter.toLocaleUpperCase()))
                        .join('');

                    const result = await getSupplies(
                        connection.manager,
                        {
                            body: {
                                offset: 0,
                                limit: tasksNumber,
                                filters: {
                                    storeIds: [],
                                    dateRange: [undefined, undefined],
                                    documentNumber: documentNumberToFind,
                                    statuses: [RecognitionRequestStatus.NEW],
                                    onlyInProgress: false
                                },
                                order: undefined
                            }
                        },
                        ({
                            getUser: async () => {
                                return {
                                    id: 0
                                };
                            }
                        } as unknown) as ApiRequestContext
                    );

                    const documentNumberRegExp = new RegExp(`.*${documentNumberToFind.toLocaleLowerCase()}.*`);

                    const expectedTasks = allTasks.filter(
                        (task) =>
                            task.recognition_request_status === RecognitionRequestStatus.NEW &&
                            documentNumberRegExp.test(task.data.number.toLocaleLowerCase())
                    );

                    // проверяем валидность теста
                    expect(expectedTasks.length).toBeGreaterThan(10);

                    for (const supply of result.list) {
                        expect(supply.name.toLocaleLowerCase()).toMatch(documentNumberRegExp);
                    }
                    expect(result.totalCount).toBe(expectedTasks.length);
                })
            );
        });

        it('inn filter', async () => {
            const connection = await ensureConnection();

            const allTasks = await connection.getRepository(Tasks).find();

            await Promise.all(
                times(3, async () => {
                    const supplierInnToFind = times(3, () =>
                        casual.boolean ? casual.random_element(randomNumbersArray) : ''
                    ).join('');

                    const result = await getSupplies(
                        connection.manager,
                        {
                            body: {
                                offset: 0,
                                limit: tasksNumber,
                                filters: {
                                    storeIds: [],
                                    dateRange: [undefined, undefined],
                                    supplierInn: supplierInnToFind,
                                    statuses: [RecognitionRequestStatus.NEW],
                                    onlyInProgress: false
                                },
                                order: undefined
                            }
                        },
                        ({
                            getUser: async () => {
                                return {
                                    id: 0
                                };
                            }
                        } as unknown) as ApiRequestContext
                    );

                    const supplierInnRegExp = new RegExp(`^${supplierInnToFind}`);

                    const expectedTasks = allTasks.filter(
                        (task) =>
                            task.recognition_request_status === RecognitionRequestStatus.NEW &&
                            supplierInnRegExp.test(task.data.supplier?.inn.toString() ?? '')
                    );

                    // проверяем валидность теста
                    expect(expectedTasks.length).toBeGreaterThan(10);

                    for (const supply of result.list) {
                        expect(supply.tin).toMatch(supplierInnRegExp);
                    }
                    expect(result.totalCount).toBe(expectedTasks.length);
                })
            );
        });

        it('onlyInProgress filter', async () => {
            const connection = await ensureConnection();

            const result = await getSupplies(
                connection.manager,
                {
                    body: {
                        offset: 0,
                        limit: tasksNumber,
                        filters: {
                            dateRange: [undefined, undefined],
                            supplierName: undefined,
                            statuses: [RecognitionRequestStatus.NEW],
                            storeIds: [],
                            onlyInProgress: true
                        },
                        order: ['status', 'ASC']
                    }
                },
                ({
                    getUser: async () => {
                        return {
                            id: 0
                        };
                    }
                } as unknown) as ApiRequestContext
            );

            expect(result.list).toHaveLength(1);
            expect(result.totalCount).toBe(1);
            expect(result.suppliersNames).toHaveLength(1);

            const [supplierName] = result.suppliersNames;
            const [task] = result.list;

            expect(supplierName).toBeString();
            expect(task.takenByUser.login).toBe('vasya');
            expect(task.takenUntil).toBeInstanceOf(Date);
            expect(isAfter((task.takenUntil as unknown) as Date, new Date())).toBeTrue();
        });

        describe('statuses filter', () => {
            it('filters by status', async () => {
                const filterStatuses = [RecognitionRequestStatus.FINISHED, RecognitionRequestStatus.VERIFIED];
                const restStatuses = Object.values(RecognitionRequestStatus).filter(
                    (status) => !filterStatuses.includes(status)
                );

                const connection = await ensureConnection();

                const result = await getSupplies(
                    connection.manager,
                    {
                        body: {
                            offset: 0,
                            limit: tasksNumber,
                            filters: {
                                dateRange: [undefined, undefined],
                                supplierName: undefined,
                                storeIds: [],
                                statuses: [...filterStatuses],
                                onlyInProgress: false
                            },
                            order: ['status', 'ASC']
                        }
                    },
                    ({
                        getUser: async () => {
                            return {
                                id: 0
                            };
                        }
                    } as unknown) as ApiRequestContext
                );

                const statuses = new Set(result.list.map((supply) => supply.status));

                expect(statuses.size).toBe(2);

                filterStatuses.forEach((status) => {
                    expect(statuses).toContain(status);
                });

                expect(restStatuses.length).toBeGreaterThan(0);

                restStatuses.forEach((status) => {
                    expect(statuses).not.toContain(status);
                });
            });

            it("filters doesn't filter if status is empty", async () => {
                const connection = await ensureConnection();

                const result = await getSupplies(
                    connection.manager,
                    {
                        body: {
                            offset: 0,
                            limit: tasksNumber,
                            filters: {
                                dateRange: [undefined, undefined],
                                supplierName: undefined,
                                storeIds: [],
                                onlyInProgress: false
                            },
                            order: ['status', 'ASC']
                        }
                    },
                    ({
                        getUser: async () => {
                            return {
                                id: 0
                            };
                        }
                    } as unknown) as ApiRequestContext
                );

                const statuses = new Set(result.list.map((supply) => supply.status));

                [
                    RecognitionRequestStatus.FINISHED,
                    RecognitionRequestStatus.VERIFIED,
                    RecognitionRequestStatus.NEW
                ].forEach((status) => {
                    expect(statuses).toContain(status);
                });
            });
        });
    });

    describe('sort', () => {
        it('status', async () => {
            const connection = await ensureConnection();

            const result = await getSupplies(
                connection.manager,
                {
                    body: {
                        offset: 0,
                        limit: tasksNumber,
                        filters: {
                            dateRange: [undefined, undefined],
                            supplierName: undefined,
                            storeIds: [],
                            statuses: RecognitionRequestNotNewStatus,
                            onlyInProgress: false
                        },
                        order: ['status', 'ASC']
                    }
                },
                ({
                    getUser: async () => {
                        return {
                            id: 0
                        };
                    }
                } as unknown) as ApiRequestContext
            );

            const statuses = result.list.map((supply) => supply.status);

            expect(statuses).toStrictEqual([...statuses].sort((first, second) => first.localeCompare(second)));
        });

        it('supplier', async () => {
            const connection = await ensureConnection();

            const result = await getSupplies(
                connection.manager,
                {
                    body: {
                        offset: 0,
                        limit: tasksNumber,
                        filters: {
                            dateRange: [undefined, undefined],
                            supplierName: undefined,
                            storeIds: [],
                            statuses: RecognitionRequestNotNewStatus,
                            onlyInProgress: false
                        },
                        order: ['supplier', 'DESC']
                    }
                },
                ({
                    getUser: async () => {
                        return {
                            id: 0
                        };
                    }
                } as unknown) as ApiRequestContext
            );

            const suppliers = result.list.map((supply) => supply.supplier.name);

            expect(suppliers).toStrictEqual([...suppliers].sort((first, second) => second.localeCompare(first)));
        });
    });
});
