import {prepareStep} from '@blocks/AuthRegComplete/actions/prepareStep.js';
import {STEPS} from '@blocks/UserEntryFlow/steps';
import {getSuggestedLogins} from '@components/LoginSuggest/actions';
import {getCurrentStep} from '@blocks/AuthRegComplete/logic';

jest.mock('@components/LoginSuggest/actions', () => ({
    getSuggestedLogins: jest.fn()
}));
jest.mock('@blocks/AuthRegComplete/logic', () => ({
    getAuthRegCompleteConfig: jest.fn(),
    getCurrentStep: jest.fn()
}));

describe('@blocks/AuthRegComplete/actions/prepareStep.js', () => {
    afterEach(() => {
        jest.clearAllMocks();
    });
    it('should call getSuggestedLogins for STEPS.LOGIN if suggest did not load yet', async () => {
        const action = prepareStep();
        const dispatch = jest
            .fn()
            .mockImplementation((callback) => (typeof callback === 'function' ? callback() : undefined));
        const getState = jest.fn().mockReturnValue({});

        getCurrentStep.mockReturnValue(STEPS.LOGIN);

        await action(dispatch, getState);

        expect(getSuggestedLogins).toBeCalled();
    });
});
