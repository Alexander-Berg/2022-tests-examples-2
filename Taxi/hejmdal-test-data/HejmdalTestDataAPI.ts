import {adminApi} from '_utils/httpApi';

import {
    RetrieveTestDataResponse,
    SaveDataRequestBody,
    TestDataList,
    UpsertTestDataRequestBody,
    UpsertTestDataResponse
} from './types';

const API_URL = 'hejmdal/v1/test-data';

export default class HejmdalTestDataAPI {
    public static toString = () => 'HejmdalTestDataAPI';

    /**
     * Получить упорядоченный по id список id, schema_id и описаний тестовых данных
     * @param schema_id Идентификатор схемы, для которой необходимо получить
     * список тестовых данных. Если не указан, получить список для всех схем
     */
    public list(schema_id?: string): Promise<TestDataList> {
        return adminApi.post<{}, TestDataList>(`${API_URL}/list`, {}, {query: {schema_id}});
    }

    /**
     * Получить тестовые данные по идентификатору
     * @param id Идентификатор тестовых данных
     */
    public read(id: number): Promise<RetrieveTestDataResponse> {
        return adminApi.post<{}, RetrieveTestDataResponse>(`${API_URL}/read`, {}, {query: {id}});
    }

    /**
     * Сохранить временные ряды для заданного circuit_id
     * @param body Тестовые данные
     */
    public save(body: SaveDataRequestBody): Promise<{}> {
        return adminApi.post<SaveDataRequestBody, {}>(`${API_URL}/save`, body);
    }

    /**
     * Создать тестовые данные и сохранить их в базу
     * @param body Тестовые данные
     */
    public create(body: UpsertTestDataRequestBody): Promise<UpsertTestDataResponse> {
        return adminApi.post<UpsertTestDataRequestBody, UpsertTestDataResponse>(`${API_URL}/create`, body);
    }

    /**
     * Обновить тестовые данные по идентификатору
     * @param id Идентификатор тестовых данных
     * @param body Тестовые данные
     */
    public update(id: number, body: UpsertTestDataRequestBody): Promise<UpsertTestDataResponse> {
        return adminApi.put<UpsertTestDataRequestBody, UpsertTestDataResponse>(`${API_URL}/update`, body, {
            query: {id}
        });
    }

    /**
     * Удалить тестовые данные по идентификатору
     * @param id Идентификатор тестовых данных
     */
    public delete(id: number): Promise<{}> {
        return adminApi.del<{}, {}>(`${API_URL}/delete`, {}, {query: {id}});
    }
}

export const apiInstance = new HejmdalTestDataAPI();
