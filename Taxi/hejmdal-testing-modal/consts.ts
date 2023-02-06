import {OperationId, StrictModel} from '_types/common/infrastructure';

import {HejmdalTestingModel, TestsList} from './types';

export const HEJMDAL_TESTING_MODEL = 'HEJMDAL_TESTING_MODEL' as StrictModel<HejmdalTestingModel>;

export const LOAD_TESTS_LIST = 'LOAD_TESTS_LIST' as OperationId<TestsList>;

export const TEXTS = {
    MODAL_TITLE: 'Тестирование',
    RUN_ALL: 'Запустить все',
    RUN_SELECTED: 'Запустить выбранные',
    ENABLED_TESTS: 'Тесты',
    DISABLED_TESTS: 'Выключенные тесты',
    ID: 'ID',
    TYPE: 'Тип',
    DESC: 'Описание',
    RUN_TEST: 'Запустить',
    TO_DEBUG: 'В дебаг',
    NO_TESTS: 'Для данной схемы нет тестов'
};
