import {In} from 'typeorm';

import {Documents} from '@/src/entities/documents/entity';
import {RecognitionResults} from '@/src/entities/recognition-results/entity';
import {Tasks} from '@/src/entities/tasks/entity';
import {generateStores, insertDocs, insertRecognitionResult, insertTasks} from '@/src/test/test-factory';
import {ensureConnection} from 'service/db';
import {pMap} from 'service/helper/p-map';

describe('should cascade delete task', () => {
    it('test', async () => {
        const stores = await generateStores(1, (index) => ({id: () => index + 1}));
        const tasks = await insertTasks(stores.raw[0].id);
        const documents = (await pMap(tasks, (task) => insertDocs(task.id))).flat();
        const recognitionResults = (await pMap(documents, (document) => insertRecognitionResult(document.id))).flat();

        const documentsIds = documents.map((document) => document.id);
        const recognitionResultsIds = recognitionResults.map((result) => result.id);

        expect(recognitionResultsIds.length).toBeGreaterThan(0);

        const connection = await ensureConnection();
        await connection.getRepository(Tasks).delete({id: In(tasks.map((task) => task.id))});

        const recognitionResultsRemainIds = await connection
            .getRepository(RecognitionResults)
            .find({id: In(recognitionResultsIds)});
        expect(recognitionResultsRemainIds).toHaveLength(0);

        const documentsRemainIds = await connection.getRepository(Documents).find({id: In(documentsIds)});
        expect(documentsRemainIds).toHaveLength(0);
    });
});
