import {sendFingerprint} from '../sendFingerprint';
import api from '@blocks/api';

jest.mock('@blocks/api', () => ({
    log: jest.fn()
}));
jest.mock('@plibs/greed', () => ({
    Greed: {
        safeGet: jest.fn().mockResolvedValue({
            test: 'test'
        })
    }
}));

describe('@blocks/actions/sendFingerprint', () => {
    afterEach(() => {
        jest.clearAllMocks();
    });
    it('should send fingerprint', async () => {
        const action = sendFingerprint();
        const dispatch = jest.fn();
        const getState = jest.fn().mockReturnValue({
            common: {
                yandexuid: 'qwe',
                uid: 123
            }
        });
        const data = {
            action: 'fingerprint',
            greedResult: JSON.stringify({test: 'test'}),
            yandexuid: 'qwe',
            uid: 123
        };

        await action(dispatch, getState);

        expect(api.log).toBeCalledWith(data, {encrypt: true});
    });
});
