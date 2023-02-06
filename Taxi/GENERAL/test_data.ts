import { EntryPointInputs, NamedTimeSeries } from "../definitions";
export type TargetState = "Ok" | "Warning" | "Critical" | "Compute";
export type SaveDataRequestBody = {
    /**
    * id циркута
    * */
    circuit_id: string;
    /**
    * id выхода
    * */
    out_point_id?: string;
    /**
    * время алерта
    * */
    precedent_time: string;
    /**
    * Длительность после момента precedent_time, дефолт в конфиге HEJMDAL_TEST_DATA_SAVER
    * */
    duration_after_min?: number;
    /**
    * Длительность до момента precedent_time (не считая истории) в минутах, дефолт в конфиге HEJMDAL_TEST_DATA_SAVER
    * */
    duration_before_min?: number;
    target_state?: TargetState;
    /**
    * Состояние, которое было при алерте
    * */
    alert_state?: string;
    /**
    * Насколько все плохо
    * */
    how_bad_is_it?: string;
    /**
    * Что не так с алертом
    * */
    reason?: string;
};
export type UpsertTestDataRequestBody = {
    /**
    * Идентификатор схемы
    * */
    schema_id: string;
    /**
    * Описание данных
    * */
    description: string;
    entry_point_inputs: EntryPointInputs;
};
export type UpsertTestDataResponse = {
    /**
    * Идентификатор созданых тестовых данных
    * */
    test_data_id: number;
    /**
    * Начало интервала тестовых данных
    * */
    start_time: string;
    /**
    * Конец интервала тестовых данных
    * */
    end_time: string;
};
export type RetrieveTestDataResponse = {
    /**
    * Идентификатор схемы
    * */
    schema_id: string;
    /**
    * Описание данных
    * */
    description: string;
    /**
    * Данные enrty_point-ов в формате JSON
    * */
    test_data: NamedTimeSeries[];
    /**
    * Начало интервала тестовых данных
    * */
    start_time: string;
    /**
    * Конец интервала тестовых данных
    * */
    end_time: string;
};
export type TestDataListItem = {
    /**
    * Идентификатор тестовых данных
    * */
    id: number;
    /**
    * Описание данных
    * */
    description: string;
    /**
    * Идентификатор схемы
    * */
    schema_id: string;
    /**
    * Идентификаторы тест кейсов
    * */
    test_case_ids?: number[];
};
export type TestDataList = {
    /**
    * Информация о тестовых данных
    * */
    test_data_items: TestDataListItem[];
};
