import {StrictModel} from '_types/common/infrastructure';

import {LABELS} from '../../consts';
import {TestSubmode} from '../../enums';
import {TestCheckModel, TestMockModel} from '../../types';

export const TEST_CHECK_EDIT_MODEL = 'EfficiecnyPipelineTestsCheckEditModel' as StrictModel<TestCheckModel>;
export const TEST_MOCK_EDIT_MODEL = 'EfficiecnyPipelineTestsMockEditModel' as StrictModel<TestMockModel>;

export const SUBMODE_EDIT_HEADERS = {
    [TestSubmode.MockEdit]: LABELS.EDIT_TEST_MOCK,
    [TestSubmode.CheckEdit]: LABELS.EDIT_TEST_CHECK,
};
