import {Documents} from '@/src/entities/documents/entity';
import {Stores} from '@/src/entities/stores/entity';
import {changeTaskRecognitionStatus} from '@/src/entities/tasks/api/change-status';
import {Tasks} from '@/src/entities/tasks/entity';
import {ensureConnection} from 'service/db';
import {InputDocumentType, RecognitionRequestStatus as DocumentRecognitionRequestStatus} from 'types/documents';
import {RecognitionRequestStatus as TaskRecognitionRequestStatus} from 'types/task';

import {getToken, handleTokenSigning} from './sign-token';
import {checkIfTokenIsValid} from './utils';

describe('should sign JWT tokens correctly', () => {
    let accessToken = '';
    let taskId = 0;

    beforeEach(async () => {
        const connection = await ensureConnection();

        const store = await connection
            .getRepository(Stores)
            .createQueryBuilder('stores')
            .insert()
            .into(Stores)
            .values({name: 'Test store', externalId: 'qwerty_id'})
            .execute();
        const storeId = store.identifiers[0].id;

        const task = await connection
            .getRepository(Tasks)
            .createQueryBuilder('tasks')
            .insert()
            .into(Tasks)
            .values({
                externalId: 'azerty_id',
                storeId,
                data: {
                    id: '5f6a3d70-08ba-11ec-329e-525400123456',
                    date: '2021-08-31T21:00:00.000Z',
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
                }
            })
            .execute();
        taskId = task.identifiers[0].id;
    });

    it('sign token', async () => {
        accessToken = await getToken('erp_id', 'task_id');
        const accessTokenParts = accessToken.split('.');

        expect(accessTokenParts).toHaveLength(3);
        expect(accessToken).toHaveLength(229);
    });

    it('verify token', async () => {
        const isTokenValid = await checkIfTokenIsValid(accessToken, 'task_id');

        expect(isTokenValid).toBeTruthy();
    });

    it('should return 200', async () => {
        expect.assertions(1);

        const response = await handleTokenSigning('azerty_id', 'ru');
        expect(response.code).toBe('OK');
    });

    it('should throw 404', async () => {
        expect.assertions(1);

        try {
            await handleTokenSigning('azerty_id1', 'ru');
        } catch (error) {
            expect(error.jse_info.name).toBe('ENTITY_NOT_FOUND_ERROR');
        }
    });

    it('should throw 409', async () => {
        expect.assertions(1);

        await changeTaskRecognitionStatus(taskId, {status: TaskRecognitionRequestStatus.FINISHED});

        const connection = await ensureConnection();
        await connection.getRepository(Documents).insert([
            {
                taskId,
                originalDocumentImage: '',
                originalName: '',
                uid: '',
                status: DocumentRecognitionRequestStatus.FINISHED,
                type: InputDocumentType.Another,
                date: new Date(),
                number: '',
                groupNumber: 0,
                description: ''
            }
        ]);

        try {
            await handleTokenSigning('azerty_id', 'ru');
        } catch (error) {
            expect(error.jse_info.name).toBe('CONFLICT');
        }
    });
});
