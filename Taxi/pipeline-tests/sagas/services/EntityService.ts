import {all, call, put, select} from 'typed-redux-saga';
import uuid from 'uuid';

import {pure as commonActions} from '_infrastructure/actions';
import {getOperation, getStrictModel} from '_infrastructure/selectors';
import {THEME} from '_pkg/consts';
import {createService} from '_sagas/createService';
import {catchWith, confirm, daemon, notifySuccess, validate} from '_sagas/decorators';
import {showError} from '_sagas/showError';
import {Service} from '_types/common/infrastructure';
import {buildPath} from '_utils/buildPath';

import {apiInstance as checksAPI} from '../../../common/api/ChecksAPI';
import {apiInstance as mocksAPI} from '../../../common/api/MocksAPI';
import {apiInstance as testsAPI} from '../../../common/api/TestsAPI';
import {LOAD_RESOURCES_ID} from '../../../common/sagas/services/PipelineCommonService';
import {getCurrentServiceName} from '../../../common/utils';
import {NOTIFICATIONS, TESTS_ROUTE} from '../../consts';
import {
    prepareCheck,
    prepareCheckModel,
    prepareMock,
    prepareMockModel,
    preparePipelineTest,
    prepareTest,
} from '../../converters';
import {FormMode, TabType} from '../../enums';
import {QueryParams} from '../../types';
import {
    checkModel,
    makeDefaultCheckModel,
    makeDefaultMockModel,
    makeDefaultTestModel,
    mockModel,
    testModel,
} from '../../utils';
import {makeCheckValidator} from '../validators/checkValidator';
import {makeMockValidator} from '../validators/mockValidator';
import {testValidator} from '../validators/testValidator';
import PipelineTestsService from './PipelineTestsService';

const mockValidator = makeMockValidator(mockModel(m => m));
const checkValidator = makeCheckValidator(checkModel(m => m));

class EntityService {
    public static toString = () => 'PipelineTestsEntityService';

    public static *loadMockModel(mode: FormMode, id: Undefinable<string>) {
        const serviceName = getCurrentServiceName();
        switch (mode) {
            case FormMode.View:
            case FormMode.Edit: {
                if (id) {
                    const mock = yield* call(mocksAPI.find, serviceName, id);
                    return prepareMockModel(mock);
                }
            }
            default: {
                return makeDefaultMockModel();
            }
        }
    }

    public static *loadCheckModel(mode: FormMode, id: Undefinable<string>) {
        const serviceName = getCurrentServiceName();
        switch (mode) {
            case FormMode.View:
            case FormMode.Edit: {
                if (id) {
                    const check = yield* call(checksAPI.find, serviceName, id);
                    return prepareCheckModel(check);
                }
            }
            default: {
                return makeDefaultCheckModel();
            }
        }
    }

    public static *loadTestModel(mode: FormMode, id: Undefinable<string>) {
        const serviceName = getCurrentServiceName();
        switch (mode) {
            case FormMode.View:
            case FormMode.Edit: {
                if (id) {
                    const test = yield* call(testsAPI.find, serviceName, id);
                    return prepareTest(test);
                }
            }
            default: {
                return makeDefaultTestModel();
            }
        }
    }

    public static *loadEntityModel(tabType: TabType, mode: FormMode, id: Undefinable<string>) {
        if (tabType === TabType.Mock) {
            const model = yield* call(EntityService.loadMockModel, mode, id);
            yield* put(
                commonActions.form.strict.change(
                    mockModel(m => m),
                    model,
                ),
            );
        } else if (tabType === TabType.Check) {
            const model = yield* call(EntityService.loadCheckModel, mode, id);
            yield* put(
                commonActions.form.strict.change(
                    checkModel(m => m),
                    model,
                ),
            );
        } else if (tabType === TabType.Test) {
            const model = yield* call(EntityService.loadTestModel, mode, id);
            yield* put(
                commonActions.form.strict.change(
                    testModel(m => m),
                    model,
                ),
            );
        }
    }

    @validate(mockValidator)
    @catchWith(showError)
    @notifySuccess(NOTIFICATIONS.MOCK_CREATED)
    public static *saveMock() {
        const model = yield* select(getStrictModel(mockModel(m => m)));

        const {result: resources = []} = yield* select(getOperation(LOAD_RESOURCES_ID));

        const id = uuid.v4();

        yield* call(mocksAPI.create, getCurrentServiceName(), prepareMock(model, resources, id));

        yield* call(EntityService.navigate, {
            id,
            mode: FormMode.View,
        });
    }

    @validate(checkValidator)
    @catchWith(showError)
    @notifySuccess(NOTIFICATIONS.CHECK_CREATED)
    public static *saveCheck() {
        const model = yield* select(getStrictModel(checkModel(m => m)));

        const id = uuid.v4();

        yield* call(checksAPI.create, getCurrentServiceName(), prepareCheck(model, id));

        yield* call(EntityService.navigate, {
            id,
            mode: FormMode.View,
        });
    }

    @validate(testValidator)
    @catchWith(showError)
    @notifySuccess(NOTIFICATIONS.TEST_CREATED)
    public static *saveTest() {
        const model = yield* select(getStrictModel(testModel(m => m)));

        const {result: resources = []} = yield* select(getOperation(LOAD_RESOURCES_ID));

        const id = uuid.v4();

        yield* call(testsAPI.create, getCurrentServiceName(), preparePipelineTest(model, resources, id));

        yield* call(EntityService.navigate, {
            id,
            mode: FormMode.View,
        });
    }

    @daemon()
    public static *saveEntity(tabType: TabType) {
        const service = getCurrentServiceName();

        if (tabType === TabType.Mock) {
            yield* call(EntityService.saveMock);
        } else if (tabType === TabType.Check) {
            yield* call(EntityService.saveCheck);
        } else if (tabType === TabType.Test) {
            yield* call(EntityService.saveTest);
        }

        yield* call(PipelineTestsService.loadEntityList, service, tabType);
    }

    @validate(mockValidator)
    @catchWith(showError)
    @notifySuccess(NOTIFICATIONS.MOCK_EDITED)
    public static *editMock(id: string) {
        const model = yield* select(getStrictModel(mockModel(m => m)));

        const {result: resources = []} = yield* select(getOperation(LOAD_RESOURCES_ID));

        yield* call(mocksAPI.update, getCurrentServiceName(), prepareMock(model, resources, id));

        yield* call(EntityService.navigate, {
            id,
            mode: FormMode.View,
        });
    }

    @validate(checkValidator)
    @catchWith(showError)
    @notifySuccess(NOTIFICATIONS.CHECK_EDITED)
    public static *editCheck(id: string) {
        const model = yield* select(getStrictModel(checkModel(m => m)));

        yield* call(checksAPI.update, getCurrentServiceName(), prepareCheck(model, id));

        yield* call(EntityService.navigate, {
            id,
            mode: FormMode.View,
        });
    }

    @validate(testValidator)
    @catchWith(showError)
    @notifySuccess(NOTIFICATIONS.TEST_EDITED)
    public static *editTest(id: string) {
        const model = yield* select(getStrictModel(testModel(m => m)));

        const {result: resources = []} = yield* select(getOperation(LOAD_RESOURCES_ID));

        yield* call(testsAPI.update, getCurrentServiceName(), preparePipelineTest(model, resources, id));

        yield* call(EntityService.navigate, {
            id,
            mode: FormMode.View,
        });
    }

    @daemon()
    public static *editEntity(tabType: TabType, id: string) {
        const service = getCurrentServiceName();

        if (tabType === TabType.Mock) {
            yield* call(EntityService.editMock, id);
        } else if (tabType === TabType.Check) {
            yield* call(EntityService.editCheck, id);
        } else if (tabType === TabType.Test) {
            yield* call(EntityService.editTest, id);
        }

        yield* call(PipelineTestsService.loadEntityList, service, tabType);
    }

    @confirm({
        title: `${NOTIFICATIONS.IS_MOCK_DELETE}?`,
        confirmButtonText: NOTIFICATIONS.DELETE,
        confirmButtonTheme: THEME.COLOR,
    })
    @catchWith(showError)
    @notifySuccess(NOTIFICATIONS.MOCK_DELETED)
    public static *removeMock(service: string, id: string) {
        yield* call(mocksAPI.remove, service, id);
    }

    @confirm({
        title: `${NOTIFICATIONS.IS_CHECK_DELETE}?`,
        confirmButtonText: NOTIFICATIONS.DELETE,
        confirmButtonTheme: THEME.COLOR,
    })
    @catchWith(showError)
    @notifySuccess(NOTIFICATIONS.CHECK_DELETED)
    public static *removeCheck(service: string, id: string) {
        yield* call(checksAPI.remove, service, id);
    }

    @confirm({
        title: `${NOTIFICATIONS.IS_TEST_DELETE}?`,
        confirmButtonText: NOTIFICATIONS.DELETE,
        confirmButtonTheme: THEME.COLOR,
    })
    @catchWith(showError)
    @notifySuccess(NOTIFICATIONS.TEST_DELETED)
    public static *removeTest(service: string, id: string) {
        yield* call(testsAPI.remove, service, id);
    }

    @daemon()
    public static *removeEntity(tabType: TabType, id: string) {
        const service = getCurrentServiceName();
        if (tabType === TabType.Mock) {
            yield* call(EntityService.removeMock, service, id);
        } else if (tabType === TabType.Check) {
            yield* call(EntityService.removeCheck, service, id);
        } else if (tabType === TabType.Test) {
            yield* call(EntityService.removeTest, service, id);
        }

        yield* call(PipelineTestsService.loadEntityList, service, tabType);
    }

    @daemon()
    public static *navigate(query: Partial<QueryParams>) {
        const path = buildPath(TESTS_ROUTE, getCurrentServiceName());
        yield* put(commonActions.router.pushWithQuery(path, query));
    }
}

export const service = createService(EntityService, {
    bind: true,
    onBeforeRun: function* () {
        yield* all([
            put(commonActions.form.strict.reset(mockModel(m => m))),
            put(commonActions.form.strict.reset(checkModel(m => m))),
            put(commonActions.form.strict.reset(testModel(m => m))),
        ]);
    },
});

export default EntityService as Service<typeof EntityService>;
