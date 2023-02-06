/* eslint-disable max-len */

import fs from 'fs';
import moment from 'moment';
import type {Connection, EntityManager} from 'typeorm';

import {ErpRecognitionResults} from '@/src/entities/erp-recognition-results/entity';
import {ErpRecognitionResultsHistory} from '@/src/entities/history/entity';
import {Stores} from '@/src/entities/stores/entity';
import {Tasks} from '@/src/entities/tasks/entity';
import {Users} from '@/src/entities/users/entity';
import {UsersStores} from '@/src/entities/users-stores/entity';
import {serviceResolve} from '@/src/lib/resolve';
import {executeInTransaction, executeInTransactionWithAuthor} from 'service/db';
import type {DocumentsRecognizedBasicInfo, ErpRecognitionResult} from 'types/erp-recognition-results';
import {RecognitionRequestStatus} from 'types/task';

import {createReport, GetReportInputParamsType} from './get-user-report';

interface TestTask {
    taskId: number;
    erpRecognitionResultId: number;
    isQualifiedProcessingRequired: boolean;
}

describe('should create users report correctly', () => {
    const query: GetReportInputParamsType = {
        firstDate: moment().subtract(3, 'days').toDate(),
        lastDate: moment().add(1, 'day').toDate()
    };

    let usersIds: number[] = [];
    let storeId = 1;
    let nextExternalTaskId = 4000;

    const commonInitResult: ErpRecognitionResult = JSON.parse(
        fs.readFileSync(
            serviceResolve('./src/server/routes/api/v1/users/samples/init-states/common-result.json'),
            'utf8'
        )
    );

    const commitInitBasicInfo: DocumentsRecognizedBasicInfo = JSON.parse(
        fs.readFileSync(
            serviceResolve('./src/server/routes/api/v1/users/samples/init-states/common-basic-info.json'),
            'utf8'
        )
    );

    async function addTask(
        connection: Connection | EntityManager,
        {
            recognitionRequestStatus = RecognitionRequestStatus.VERIFIED,
            requireQualifiedProcessing = false,
            result = commonInitResult,
            updatedAt = new Date()
        }: {
            recognitionRequestStatus?: RecognitionRequestStatus;
            requireQualifiedProcessing?: boolean;
            result?: ErpRecognitionResult;
            updatedAt?: Date;
        }
    ): Promise<TestTask> {
        const insertedTask = await connection.getRepository(Tasks).insert({
            externalId: nextExternalTaskId.toString(),
            storeId,
            data: {
                id: '5f6a3d70-08ba-arrrrrr-329e-525400123456',
                date: '2022-05-14T09:00:00.000Z',
                items: [
                    {
                        id: '2676',
                        sum: 41.65,
                        total_sum: 49,
                        name: 'Сырок Б. Ю. Александров',
                        price: 41.65,
                        wms_id: '1ed883d4b482455881cfaed20e6dada9000300010000',
                        quantity: 1,
                        supplier_id: 1,
                        vat: 15,
                        vat_sum: 7.35
                    }
                ],
                number: 'ЯЛ00-814061',
                supplier: {id: '1', inn: '2', kpp: '3', name: 'Хлеб Насущный'},
                warehouse: {
                    id: 'qwerty_id',
                    name: 'Test store',
                    wms_id: 'cc1b25dd93614ebda12b2f7eca8a18ca000300010000'
                }
            },
            recognized_at: updatedAt,
            recognition_request_status: recognitionRequestStatus
        });

        nextExternalTaskId++;

        const taskId = insertedTask.identifiers[0].id;
        const task: TestTask = {
            taskId,
            erpRecognitionResultId: 0,
            isQualifiedProcessingRequired: requireQualifiedProcessing
        };

        const erpRecognitionResultId = await addErpRecognitionResult(connection, task, {
            requireQualifiedProcessing,
            result,
            updatedAt
        });

        task.erpRecognitionResultId = erpRecognitionResultId;

        return task;
    }

    async function updateErpRecognitonResult(
        connection: Connection | EntityManager,
        task: TestTask,
        result: ErpRecognitionResult,
        updatedAt = new Date()
    ) {
        await connection
            .getRepository(ErpRecognitionResults)
            .update({id: task.erpRecognitionResultId}, {result, updatedAt});

        await updateLastHistoryRowDate(connection, task, updatedAt);
    }

    async function updateLastHistoryRowDate(
        connection: Connection | EntityManager,
        task: TestTask,
        updatedAt = new Date()
    ) {
        const lastHistoryRow = await connection
            .getRepository(ErpRecognitionResultsHistory)
            .findOne({where: {erpRecognitionResultId: task.erpRecognitionResultId}, order: {id: 'DESC'}});

        await connection
            .getRepository(ErpRecognitionResultsHistory)
            .update({id: lastHistoryRow?.id}, {createdAt: updatedAt});
    }

    async function addBasicInfoToHistory(
        connection: Connection | EntityManager,
        task: TestTask,
        basicInfo: DocumentsRecognizedBasicInfo
    ) {
        await connection
            .getRepository(ErpRecognitionResults)
            .update(
                {id: task.erpRecognitionResultId},
                {documentsRecognizedBasicInfo: basicInfo, updatedAt: new Date()}
            );
    }

    async function deleteErpRecognitionResult(
        connection: Connection | EntityManager,
        task: TestTask,
        updatedAt = new Date()
    ) {
        await connection.getRepository(ErpRecognitionResults).delete({id: task.erpRecognitionResultId});
        await updateLastHistoryRowDate(connection, task, updatedAt);
    }

    async function addErpRecognitionResult(
        connection: Connection | EntityManager,
        task: TestTask,
        {
            requireQualifiedProcessing = false,
            result = commonInitResult,
            basicInfo = commitInitBasicInfo,
            updatedAt = new Date()
        }: {
            requireQualifiedProcessing?: boolean;
            result?: ErpRecognitionResult;
            basicInfo?: DocumentsRecognizedBasicInfo;
            updatedAt?: Date;
        }
    ) {
        const erpRecognitionResult = await connection.getRepository(ErpRecognitionResults).insert({
            result,
            taskId: task.taskId,
            updatedAt,
            documentsRecognizedBasicInfo: basicInfo,
            requireQualifiedProcessing
        });

        await updateLastHistoryRowDate(connection, task, updatedAt);

        return erpRecognitionResult.identifiers[0].id;
    }

    beforeEach(async () => {
        await executeInTransaction({}, async (connection) => {
            const store = await connection
                .getRepository(Stores)
                .insert({id: 5001, name: 'Test store', externalId: 'qwerty_id'});

            storeId = store.identifiers[0].id;
            usersIds = [];

            usersIds.push(
                (await connection.getRepository(Users).insert({id: 5001, login: 'user-0'})).identifiers[0].id
            );
            usersIds.push(
                (await connection.getRepository(Users).insert({id: 5002, login: 'user-1'})).identifiers[0].id
            );
            usersIds.push(
                (await connection.getRepository(Users).insert({id: 5003, login: 'user-2'})).identifiers[0].id
            );
            usersIds.push(
                (await connection.getRepository(Users).insert({id: 5004, login: 'user-3'})).identifiers[0].id
            );
            usersIds.push(
                (await connection.getRepository(Users).insert({id: 5005, login: 'user-4'})).identifiers[0].id
            );
            usersIds.push(
                (await connection.getRepository(Users).insert({id: 5006, login: 'user-5'})).identifiers[0].id
            );

            for (const userId of usersIds) {
                await connection.getRepository(UsersStores).insert({userId, storeId});
            }
        });
    });

    it('returning supplies', async () => {
        await executeInTransactionWithAuthor({authorId: usersIds[0]}, async (connection) => {
            const task1 = await addTask(connection, {recognitionRequestStatus: RecognitionRequestStatus.NEW});

            await updateErpRecognitonResult(connection, task1, commonInitResult);
            await deleteErpRecognitionResult(connection, task1);

            const task2 = await addTask(connection, {recognitionRequestStatus: RecognitionRequestStatus.VERIFIED});

            await updateErpRecognitonResult(connection, task2, commonInitResult);
            await deleteErpRecognitionResult(connection, task2);
            await addErpRecognitionResult(connection, task2, {});

            const task3 = await addTask(connection, {recognitionRequestStatus: RecognitionRequestStatus.NEW});

            await updateErpRecognitonResult(connection, task3, commonInitResult);

            const task4 = await addTask(connection, {recognitionRequestStatus: RecognitionRequestStatus.VERIFIED});
            await updateErpRecognitonResult(connection, task4, commonInitResult);

            const report = await createReport(query);

            expect(report[0].totalVerifiedTask).toBe(2);
            expect(report[0].totalVerifiedTaskAndRequiredQualifiedProcessing).toBe(0);
            expect(report[0].totalReturnedTasks).toBe(2);
            expect(report[0].editedCellsAmount).toBe(0);
        });
    });

    it('verification tasks and/or qualified operator calling', async () => {
        await executeInTransactionWithAuthor({authorId: usersIds[0]}, async (connection) => {
            await addTask(connection, {
                recognitionRequestStatus: RecognitionRequestStatus.VERIFIED
            });
            await addTask(connection, {
                recognitionRequestStatus: RecognitionRequestStatus.VERIFIED,
                requireQualifiedProcessing: true
            });

            await addTask(connection, {
                recognitionRequestStatus: RecognitionRequestStatus.NEW
            });
            await addTask(connection, {
                recognitionRequestStatus: RecognitionRequestStatus.PENDING
            });
            await addTask(connection, {
                recognitionRequestStatus: RecognitionRequestStatus.IN_PROGRESS
            });
            await addTask(connection, {
                recognitionRequestStatus: RecognitionRequestStatus.SKIPPED
            });
            await addTask(connection, {
                recognitionRequestStatus: RecognitionRequestStatus.FAILED
            });
            await addTask(connection, {
                recognitionRequestStatus: RecognitionRequestStatus.FINISHED
            });

            await addTask(connection, {
                recognitionRequestStatus: RecognitionRequestStatus.NEW,
                requireQualifiedProcessing: true
            });
            await addTask(connection, {
                recognitionRequestStatus: RecognitionRequestStatus.PENDING,
                requireQualifiedProcessing: true
            });
            await addTask(connection, {
                recognitionRequestStatus: RecognitionRequestStatus.IN_PROGRESS,
                requireQualifiedProcessing: true
            });
            await addTask(connection, {
                recognitionRequestStatus: RecognitionRequestStatus.SKIPPED,
                requireQualifiedProcessing: true
            });
            await addTask(connection, {
                recognitionRequestStatus: RecognitionRequestStatus.FAILED,
                requireQualifiedProcessing: true
            });
            await addTask(connection, {
                recognitionRequestStatus: RecognitionRequestStatus.FINISHED,
                requireQualifiedProcessing: true
            });

            const report = await createReport(query);

            expect(report[0].totalVerifiedTask).toBe(2);
            expect(report[0].totalVerifiedTaskAndRequiredQualifiedProcessing).toBe(1);
            expect(report[0].totalReturnedTasks).toBe(0);
            expect(report[0].editedCellsAmount).toBe(0);
        });
    });

    it('rows confirmation (1 row + 1 row with 4 edited cells)', async () => {
        await executeInTransactionWithAuthor({authorId: usersIds[0]}, async (connection) => {
            const task = await addTask(connection, {});
            const confirmedRowAndRowWithCells: ErpRecognitionResult = JSON.parse(
                fs.readFileSync(
                    serviceResolve(
                        './src/server/routes/api/v1/users/samples/rows-confirmation/row-and-row-with-cells.json'
                    ),
                    'utf8'
                )
            );

            await updateErpRecognitonResult(connection, task, confirmedRowAndRowWithCells);

            const report = await createReport(query);

            expect(report[0].editedCellsAmount).toBe(6);

            expect(report[0].totalReturnedTasks).toBe(0);
            expect(report[0].totalVerifiedTask).toBe(1);
            expect(report[0].totalVerifiedTaskAndRequiredQualifiedProcessing).toBe(0);
        });
    });

    it('rows removals', async () => {
        await executeInTransactionWithAuthor({authorId: usersIds[0]}, async (connection) => {
            const task = await addTask(connection, {});
            const threeRowsRemovedAndFourCellsEdited: ErpRecognitionResult = JSON.parse(
                fs.readFileSync(
                    serviceResolve(
                        './src/server/routes/api/v1/users/samples/rows-removal/two-rows-removed-and-4-cells-edited.json'
                    ),
                    'utf8'
                )
            );

            await updateErpRecognitonResult(connection, task, threeRowsRemovedAndFourCellsEdited);

            const report = await createReport(query);

            expect(report[0].editedCellsAmount).toBe(6);

            expect(report[0].totalReturnedTasks).toBe(0);
            expect(report[0].totalVerifiedTask).toBe(1);
            expect(report[0].totalVerifiedTaskAndRequiredQualifiedProcessing).toBe(0);
        });
    });

    it('rows adding', async () => {
        await executeInTransactionWithAuthor({authorId: usersIds[0]}, async (connection) => {
            const task = await addTask(connection, {});
            const rowAdded: ErpRecognitionResult = JSON.parse(
                fs.readFileSync(
                    serviceResolve('./src/server/routes/api/v1/users/samples/rows-adding/row-added.json'),
                    'utf8'
                )
            );

            await updateErpRecognitonResult(connection, task, rowAdded);

            const rowAddedAndFourCellsAndIndexFilled: ErpRecognitionResult = JSON.parse(
                fs.readFileSync(
                    serviceResolve(
                        './src/server/routes/api/v1/users/samples/rows-adding/row-added-and-four-fields-and-index-filled.json'
                    ),
                    'utf8'
                )
            );

            await updateErpRecognitonResult(connection, task, rowAddedAndFourCellsAndIndexFilled);

            const report = await createReport(query);

            expect(report[0].editedCellsAmount).toBe(7);

            expect(report[0].totalReturnedTasks).toBe(0);
            expect(report[0].totalVerifiedTask).toBe(1);
            expect(report[0].totalVerifiedTaskAndRequiredQualifiedProcessing).toBe(0);
        });
    });

    it('simple cells editing and confirmations (including row auto-fill)', async () => {
        await executeInTransactionWithAuthor({authorId: usersIds[0]}, async (connection) => {
            const task = await addTask(connection, {});
            const cellConfirmedAndEditedAndRowAutoFilled: ErpRecognitionResult = JSON.parse(
                fs.readFileSync(
                    serviceResolve(
                        './src/server/routes/api/v1/users/samples/cells-editing/cells-confirmed-and-edited-and-row-auto-filled.json'
                    ),
                    'utf8'
                )
            );

            await updateErpRecognitonResult(connection, task, cellConfirmedAndEditedAndRowAutoFilled);

            const report = await createReport(query);

            expect(report[0].editedCellsAmount).toBe(10);

            expect(report[0].totalReturnedTasks).toBe(0);
            expect(report[0].totalVerifiedTask).toBe(1);
            expect(report[0].totalVerifiedTaskAndRequiredQualifiedProcessing).toBe(0);
        });
    });

    it('indexes editing', async () => {
        await executeInTransactionWithAuthor({authorId: usersIds[0]}, async (connection) => {
            const task = await addTask(connection, {});
            const indexesEditedManuallyAndAutoFilled: ErpRecognitionResult = JSON.parse(
                fs.readFileSync(
                    serviceResolve(
                        './src/server/routes/api/v1/users/samples/indexes-editing/indexes-edited-manually-and-auto-fill.json'
                    ),
                    'utf8'
                )
            );

            await updateErpRecognitonResult(connection, task, indexesEditedManuallyAndAutoFilled);

            const report = await createReport(query);

            expect(report[0].editedCellsAmount).toBe(1);

            expect(report[0].totalReturnedTasks).toBe(0);
            expect(report[0].totalVerifiedTask).toBe(1);
            expect(report[0].totalVerifiedTaskAndRequiredQualifiedProcessing).toBe(0);
        });
    });

    it('multi-user editing', async () => {
        let task: TestTask;
        await executeInTransactionWithAuthor({authorId: usersIds[0]}, async (connection) => {
            const multiUserInitResult: ErpRecognitionResult = JSON.parse(
                fs.readFileSync(
                    serviceResolve('./src/server/routes/api/v1/users/samples/init-states/multi-user.json'),
                    'utf8'
                )
            );

            task = await addTask(connection, {result: multiUserInitResult});

            const changesByUser0: ErpRecognitionResult = JSON.parse(
                fs.readFileSync(
                    serviceResolve(
                        './src/server/routes/api/v1/users/samples/multi-user-changes/changes-by-user-0.json'
                    ),
                    'utf8'
                )
            );

            await updateErpRecognitonResult(connection, task, changesByUser0);
        });

        await executeInTransactionWithAuthor({authorId: usersIds[1]}, async (connection) => {
            const changesByUser1: ErpRecognitionResult = JSON.parse(
                fs.readFileSync(
                    serviceResolve(
                        './src/server/routes/api/v1/users/samples/multi-user-changes/changes-by-user-1.json'
                    ),
                    'utf8'
                )
            );

            await updateErpRecognitonResult(connection, task, changesByUser1);
        });

        await executeInTransactionWithAuthor({authorId: usersIds[2]}, async (connection) => {
            const changesByUser2: ErpRecognitionResult = JSON.parse(
                fs.readFileSync(
                    serviceResolve(
                        './src/server/routes/api/v1/users/samples/multi-user-changes/changes-by-user-2.json'
                    ),
                    'utf8'
                )
            );

            await updateErpRecognitonResult(connection, task, changesByUser2);
        });

        await executeInTransactionWithAuthor({authorId: usersIds[3]}, async (connection) => {
            const changesByUser3: ErpRecognitionResult = JSON.parse(
                fs.readFileSync(
                    serviceResolve(
                        './src/server/routes/api/v1/users/samples/multi-user-changes/changes-by-user-3.json'
                    ),
                    'utf8'
                )
            );

            await updateErpRecognitonResult(connection, task, changesByUser3);
        });

        await executeInTransactionWithAuthor({authorId: usersIds[4]}, async (connection) => {
            const changesByUser4: ErpRecognitionResult = JSON.parse(
                fs.readFileSync(
                    serviceResolve(
                        './src/server/routes/api/v1/users/samples/multi-user-changes/changes-by-user-4.json'
                    ),
                    'utf8'
                )
            );

            await updateErpRecognitonResult(connection, task, changesByUser4);
        });

        await executeInTransactionWithAuthor({authorId: usersIds[5]}, async (connection) => {
            const changesByUser5: ErpRecognitionResult = JSON.parse(
                fs.readFileSync(
                    serviceResolve(
                        './src/server/routes/api/v1/users/samples/multi-user-changes/changes-by-user-5.json'
                    ),
                    'utf8'
                )
            );

            await updateErpRecognitonResult(connection, task, changesByUser5);
        });

        const report = await createReport(query);

        expect(report).toHaveLength(1);
        expect(report[0].login).toBe('user-5');
        expect(report[0].editedCellsAmount).toBe(20);

        expect(report[0].totalReturnedTasks).toBe(0);
        expect(report[0].totalVerifiedTask).toBe(1);
        expect(report[0].totalVerifiedTaskAndRequiredQualifiedProcessing).toBe(0);
    });

    it('rows filled from plan', async () => {
        await executeInTransactionWithAuthor({authorId: usersIds[0]}, async (connection) => {
            const docAutoFillResult: ErpRecognitionResult = JSON.parse(
                fs.readFileSync(
                    serviceResolve('./src/server/routes/api/v1/users/samples/init-states/fill-row-from-plan.json'),
                    'utf8'
                )
            );

            const task = await addTask(connection, {result: docAutoFillResult});
            const docCellsAutoFilles: ErpRecognitionResult = JSON.parse(
                fs.readFileSync(
                    serviceResolve('./src/server/routes/api/v1/users/samples/auto-filling/row-filled-from-plan.json'),
                    'utf8'
                )
            );

            await updateErpRecognitonResult(connection, task, docCellsAutoFilles);

            const report = await createReport(query);

            expect(report[0].editedCellsAmount).toBe(7);

            expect(report[0].totalReturnedTasks).toBe(0);
            expect(report[0].totalVerifiedTask).toBe(1);
            expect(report[0].totalVerifiedTaskAndRequiredQualifiedProcessing).toBe(0);
        });
    });

    it('table filled from plan', async () => {
        await executeInTransactionWithAuthor({authorId: usersIds[0]}, async (connection) => {
            const docAutoFillResult: ErpRecognitionResult = JSON.parse(
                fs.readFileSync(
                    serviceResolve('./src/server/routes/api/v1/users/samples/init-states/fill-row-from-plan.json'),
                    'utf8'
                )
            );

            const task = await addTask(connection, {result: docAutoFillResult});
            const docCellsAutoFilles: ErpRecognitionResult = JSON.parse(
                fs.readFileSync(
                    serviceResolve('./src/server/routes/api/v1/users/samples/auto-filling/table-filled-from-plan.json'),
                    'utf8'
                )
            );

            await updateErpRecognitonResult(connection, task, docCellsAutoFilles);

            const report = await createReport(query);

            expect(report[0].editedCellsAmount).toBe(4);

            expect(report[0].totalReturnedTasks).toBe(0);
            expect(report[0].totalVerifiedTask).toBe(1);
            expect(report[0].totalVerifiedTaskAndRequiredQualifiedProcessing).toBe(0);
        });
    });

    it('auto-fill doc', async () => {
        await executeInTransactionWithAuthor({authorId: usersIds[0]}, async (connection) => {
            const docAutoFillResult: ErpRecognitionResult = JSON.parse(
                fs.readFileSync(
                    serviceResolve('./src/server/routes/api/v1/users/samples/init-states/doc-auto-fill.json'),
                    'utf8'
                )
            );

            const task = await addTask(connection, {result: docAutoFillResult});
            const docCellsAutoFilles: ErpRecognitionResult = JSON.parse(
                fs.readFileSync(
                    serviceResolve('./src/server/routes/api/v1/users/samples/doc-auto-filling/auto-filled.json'),
                    'utf8'
                )
            );

            await updateErpRecognitonResult(connection, task, docCellsAutoFilles);

            const report = await createReport(query);

            expect(report[0].editedCellsAmount).toBe(18);

            expect(report[0].totalReturnedTasks).toBe(0);
            expect(report[0].totalVerifiedTask).toBe(1);
            expect(report[0].totalVerifiedTaskAndRequiredQualifiedProcessing).toBe(0);
        });
    });

    it('approve basic info', async () => {
        await executeInTransactionWithAuthor({authorId: usersIds[0]}, async (connection) => {
            const task = await addTask(connection, {});
            const dateApproved: DocumentsRecognizedBasicInfo = JSON.parse(
                fs.readFileSync(
                    serviceResolve(
                        './src/server/routes/api/v1/users/samples/basic-info-approvement/date-approved.json'
                    ),
                    'utf8'
                )
            );

            await addBasicInfoToHistory(connection, task, dateApproved);

            const report = await createReport(query);

            expect(report[0].editedCellsAmount).toBe(1);

            expect(report[0].totalReturnedTasks).toBe(0);
            expect(report[0].totalVerifiedTask).toBe(1);
            expect(report[0].totalVerifiedTaskAndRequiredQualifiedProcessing).toBe(0);

            const innApproved: DocumentsRecognizedBasicInfo = JSON.parse(
                fs.readFileSync(
                    serviceResolve('./src/server/routes/api/v1/users/samples/basic-info-approvement/inn-approved.json'),
                    'utf8'
                )
            );

            await addBasicInfoToHistory(connection, task, innApproved);

            const report2 = await createReport(query);

            expect(report2[0].editedCellsAmount).toBe(2);

            expect(report2[0].totalReturnedTasks).toBe(0);
            expect(report2[0].totalVerifiedTask).toBe(1);
            expect(report2[0].totalVerifiedTaskAndRequiredQualifiedProcessing).toBe(0);
        });
    });

    it.skip('take only tasks from date range', async () => {
        await executeInTransactionWithAuthor({authorId: usersIds[0]}, async (connection) => {
            const firstDate = moment('2022-06-01').utc().toDate();
            const lastDate = moment('2022-06-03').utc().toDate();

            // 2 из 4 тасок попадают в нужный диапазон дат
            await addTask(connection, {
                recognitionRequestStatus: RecognitionRequestStatus.VERIFIED,
                updatedAt: moment('2022-05-31').toDate()
            });

            await addTask(connection, {
                recognitionRequestStatus: RecognitionRequestStatus.VERIFIED,
                updatedAt: moment('2022-06-01').toDate()
            });

            await addTask(connection, {
                recognitionRequestStatus: RecognitionRequestStatus.VERIFIED,
                updatedAt: moment('2022-06-03').toDate()
            });

            await addTask(connection, {
                recognitionRequestStatus: RecognitionRequestStatus.VERIFIED,
                updatedAt: moment('2022-06-04').toDate()
            });

            // то же самое для возвращённых тасок
            const task1 = await addTask(connection, {
                recognitionRequestStatus: RecognitionRequestStatus.NEW,
                updatedAt: moment('2022-05-31').toDate()
            });

            await updateErpRecognitonResult(connection, task1, commonInitResult, moment('2022-05-31').toDate());
            await deleteErpRecognitionResult(connection, task1, moment('2022-05-31').toDate());

            const task2 = await addTask(connection, {
                recognitionRequestStatus: RecognitionRequestStatus.NEW,
                updatedAt: moment('2022-06-01').toDate()
            });

            await updateErpRecognitonResult(connection, task2, commonInitResult, moment('2022-06-01').toDate());
            await deleteErpRecognitionResult(connection, task2, moment('2022-06-01').toDate());

            const task3 = await addTask(connection, {
                recognitionRequestStatus: RecognitionRequestStatus.NEW,
                updatedAt: moment('2022-06-03').toDate()
            });

            await updateErpRecognitonResult(connection, task3, commonInitResult, moment('2022-06-03').toDate());
            await deleteErpRecognitionResult(connection, task3, moment('2022-06-03').toDate());

            const task4 = await addTask(connection, {
                recognitionRequestStatus: RecognitionRequestStatus.NEW,
                updatedAt: moment('2022-06-04').toDate()
            });

            await updateErpRecognitonResult(connection, task4, commonInitResult, moment('2022-06-04').toDate());
            await deleteErpRecognitionResult(connection, task4, moment('2022-06-04').toDate());

            // распознали до границ диапазона дат, подтвердили в границах
            const task5 = await addTask(connection, {
                recognitionRequestStatus: RecognitionRequestStatus.VERIFIED,
                updatedAt: moment('2022-05-31').toDate()
            });

            const rowAdded: ErpRecognitionResult = JSON.parse(
                fs.readFileSync(
                    serviceResolve('./src/server/routes/api/v1/users/samples/rows-adding/row-added.json'),
                    'utf8'
                )
            );

            await updateErpRecognitonResult(connection, task5, rowAdded, moment('2022-06-02').toDate());

            // распознали в границах диапазона дат, подтвердили после
            const task6 = await addTask(connection, {
                recognitionRequestStatus: RecognitionRequestStatus.VERIFIED,
                updatedAt: moment('2022-06-02 12:00').utcOffset(0, true).toDate()
            });

            // TODO: почему-то граница дат проходит по 3 AM
            await updateErpRecognitonResult(
                connection,
                task6,
                rowAdded,
                moment('2022-06-04 00:01').utcOffset(0, true).toDate()
            );

            const report = await createReport({firstDate, lastDate});

            expect(report[0].totalVerifiedTask).toBe(3);
            expect(report[0].totalReturnedTasks).toBe(2);
        });
    });

    it("don't count different format of the same (4 and 4.00)", async () => {
        await executeInTransactionWithAuthor({authorId: usersIds[0]}, async (connection) => {
            const task = await addTask(connection, {});
            const reformatedCells: ErpRecognitionResult = JSON.parse(
                fs.readFileSync(
                    serviceResolve('./src/server/routes/api/v1/users/samples/reformated-cells/reformated-cells.json'),
                    'utf8'
                )
            );

            await updateErpRecognitonResult(connection, task, reformatedCells);

            const report = await createReport(query);

            expect(report[0].editedCellsAmount).toBe(1);

            expect(report[0].totalReturnedTasks).toBe(0);
            expect(report[0].totalVerifiedTask).toBe(1);
            expect(report[0].totalVerifiedTaskAndRequiredQualifiedProcessing).toBe(0);
        });
    });
});
