import {changeDocumentStatus} from '@/src/entities/documents/api/change-document-status';
import {Documents} from '@/src/entities/documents/entity';
import {RecognitionResults} from '@/src/entities/recognition-results/entity';
import {Users} from '@/src/entities/users/entity';
import {addDocument, getItemFromDBById} from '@/src/test/test-factory';
import {saveRecognitionResultToDataBase} from 'server/recognition/save-recognition-result-to-data-base';
import {ensureConnection} from 'service/db';
import {DocumentType, RecognitionRequestStatus} from 'types/documents';
import {RecognitionResultStatus} from 'types/recognition-results';

describe('save recognized json to database', () => {
    it('should save recognized json to database', async () => {
        const insertedDocument = await addDocument();
        const connection = await ensureConnection();

        const user = (await connection.getRepository(Users).insert({login: 'stub'})).generatedMaps[0];

        const savedRecognitionResults = await saveRecognitionResultToDataBase(
            {
                documentJson: {type: DocumentType.Invoice, pages: []},
                document: {id: insertedDocument.id},
                status: RecognitionResultStatus.SUCCESS,
                authorId: user.id,
                taskId: 1,
                s3Chunks: ['stubS3Chunk_1', 'stubS3Chunk_2']
            },
            {manager: connection.manager}
        );

        const recognitionResults = await getItemFromDBById(RecognitionResults, savedRecognitionResults.id);

        expect(recognitionResults?.documentId).toBe(insertedDocument.id);
        expect(recognitionResults?.status).toBe(RecognitionResultStatus.SUCCESS);
        expect(recognitionResults?.chunks).toEqual(['stubS3Chunk_1', 'stubS3Chunk_2']);
    });
});

describe('update document status', () => {
    it('should start recognition', async () => {
        const document = await addDocument();

        const connection = await ensureConnection();

        await changeDocumentStatus(document.id, RecognitionRequestStatus.IN_PROGRESS, {manager: connection.manager});

        const stubDocument = await getItemFromDBById(Documents, document.id);

        expect(stubDocument?.status).toBe(RecognitionRequestStatus.IN_PROGRESS);
    });

    it('should finish recognition', async () => {
        const document = await addDocument();

        const connection = await ensureConnection();

        await changeDocumentStatus(document.id, RecognitionRequestStatus.FINISHED, {manager: connection.manager});

        const stubDocument = await getItemFromDBById(Documents, document.id);

        expect(stubDocument?.status).toBe(RecognitionRequestStatus.FINISHED);
    });
});
