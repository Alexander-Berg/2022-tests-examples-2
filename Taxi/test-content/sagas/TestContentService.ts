import {all, call, put, select} from 'typed-redux-saga';
import uuid from 'uuid';

import {pure as commonActions} from '_infrastructure/actions';
import {getStrictModel} from '_infrastructure/selectors';
import {createService} from '_sagas/createService';
import {daemon, operation, validate} from '_sagas/decorators';
import {Service} from '_types/common/infrastructure';
import {isEmpty} from '_utils/strict/validators';

import {TestSubmode} from '../../../enums';
import {makeCheckValidator} from '../../../sagas/validators/checkValidator';
import {makeMockValidator} from '../../../sagas/validators/mockValidator';
import {testModel} from '../../../utils';
import {testCheckModel, testMockModel} from '../utils';

export type State = {
    submode?: TestSubmode;
    editIndex?: number;
};

const mockValidator = makeMockValidator(testMockModel(m => m));
const checkValidator = makeCheckValidator(testCheckModel(m => m));

class TestContentService {
    public static toString = () => 'EfficiencyPipelinesTestContentService';

    @operation
    public static *setState(state: State) {
        return state;
    }

    @daemon()
    public static *closeSubmode() {
        yield* call(TestContentService.setState, {});
    }

    @daemon()
    public static *setSubmode(submode: TestSubmode, editIndex: number) {
        yield* call(TestContentService.setState, {submode, editIndex});
    }

    @validate(checkValidator, {args: (checkNameList: string[]) => ({checkNameList})})
    public static *getValidCheckModel(_checkNameList: string[]) {
        return yield* select(getStrictModel(testCheckModel(m => m)));
    }

    @daemon()
    public static *saveCheck(editIndex: number) {
        const checks = yield* select(getStrictModel(testModel(m => m.checks)));
        const model = yield* call(
            TestContentService.getValidCheckModel,
            checks.reduce<string[]>((acc, {checkName}, checkIndex) => {
                if (editIndex !== checkIndex) {
                    acc.push(checkName);
                }
                return acc;
            }, []),
        );
        yield* put(
            commonActions.form.strict.change(
                testModel(m => m.checks[editIndex]),
                {
                    ...model,
                    _id: isEmpty(model._id) ? uuid.v4() : model._id,
                },
            ),
        );
        yield* call(TestContentService.closeSubmode);
    }

    @validate(mockValidator, {args: (mockNameList: string[]) => ({mockNameList})})
    public static *getValidMockModel(_mockNameList: string[]) {
        return yield* select(getStrictModel(testMockModel(m => m)));
    }

    @daemon()
    public static *saveMock(editIndex: number) {
        const mocks = yield* select(getStrictModel(testModel(m => m.mocks)));

        const model = yield* call(
            TestContentService.getValidMockModel,
            mocks.reduce<string[]>((acc, {mockName}, mockIndex) => {
                if (editIndex !== mockIndex) {
                    acc.push(mockName);
                }
                return acc;
            }, []),
        );
        yield* put(
            commonActions.form.strict.change(
                testModel(m => m.mocks[editIndex]),
                {
                    ...model,
                    _id: isEmpty(model._id) ? uuid.v4() : model._id,
                },
            ),
        );
        yield* call(TestContentService.closeSubmode);
    }
}

export const service = createService(TestContentService, {
    bind: true,
    onBeforeRun: function* () {
        yield* all([
            put(commonActions.form.strict.reset(testCheckModel(m => m))),
            put(commonActions.form.strict.reset(testMockModel(m => m))),
        ]);
    },
});

export default TestContentService as Service<typeof TestContentService>;
