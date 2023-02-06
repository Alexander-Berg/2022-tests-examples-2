import {magicService} from '@blocks/AuthSilent/magicService';
import {magicDoneCallback} from '../magicDoneCallback';
import {magicFailCallback} from '../magicFailCallback';
import {magicInit} from '../magicInit';

jest.mock('@blocks/AuthSilent/magicService', () => ({
    magicService: {
        init: jest.fn(),
        start: jest.fn()
    }
}));
jest.mock('../magicDoneCallback', () => ({
    magicDoneCallback: jest.fn()
}));
jest.mock('../magicFailCallback', () => ({
    magicFailCallback: jest.fn()
}));

describe('authv2/magic/magicInit', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });
    it('should call init', () => {
        const action = magicInit();
        const dispatchMock = jest.fn();
        const getStateMock = () => ({auth: {magicTrack: 'qwe', magicCSRF: 'asd'}});

        action(dispatchMock, getStateMock);

        expect(magicService.init).toBeCalledWith({
            doneCallback: magicDoneCallback,
            failCallback: magicFailCallback(dispatchMock),
            trackId: 'qwe',
            csrfToken: 'asd'
        });
        expect(magicService.start).toBeCalled();
    });
});
