import {IEntityAPI} from '_types/common/infrastructure';
import {adminApi} from '_utils/httpApi';

import {TestKindsResponse} from './types';

export default class TestKindsAPI implements IEntityAPI {
    public static toString = () => 'TestKindsAPI';

    public request(): Promise<TestKindsResponse> {
        return adminApi.get<never, TestKindsResponse>('/persey-labs/admin/v1/test-kinds');
    }
}

export const apiInstance = new TestKindsAPI();
