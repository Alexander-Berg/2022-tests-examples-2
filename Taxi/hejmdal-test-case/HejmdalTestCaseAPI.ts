import {adminApi} from '_utils/httpApi';

import {
    ActivateTestCaseResponse,
    RetrieveTestCaseResponse,
    RunTestsRequestBody,
    RunTestsResponse,
    TestCaseList,
    UpsertTestCaseRequestBody,
    UpsertTestCaseResponse
} from './types';

const API_URL = 'hejmdal/v1/test-case';

export default class HejmdalTestCaseAPI {
    public static toString = () => 'HejmdalTestCaseAPI';

    /**
     * Получить упорядоченный по id список id, schema_id и описаний тест кейсов
     * @param schema_id Идентификатор схемы, для которой необходимо получить
     * список тест кейсов. Если не указан, получить список тест кейсов для всех схем
     */
    public list(schema_id?: string): Promise<TestCaseList> {
        return adminApi.post<{}, TestCaseList>(`${API_URL}/list`, {}, {query: {schema_id}});
    }

    /**
     * Протестировать схему
     * @param body
     */
    public run(body: RunTestsRequestBody): Promise<RunTestsResponse> {
        return adminApi.post<RunTestsRequestBody, RunTestsResponse>(`${API_URL}/run`, body);
    }

    /**
     * Создать тест кейс
     * @param body Тест кейс
     */
    public create(body: UpsertTestCaseRequestBody): Promise<UpsertTestCaseResponse> {
        return adminApi.post<UpsertTestCaseRequestBody, UpsertTestCaseResponse>(`${API_URL}/create`, body);
    }

    /**
     * Получить тест кейс по идентификатору
     * @param id Идентификатор тест кейса
     */
    public read(id: number): Promise<RetrieveTestCaseResponse> {
        return adminApi.post<{}, RetrieveTestCaseResponse>(`${API_URL}/read`, {}, {query: {id}});
    }

    /**
     * Обновить тест кейс по идентификатору
     * @param id Идентификатор тест кейса
     * @param body Тест кейс
     */
    public update(id: number, body: UpsertTestCaseRequestBody): Promise<UpsertTestCaseResponse> {
        return adminApi.put<UpsertTestCaseRequestBody, UpsertTestCaseResponse>(`${API_URL}/update`, body, {
            query: {id}
        });
    }

    /**
     * Удалить тест кейс по идентификатору
     * @param id Идентификатор тест кейса
     */
    public delete(id: number): Promise<{}> {
        return adminApi.del<{}, {}>(`${API_URL}/delete`, {}, {query: {id}});
    }

    /**
     * Активировать тест кейс по идентификатору
     * @param id Идентификатор тест кейса
     * @param do_activate Надо ли запускать тест кейс автоматически при сохранении схемы
     */
    public activate(id: number, do_activate?: boolean): Promise<ActivateTestCaseResponse> {
        return adminApi.post<{}, ActivateTestCaseResponse>(`${API_URL}/activate`, {}, {query: {id, do_activate}});
    }
}

export const apiInstance = new HejmdalTestCaseAPI();
