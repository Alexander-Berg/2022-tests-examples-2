import {trim} from 'lodash';

import {StrictModel} from '_types/common/infrastructure';

import {FormMode, TabType} from './enums';
import {CheckModel, MockModel, TestModel} from './types';

export * from '../init/consts';

export const MOCK_MODEL = 'modelA' as StrictModel<MockModel>;
export const CHECK_MODEL = 'modelB' as StrictModel<CheckModel>;
export const TEST_MODEL = 'modelC' as StrictModel<TestModel>;

export const LABELS = {
    ALGORITHMS: 'Алгоритмы',
    ALGORITHM_TESTS: 'Тесты алгоритмов',
    MOCK: 'Мок',
    MOCKS: 'Моки',
    CHECK: 'Проверка',
    CHECKS: 'Проверки',
    TEST: 'Тест',
    TESTS: 'Тесты',
    SELECT_SERVICE: 'Выберите сервис',
    NAME: 'Название',
    INPUT_MOCK: 'Мок ввода',
    RESOURCE_MOCK: 'Мок ресурса',
    TYPE: 'Тип',
    RESOURCE: 'Ресурс',
    JSON: 'json',
    JAVASCRIPT: 'javascript',
    CREATE: 'Создать',
    EDIT: 'Редактировать',
    SAVE_CHANGES: 'Сохранить изменения',
    CANCEL: 'Отмена',
    MOCK_CREATE: 'Создание Мока',
    MOCK_EDIT: 'Редактирование Мока',
    MOCK_VIEW: 'Просмотр Мока',
    CHECK_CREATE: 'Создание Проверки',
    CHECK_EDIT: 'Редактирование Проверки',
    CHECK_VIEW: 'Просмотр Проверки',
    TEST_CREATE: 'Создание Теста',
    TEST_EDIT: 'Редактирование Теста',
    TEST_VIEW: 'Просмотр Теста',
    MODE_NOT_SUPPORTED: 'Режим не поддреживается',
    COMBINED: 'Combined',
    IMPERATIVE: 'Imperative',
    CODE: 'Код',
    FUNCTION_OUTPUT: 'function (output) {',
    IGNORE_ADDITIONAL_PARAMS: 'Игнорировать дополнительные поля в объекте',
    PIPELINE: 'Pipeline',
    GLOBAL: 'Global',
    SCOPE: 'Scope',
    TESTCASE: 'Тест-кейс',
    TESTCASES: 'Тест-кейсы',
    SAVE: 'Сохранить',
    RESOURCES_MOCKS: 'Моки ресурсов',
    MOCKS_AND_CHECKS_IN_TEST: 'Моки и проверки, доступные только для этого теста',
    CREATE_TEST_MOCK: 'Создание Мока для Теста',
    CREATE_TEST_CHECK: 'Создание Проверки для Теста',
    EDIT_TEST_MOCK: 'Редактирование Мока для Теста',
    EDIT_TEST_CHECK: 'Редактирование Проверки для Теста',
};

export const NOTIFICATIONS = {
    MOCK_CREATED: 'Мок успешно создан',
    CHECK_CREATED: 'Проверка успешно создана',
    TEST_CREATED: 'Тест успешно создан',
    MOCK_EDITED: 'Мок успешно изменен',
    CHECK_EDITED: 'Проверка успешно изменена',
    TEST_EDITED: 'Тест успешно изменен',
    DELETE: 'Удалить',
    IS_MOCK_DELETE: 'Вы действительно хотите удалить мок',
    IS_CHECK_DELETE: 'Вы действительно хотите удалить проверку',
    IS_TEST_DELETE: 'Вы действительно хотите удалить тест',
    MOCK_DELETED: 'Мок успешно удален',
    CHECK_DELETED: 'Проверка успешно удалена',
    TEST_DELETED: 'Тест успешно удален',
};

export const NAME_REGEXP = /^[^_\d\W]\w*$/;

export const ERRORS = {
    FILL_FIELD: 'Заполните поле',
    INVALID_NAME: `Имя должно соответствовать регулярному выражению: ${trim(NAME_REGEXP.toString(), '/')}`,
    INVALID_JSON: 'Не валидный JSON',
    NAME_IS_OCCUPIED: 'Имя уже используется',
};

export const SIDE_TITLES = {
    [TabType.Mock]: {
        [FormMode.Create]: LABELS.MOCK_CREATE,
        [FormMode.View]: LABELS.MOCK_VIEW,
        [FormMode.Edit]: LABELS.MOCK_EDIT,
    },
    [TabType.Check]: {
        [FormMode.Create]: LABELS.CHECK_CREATE,
        [FormMode.View]: LABELS.CHECK_VIEW,
        [FormMode.Edit]: LABELS.CHECK_EDIT,
    },
    [TabType.Test]: {
        [FormMode.Create]: LABELS.TEST_CREATE,
        [FormMode.View]: LABELS.TEST_VIEW,
        [FormMode.Edit]: LABELS.TEST_EDIT,
    },
};

export const CREATE_BUTTON_TITLES = {
    [TabType.Mock]: LABELS.MOCK,
    [TabType.Check]: LABELS.CHECK,
    [TabType.Test]: LABELS.TEST,
};

export const TABS = [
    {id: TabType.Mock, title: LABELS.MOCKS},
    {id: TabType.Check, title: LABELS.CHECKS},
    {id: TabType.Test, title: LABELS.TESTS},
];
