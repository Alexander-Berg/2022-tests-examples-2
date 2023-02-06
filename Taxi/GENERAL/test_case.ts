import { CircuitSchemaJson, TestCaseInfo } from "../definitions";
export type TestCaseResult = {
    /**
    * Идентификатор тест кейса
    * */
    test_case_id: number;
    /**
    * Тип проверки тест кейса
    * */
    check_type: string;
    /**
    * Результат выполнения теста
    * */
    passed: boolean;
    /**
    * Запускался ли тест
    * */
    ignored: boolean;
    /**
    * Описание тест кейса
    * */
    description: string;
    /**
    * Ошибка при выполнении тест кейса
    * */
    error_message?: string;
};
export type TestCaseResultState = "Success" | "WithFailures" | "Error";
export type RunTestsResponse = {
    state: TestCaseResultState;
    test_case_results: TestCaseResult[];
    /**
    * Сообщение об ошибке, если она произошла
    * */
    error_message?: string;
};
export type RunTestsRequestBody = {
    /**
    * Остановить выполнение, если в пачке тестов есть хотя бы один упавший
    * */
    break_on_failure?: boolean;
    /**
    * Идентификатор тестируемой схемы
    * */
    schema_id: string;
    schema_json: CircuitSchemaJson;
    /**
    * Идентификаторы тестов, которые надо прогнать, даже если они отключены (enabled=false)
    * */
    test_case_ids?: number[];
};
export type UpsertTestCaseRequestBody = {
    test_case_info: TestCaseInfo;
    /**
    * Идентификатор схемы
    * */
    schema_id: string;
    /**
    * Идентификатор тестовых данных
    * */
    test_data_id: number;
    /**
    * Описание данных
    * */
    description: string;
    /**
    * Запускается ли тест кейс автоматически при сохранении схемы
    * */
    is_enabled: boolean;
};
export type UpsertTestCaseResponse = {
    /**
    * Идентификатор созданного тест кейса
    * */
    test_case_id: number;
};
export type RetrieveTestCaseResponse = {
    test_case_info: TestCaseInfo;
    /**
    * Идентификатор схемы
    * */
    schema_id: string;
    /**
    * Идентификатор тестовых данных
    * */
    test_data_id: number;
    /**
    * Описание данных
    * */
    description: string;
    /**
    * Запускается ли тест кейс автоматически при сохранении схемы
    * */
    is_enabled: boolean;
};
export type TestCaseListItem = {
    /**
    * Идентификатор тест кейса
    * */
    id: number;
    /**
    * Описание тест кейса
    * */
    description: string;
    /**
    * Идентификатор схемы
    * */
    schema_id: string;
    /**
    * Тип проверки тест кейса
    * */
    check_type: string;
    /**
    * Запускается ли тест кейс автоматически при сохранении схемы
    * */
    is_enabled: boolean;
};
export type TestCaseList = {
    /**
    * Информация о включенных тест кейсах
    * */
    enabled: TestCaseListItem[];
    /**
    * Информация о выключенных тест кейсах
    * */
    disabled: TestCaseListItem[];
};
export type ActivateTestCaseResponse = {
    /**
    * Активирован ли тест кейс
    * */
    is_enabled: boolean;
};
