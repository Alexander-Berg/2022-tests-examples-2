import modelPath from '_utils/modelPath';

import {CheckType} from '../../enums';
import {TestCheckModel, TestMockModel} from '../../types';
import {TEST_CHECK_EDIT_MODEL, TEST_MOCK_EDIT_MODEL} from './consts';

export const testCheckModel = modelPath(TEST_CHECK_EDIT_MODEL);
export const testMockModel = modelPath(TEST_MOCK_EDIT_MODEL);

export const makeDefaultTestMockModel = (): TestMockModel => ({
    mockName: '',
    isResourceMock: false,
    resource: '',
    code: '',
    _id: '',
});

export const makeDefaultTestCheckModel = (): TestCheckModel => ({
    checkName: '',
    checkType: CheckType.Combined,
    ignoreAdditionalParams: false,
    code: '',
    _id: '',
});
