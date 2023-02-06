import {Tasks} from '@/src/entities/tasks/entity';
import {makeError} from 'server/errors';
import {ensureConnection} from 'service/db';

export async function getTaskByExternalId(externalId: string): Promise<Tasks | undefined> {
    const connection = await ensureConnection();
    const result = await connection.getRepository(Tasks).find({externalId});

    if (result.length > 1) {
        throw makeError('UNKNOWN_ERROR', {}, "There is a conflict of externalId's in Tasks");
    }

    return result[0] || undefined;
}
