import {redirect} from '@blocks/authv2/actions';
import startSocialAuth from '../startSocialAuth';
import broker from '../../broker';

jest.mock('../../broker', () => ({
    start: jest.fn()
}));
jest.mock('@blocks/authv2/actions', () => ({
    redirect: jest.fn()
}));

describe('Actions: startSocialAuth', () => {
    describe('success cases', () => {
        afterEach(() => {
            broker.start.mockClear();
        });

        it('should send social auth with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    track_id: 'track'
                }
            }));

            const params = {
                provider: 'provder'
            };

            startSocialAuth(params)(dispatch, getState);

            expect(broker.start).toBeCalled();
            expect(broker.start).toBeCalledWith({
                track_id: 'track',
                provider: params.provider
            });
        });

        it('should send social auth with valid params and additional data', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    track_id: 'track'
                }
            }));

            const params = {
                provider: 'provder',
                scope: 'scope'
            };

            startSocialAuth(params)(dispatch, getState);

            expect(broker.start).toBeCalled();
            expect(broker.start).toBeCalledWith({
                track_id: 'track',
                provider: params.provider,
                scope: params.scope
            });
        });
        it('Should redirect for autoRu', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    track_id: 'track'
                },
                customs: {
                    autoRuButton: {
                        link: 'https://auto.ru'
                    }
                }
            }));

            const params = {
                provider: 'autoRu',
                scope: 'scope'
            };

            startSocialAuth(params)(dispatch, getState);

            expect(redirect).toBeCalledWith('https://auto.ru');
        });
    });
});
