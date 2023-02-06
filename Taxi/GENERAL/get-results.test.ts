import {uuid} from 'casual';
import {groupBy} from 'lodash';
import {convertStringItemToValueItem, convertStringSumsToValueSums} from 'tests/unit/test-factory';
import {v4 as uuidv4} from 'uuid';

import {Documents} from '@/src/entities/documents/entity';
import {serializeDocument} from '@/src/entities/recognition-results/api/serialize-result';
import {RecognitionResults} from '@/src/entities/recognition-results/entity';
import {Tasks} from '@/src/entities/tasks/entity';
import {Users} from '@/src/entities/users/entity';
import {mockErpSupplies} from '@/src/test/mocks/mock-data';
import {addTask, generateStores} from '@/src/test/test-factory';
import {finalizeTaskIfNeeded} from 'server/recognition';
import type {Document} from 'server/recognition/types/types';
import {formatVat} from 'server/recognition/utils';
import {getResults} from 'server/routes/erp/v1/erp/get-results';
import {ensureConnection, executeInTransactionWithAuthor} from 'service/db';
import {pMap} from 'service/helper/p-map';
import {DocumentType, RecognitionRequestStatus} from 'types/documents';
import type {ErpSupply} from 'types/erp';
import {RecognitionResultStatus} from 'types/recognition-results';
import {RecognitionRequestStatus as Status} from 'types/task';

describe('get recognition results handler', () => {
    let tasks: Tasks[] = [];

    beforeEach(async () => {
        const erpSupplies: ErpSupply[] = mockErpSupplies;

        const connection = await ensureConnection();

        const stores = await generateStores(1, () => ({}));
        const addedTasks = await Promise.all(erpSupplies.map((supply) => addTask(supply.id, stores.raw[0].id, supply)));
        tasks = addedTasks.map((task) => task.raw[0]) as Tasks[];

        const documents = (
            await pMap(tasks, async (task) => {
                const documents = await Promise.all([
                    connection.getRepository(Documents).insert([
                        {
                            taskId: task.id,
                            originalDocumentImage: 'stubImageKey',
                            status: RecognitionRequestStatus.FINISHED,
                            originalName: 'file.pdf',
                            uid: uuidv4(),
                            type: DocumentType.PackingList
                        }
                    ]),
                    connection.getRepository(Documents).insert([
                        {
                            taskId: task.id,
                            originalDocumentImage: 'stubImageKey',
                            status: RecognitionRequestStatus.FINISHED,
                            originalName: 'file.pdf',
                            uid: uuidv4(),
                            type: DocumentType.PackingList
                        }
                    ])
                ]);

                return documents;
            })
        )
            .flat()
            .map((document) => document.raw[0]) as Documents[];

        const recognitionResultsJson: Document[] = [
            {
                type: DocumentType.UniversalTransferDocument,
                total: convertStringSumsToValueSums({sumWithVat: '234', sum: '123'}),
                number: {confidence: {value: 1}, value: 'invoiceNumber'},
                pages: [
                    {
                        pageTotal: convertStringSumsToValueSums({sumWithVat: '234', sum: '123'}),
                        items: [
                            {sum: '66.99', price: '88.99', title: 'сырок Б. Ю. Александров'},
                            {sum: '111', price: '55.55', title: 'кашка'}
                        ].map(convertStringItemToValueItem),
                        rawTable: []
                    }
                ]
            },
            {
                type: DocumentType.UniversalTransferDocument,
                total: convertStringSumsToValueSums({sumWithVat: '234', sum: '123'}),
                number: {confidence: {value: 1}, value: 'consignmentNoteNumber'},
                pages: [
                    {
                        pageTotal: convertStringSumsToValueSums({sumWithVat: '234', sum: '123'}),
                        items: [
                            {sum: '47.99', price: '48', title: 'кефирные грибки'},
                            {sum: '111', price: '55.55', title: 'тапочки'}
                        ].map(convertStringItemToValueItem),
                        rawTable: []
                    }
                ]
            },
            {
                type: DocumentType.PackingList,
                total: convertStringSumsToValueSums({sumWithVat: '234', sum: '123'}),
                number: {confidence: {value: 1}, value: 'packinglistNumber'},
                pages: [
                    {
                        pageTotal: convertStringSumsToValueSums({sumWithVat: '234', sum: '123'}),
                        items: [{sum: '600', price: '200', title: 'пельмени'}].map(convertStringItemToValueItem),
                        rawTable: []
                    }
                ]
            },
            {
                type: DocumentType.UniversalTransferDocument,
                total: convertStringSumsToValueSums({sumWithVat: '234', sum: '123'}),
                number: {confidence: {value: 1}, value: 'universalTransferDocumentNumber'},
                pages: [
                    {
                        pageTotal: convertStringSumsToValueSums({sumWithVat: '234', sum: '123'}),
                        items: [{sum: '600', price: '200', title: 'вареники'}].map(convertStringItemToValueItem),
                        rawTable: []
                    }
                ]
            }
        ];

        await pMap(documents, (document, index) => {
            return connection.getRepository(RecognitionResults).insert([
                {
                    documentId: document.id,
                    chunks: [],
                    status: RecognitionResultStatus.SUCCESS,
                    result: serializeDocument(recognitionResultsJson[index])
                }
            ]);
        });

        const documentsToUpdate = Object.values(
            groupBy(await connection.getRepository(Documents).find(), (d) => d.taskId)
        ).map((d) => d[0]);

        const user = (await connection.getRepository(Users).insert({login: uuid})).generatedMaps[0];

        await executeInTransactionWithAuthor({authorId: user.id}, async (manager) => {
            await pMap(documentsToUpdate, (document) => finalizeTaskIfNeeded(document.taskId, user.id, {manager}));

            await pMap(tasks, async (task) => {
                await manager.getRepository(Tasks).update({id: task.id}, {recognition_request_status: Status.VERIFIED});
            });
        });
    });

    it('should return correct cursors', async () => {
        const firstCursor = (await getResults(0, 1)).cursor;
        const secondCursor = (await getResults(firstCursor, 1)).cursor;

        const alsoSecondCursor = (await getResults(secondCursor, 0)).cursor;
        expect(alsoSecondCursor).toStrictEqual(secondCursor);

        const afterLastCursor = (await getResults(0, 100)).cursor;
        const alsoAfterLastCursor = (await getResults(afterLastCursor, 1)).cursor;
        expect(alsoAfterLastCursor).toStrictEqual(afterLastCursor);
        expect(alsoAfterLastCursor).toStrictEqual(alsoSecondCursor);
    });

    it('should return correct number of documents', async () => {
        let results = await getResults(0, 0);
        expect(results.data).toHaveLength(0);

        results = await getResults(0, 100);
        expect(results.data).toHaveLength(2);
        expect(results.data[0].recognized_data[0].documents).toHaveLength(2);
        expect(results.data[0].recognized_data[0].documents).toHaveLength(2);

        results = await getResults(0, 1);
        expect(results.data).toHaveLength(1);
        expect(results.data[0].recognized_data[0].documents).toHaveLength(2);
    });

    it('should return correct documents', async () => {
        const firstTask = (await getResults(0, 1)).data[0];
        expect(firstTask).toBeDefined();
        expect(firstTask.erp_id).toBe('erpId_1');

        expect(firstTask.recognized_data).toBeDefined();
        expect(firstTask.recognized_data).toHaveLength(1);

        const recognitionResult = firstTask.recognized_data[0];

        expect(Number(recognitionResult.total_sum)).toBeCloseTo(246);
        expect(Number(recognitionResult.total_sum_with_vat)).toBeCloseTo(468);

        expect(recognitionResult.items).toHaveLength(4);
        expect(recognitionResult.items).toIncludeAllPartialMembers([
            {title: 'сырок Б. Ю. Александров'},
            {title: 'кашка'},
            {title: 'кефирные грибки'},
            {title: 'тапочки'}
        ]);
    });

    it('should build falcon original url', async () => {
        const firstTask = (await getResults(0, 1)).data[0];
        expect(firstTask).toBeDefined();

        expect(firstTask.falcon_url).toEqual(`https://lavka-falcon.tst.lavka.yandex-team.ru/supplies/${tasks[0].id}`);
    });
});

describe('format result json', () => {
    it('should format vat', () => {
        expect(formatVat('123%')).toBe('123');
        expect(formatVat('1 2')).toBe('12');
        expect(formatVat('20')).toBe('20');
        expect(formatVat('#########')).toBe('');
        expect(formatVat('ндс 20.0 %')).toBe('20.0');
    });
});
