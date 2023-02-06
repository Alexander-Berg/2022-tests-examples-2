import {integer} from 'casual';
import {addYears} from 'date-fns';
import {omit} from 'lodash';
import type {EntityTarget} from 'typeorm';
import {v4 as uuidv4} from 'uuid';

import {Documents} from '@/src/entities/documents/entity';
import {ErpRecognitionResults} from '@/src/entities/erp-recognition-results/entity';
import {RecognitionResults} from '@/src/entities/recognition-results/entity';
import {Stores} from '@/src/entities/stores/entity';
import {upsertTasks} from '@/src/entities/tasks/api/upsert-tasks';
import {Tasks} from '@/src/entities/tasks/entity';
import {Users} from '@/src/entities/users/entity';
import {UsersTasks} from '@/src/entities/users-tasks/entity';
import {mockErpRecognitionResults, mockErpSupplies, mockRecognitionResults} from '@/src/test/mocks/mock-data';
import {ensureConnection, executeInTransactionWithAuthor} from 'service/db';
import {startOfDay} from 'service/utils/date-helper';
import {
    CorrectDocumentType,
    RecognitionRequestStatus as DocumentStatus,
    RecognitionRequestStatus
} from 'types/documents';
import type {StoredErpSupply} from 'types/erp';
import {RecognitionResultStatus} from 'types/recognition-results';
import {RecognitionRequestStatus as Status} from 'types/task';

export async function getDocumentByS3Key(s3Key: string) {
    const connection = await ensureConnection();

    return connection.getRepository(Documents).findOne({originalDocumentImage: s3Key});
}

export async function addTask(externalId: string, storeId: number, data: {}) {
    const connection = await ensureConnection();

    return connection
        .getRepository(Tasks)
        .insert([{externalId, storeId, data, date: new Date(), recognition_request_status: Status.VERIFIED}]);
}

export async function addDocument() {
    const connection = await ensureConnection();

    const stores = await generateStores(1, () => ({}));
    const task = await addTask('externalId', stores.raw[0].id, {});

    return (
        await connection.getRepository(Documents).insert([
            {
                taskId: task.raw[0].id,
                originalDocumentImage: 'stubImageKey',
                status: RecognitionRequestStatus.NEW,
                originalName: 'file.pdf',
                uid: uuidv4(),
                type: CorrectDocumentType.Invoice
            }
        ])
    ).raw[0];
}

export async function getItemFromDBById<T extends Documents | RecognitionResults | Tasks>(
    repository: EntityTarget<T>,
    itemId: string
): Promise<T> {
    const connection = await ensureConnection();

    return await connection.getRepository(repository).findOneOrFail(itemId);
}

export async function insertTasks(storeId: number): Promise<Tasks[]> {
    const conn = await ensureConnection();
    const tasks = (
        await upsertTasks(
            mockErpSupplies.map((supply) => ({
                externalId: uuidv4(),
                storeId,
                data: {...supply, date: new Date()},
                date: new Date()
            })),
            conn.manager
        )
    ).raw;

    return tasks;
}

export async function insertDocs(taskId: number): Promise<Documents[]> {
    const connection = await ensureConnection();

    const ids = (
        await connection.getRepository(Documents).insert([
            {
                taskId,
                originalDocumentImage: 'stubImageKey_1',
                status: DocumentStatus.NEW,
                originalName: 'file_1.pdf',
                uid: uuidv4(),
                type: CorrectDocumentType.Invoice
            },
            {
                taskId,
                originalDocumentImage: 'stubImageKey_2',
                status: DocumentStatus.NEW,
                originalName: 'file_2.pdf',
                uid: uuidv4(),
                type: CorrectDocumentType.PackingList
            }
        ])
    ).identifiers.map((id) => id.id);

    return await connection.getRepository(Documents).findByIds(ids);
}

export async function insertRecognitionResult(docId: number): Promise<RecognitionResults[]> {
    const connection = await ensureConnection();

    const ids = (
        await connection.getRepository(RecognitionResults).insert(
            mockRecognitionResults.map((recognitionResult) => ({
                documentId: docId,
                chunks: [],
                status: RecognitionResultStatus.SUCCESS,
                result: recognitionResult
            }))
        )
    ).identifiers.map((id) => id.id);

    return await connection.getRepository(RecognitionResults).findByIds(ids);
}

export async function insertErpRecognitionResult(taskId: number, authorId: number): Promise<ErpRecognitionResults> {
    return executeInTransactionWithAuthor({authorId}, async (manager) => {
        const ids = (
            await manager.getRepository(ErpRecognitionResults).insert({
                taskId,
                result: mockErpRecognitionResults[0]
            })
        ).identifiers.map((id) => id.id);

        return (await manager.getRepository(ErpRecognitionResults).findByIds(ids))[0];
    });
}

export async function generateStores(
    number: number,
    generator: (index: number) => {[key in keyof Partial<Stores>]: () => Stores[key]}
) {
    function externalIdDefaultGenerator() {
        return integer(0, Number.MAX_SAFE_INTEGER).toString();
    }

    function nameDefaultGenerator(index: number) {
        return index.toString();
    }

    const connection = await ensureConnection();

    const stores: Omit<Stores, 'storeUsers' | 'tasks' | 'id' | 'company' | 'updatedAt'>[] = new Array(number)
        .fill({})
        .map(
            (_, index): Omit<Stores, 'storeUsers' | 'tasks' | 'id' | 'company' | 'updatedAt'> => ({
                externalId: generator(index).externalId?.() ?? externalIdDefaultGenerator(),
                name: generator(index).name?.() ?? nameDefaultGenerator(index),
                companyId: 1
            })
        );

    return connection.getRepository(Stores).insert(stores);
}

export async function generateTasks(
    number: number,
    generator: (
        index: number
    ) => {[key in keyof (Partial<Omit<Tasks, 'data'>> & {storeId: Tasks['storeId']})]: () => Tasks[key]} & {
        data: {[key in keyof Partial<StoredErpSupply>]: () => StoredErpSupply[key]};
    }
) {
    function externalIdDefaultGenerator() {
        return integer(0, Number.MAX_SAFE_INTEGER).toString();
    }

    function dateDefaultGenerator() {
        return startOfDay(new Date());
    }

    function requestStatusDefaultGenerator(): Status {
        return Status.NEW;
    }

    function recognizedAtDefaultGenerator(): Date {
        return addYears(startOfDay(new Date()), -100);
    }

    function dataDefaultGenerators(
        index: number
    ): {[key in keyof Required<StoredErpSupply>]: () => Required<StoredErpSupply>[key]} {
        return {
            warehouse: () => ({
                id: index.toString(),
                name: index.toString(),
                wms_id: index.toString()
            }),
            date: () => new Date(),
            number: () => index.toString(),
            supplier: () => ({
                id: index.toString(),
                name: index.toString(),
                inn: index.toString(),
                kpp: index.toString()
            }),
            id: () => index.toString(),
            items: () => [],
            wms_orders: () => []
        };
    }

    const connection = await ensureConnection();

    const tasks: Omit<Tasks, 'documents' | 'store' | 'erpRecognitionResult' | 'id' | 'updatedAt'>[] = new Array(number)
        .fill({})
        .map(
            (_, index): Omit<Tasks, 'documents' | 'store' | 'erpRecognitionResult' | 'id' | 'updatedAt'> => ({
                externalId: generator(index).externalId?.() ?? externalIdDefaultGenerator(),
                date: generator(index).date?.() ?? dateDefaultGenerator(),
                storeId: generator(index).storeId(),
                recognition_request_status:
                    generator(index).recognition_request_status?.() ?? requestStatusDefaultGenerator(),
                recognized_at: generator(index).recognized_at?.() ?? recognizedAtDefaultGenerator(),
                data: ((): StoredErpSupply => {
                    const dataGenerators = {...dataDefaultGenerators(index), ...generator(index).data};

                    return {
                        warehouse: dataGenerators.warehouse(),
                        items: dataGenerators.items(),
                        id: dataGenerators.id(),
                        date: dataGenerators.date(),
                        supplier: dataGenerators.supplier(),
                        number: dataGenerators.number(),
                        wms_orders: dataGenerators.wms_orders()
                    };
                })()
            })
        );

    return connection.getRepository(Tasks).insert(tasks);
}

type GenerateUsersInputData = Pick<Users, 'login'> & Partial<Omit<Users, 'login'>>;

export async function generateUsers(usersData: GenerateUsersInputData[]) {
    const connection = await ensureConnection();

    return (
        await connection.getRepository(Users).insert(
            usersData.map((user) => {
                const now = new Date();

                return {
                    staffData: {},
                    hasPermission: false,
                    allStoresAccess: false,
                    staffDataUpdatedAt: now,
                    hasPermissionUpdatedAt: now,
                    ...user
                };
            })
        )
    ).generatedMaps.map((value) => Number((value as {id: string}).id));
}

type GenerateUsersTasksInputData = Omit<UsersTasks, 'user' | 'userId' | 'task' | 'taskId'> & {
    user: GenerateUsersInputData;
} & Partial<Pick<UsersTasks, 'taskId'>>;

export async function generateUsersTasks(usersTasksData: GenerateUsersTasksInputData[]) {
    const connection = await ensureConnection();

    const userIds = await generateUsers(usersTasksData.map(({user}) => user));

    const taskIds = usersTasksData.every((item) => typeof item.taskId === 'number')
        ? usersTasksData.map(({taskId}) => taskId)
        : (await connection.getRepository(Tasks).createQueryBuilder().take(usersTasksData.length).getMany()).map(
              ({id}) => id
          );

    await connection.getRepository(UsersTasks).insert(
        usersTasksData.map((data, index) => ({
            ...omit(data, 'user'),
            userId: userIds[index],
            taskId: taskIds[index]
        }))
    );
}
