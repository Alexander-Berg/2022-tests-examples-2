import {sortBy} from 'lodash';
import {call, put} from 'typed-redux-saga';

import {pure as commonActions} from '_infrastructure/actions';
import {createService} from '_sagas/createService';
import {catchWith, daemon, operation} from '_sagas/decorators';
import {showError} from '_sagas/showError';
import {Service} from '_types/common/infrastructure';
import {buildPath} from '_utils/buildPath';

import {apiInstance as checksAPI} from '../../../common/api/ChecksAPI';
import {apiInstance as mocksAPI} from '../../../common/api/MocksAPI';
import {apiInstance as testsAPI} from '../../../common/api/TestsAPI';
import {getCurrentServiceName} from '../../../common/utils';
import {TESTS_ROUTE} from '../../consts';
import {TabType} from '../../enums';
import {QueryParams} from '../../types';

class PipelineTestsService {
    public static toString = () => 'PipelineTestsService';

    @operation
    @catchWith(showError)
    public static *requestMockList(service: string) {
        const {resources_mocks, prefetched_resources_mocks, input_mocks} = yield* call(
            mocksAPI.request,
            service,
        );
        return [...resources_mocks, ...prefetched_resources_mocks, ...input_mocks];
    }

    @operation
    @catchWith(showError)
    public static *requestCheckList(service: string) {
        const {output_checks} = yield* call(checksAPI.request, service);
        return output_checks;
    }

    @operation
    @catchWith(showError)
    public static *requestTestList(service: string) {
        const {tests} = yield* call(testsAPI.request, service);
        return sortBy(tests, m => m.scope);
    }

    @operation
    public static *loadEntityList(service: string, tabType: TabType) {
        switch (tabType) {
            case TabType.Mock: {
                yield* call(PipelineTestsService.requestMockList, service);
            }
            case TabType.Check: {
                yield* call(PipelineTestsService.requestCheckList, service);
            }
            case TabType.Test: {
                yield* call(PipelineTestsService.requestTestList, service);
            }
        }
    }

    @daemon()
    public static *navigate(query: Partial<QueryParams>) {
        const service = getCurrentServiceName();
        const path = buildPath(TESTS_ROUTE, service);
        yield* put(commonActions.router.pushWithQuery(path, query));
    }
}

export const service = createService(PipelineTestsService, {bind: true});

export default PipelineTestsService as Service<typeof PipelineTestsService>;
