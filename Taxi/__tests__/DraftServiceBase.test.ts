import {expectSaga} from 'redux-saga-test-plan';
import * as matchers from 'redux-saga-test-plan/matchers';

import {DraftModes} from '_types/common/drafts';

import {DraftServiceLoadArgs, DraftsServiceBase} from '../services/DraftServiceBase';

describe('DraftServiceBase', () => {
    test('openDraftForm вызывает переопределнный в сервисе findDraft', () => {
        const mockFn = jest.fn();

        // tslint:disable-next-line: max-classes-per-file
        class TestService extends DraftsServiceBase {
            public static toString = () => 'TestService';

            public static *findDraft(args: DraftServiceLoadArgs) {
                mockFn(args);
            }
        }

        const sagaArgs: DraftServiceLoadArgs = {id: '1', mode: DraftModes.ShowDraft};

        return expectSaga(function* () {
            return yield matchers.call([TestService, TestService.openDraftForm], sagaArgs);
        })
            .run()
            .then(runResult => {
                expect(mockFn).toHaveBeenCalledTimes(1);
                expect(mockFn).toHaveBeenCalledWith(sagaArgs);
                expect(TestService.lastArgs).toEqual(sagaArgs);
            });
    });
});
