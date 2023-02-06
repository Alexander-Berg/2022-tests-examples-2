import {uuid} from 'casual';
import {In} from 'typeorm';

import {Documents} from '@/src/entities/documents/entity';
import {ErpRecognitionResults} from '@/src/entities/erp-recognition-results/entity';
import {RecognitionResults} from '@/src/entities/recognition-results/entity';
import {Users} from '@/src/entities/users/entity';
import {
    generateStores,
    insertDocs,
    insertErpRecognitionResult,
    insertRecognitionResult,
    insertTasks
} from '@/src/test/test-factory';
import {deleteSupplyRecognitionFromDB} from 'server/routes/api/v1/supplies/delete-supply-recognition';
import {ensureConnection, executeInTransactionWithAuthor} from 'service/db';
import {pMap} from 'service/helper/p-map';

describe('should delete task recognition results', () => {
    it('test', async () => {
        const stores = await generateStores(1, () => ({}));
        const tasks = (await Promise.all([1, 2, 3, 4, 5].map(() => insertTasks(stores.raw[0].id)))).flat();

        const documents = (await pMap(tasks, (task) => insertDocs(task.id))).flat();
        const recognitionResults = (await pMap(documents, (document) => insertRecognitionResult(document.id))).flat();

        const taskId = tasks[5].id;

        const documentsIds = documents.filter((document) => document.taskId === taskId).map((document) => document.id);
        const recognitionResultsIds = recognitionResults
            .filter((recognitionResult) =>
                documentsIds.some((documentId) => recognitionResult.documentId === documentId)
            )
            .map((result) => result.id);

        expect(documentsIds.length).toBeGreaterThan(0);
        expect(recognitionResultsIds.length).toBeGreaterThan(0);

        const connection = await ensureConnection();
        const user = (await connection.getRepository(Users).insert({login: uuid})).generatedMaps[0];

        const erpRecognitionResults = (
            await pMap(tasks, (task) => insertErpRecognitionResult(task.id, user.id))
        ).flat();

        const erpRecognitionResultsIds = erpRecognitionResults
            .filter((erpRecognitionResult) => erpRecognitionResult.taskId === taskId)
            .map((result) => result.id);

        expect(erpRecognitionResultsIds.length).toBeGreaterThan(0);

        await executeInTransactionWithAuthor({authorId: user.id}, async (manager) => {
            await deleteSupplyRecognitionFromDB(manager, taskId);
        });

        const recognitionResultsRemainIds = await connection
            .getRepository(RecognitionResults)
            .find({id: In(recognitionResultsIds)});
        expect(recognitionResultsRemainIds).toHaveLength(0);

        const erpRecognitionResultsRemainIds = await connection
            .getRepository(ErpRecognitionResults)
            .find({id: In(erpRecognitionResultsIds)});
        expect(erpRecognitionResultsRemainIds).toHaveLength(0);

        const documentsRemainIds = await connection.getRepository(Documents).find({id: In(documentsIds)});
        expect(documentsRemainIds).toHaveLength(documentsIds.length);
    });
});
