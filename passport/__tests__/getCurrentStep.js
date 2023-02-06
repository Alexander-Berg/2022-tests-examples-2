import {getCurrentStep} from '../getCurrentStep';

jest.mock('../getAuthRegCompleteConfig', () => ({
    getAuthRegCompleteConfig: jest.fn().mockReturnValue({
        firstStep: 'testFirstStep'
    })
}));

describe('@blocks/AuthRegComplete/logic/getCurrentStep', () => {
    afterEach(() => {
        jest.clearAllMocks();
    });
    it('should return firstStep if in state it s undefined', () => {
        expect(getCurrentStep({completeFlow: {}})).toEqual('testFirstStep');
    });
    it('should return step from state', () => {
        expect(getCurrentStep({completeFlow: {step: 'testStep'}})).toEqual('testStep');
    });
});
