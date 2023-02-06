import {Tasks} from '@/src/entities/tasks/entity';
import {ensureConnection} from 'service/db';

export async function addTask(externalId: string, storeId: number, data: {}, date: string) {
    const connection = await ensureConnection();

    return await connection.getRepository(Tasks).insert([{externalId, storeId, data, date}]);
}
