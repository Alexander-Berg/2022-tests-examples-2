import {magicService} from '../magicService';

jest.useFakeTimers();

describe('AuthSilent', () => {
    describe('magicService', () => {
        let ajaxFn;
        const ajaxJest = jest.fn();

        beforeAll(() => {
            ajaxFn = global.$.ajax;
            global.$.ajax = ajaxJest;
        });
        afterAll(() => {
            global.$.ajax = ajaxFn;
        });
        beforeEach(() => {
            ajaxJest.mockReset();
        });
        it('Should call doneCallback with state when status = ok after start polling', () => {
            const responseState = 'testState';
            const doneCallback = jest.fn();

            ajaxJest.mockReturnValueOnce({done: jest.fn((cb) => cb({})), fail: jest.fn()});
            ajaxJest.mockReturnValueOnce({
                done: jest.fn((fn) => {
                    fn({status: 'ok', state: responseState});
                }),
                fail: jest.fn()
            });

            magicService.init({
                doneCallback,
                failCallback: jest.fn(),
                trackId: 'QWE',
                csrfToken: 'ASD'
            });
            magicService.start();
            jest.advanceTimersToNextTimer(2);

            expect(doneCallback).toBeCalledWith({status: 'ok', state: responseState});
        });
        it('Should call failCallback with error after start polling', () => {
            const responseError = 'someError';
            const failCallback = jest.fn();

            ajaxJest.mockReturnValueOnce({done: jest.fn((cb) => cb({})), fail: jest.fn()});
            ajaxJest.mockReturnValueOnce({
                done: jest.fn((fn) => {
                    fn({errors: [responseError]});
                }),
                fail: jest.fn()
            });

            magicService.init({
                doneCallback: jest.fn(),
                failCallback,
                trackId: 'QWE',
                csrfToken: 'ASD'
            });
            magicService.start();
            jest.advanceTimersToNextTimer(2);

            expect(failCallback).toBeCalledWith({errors: [responseError], error: responseError});
        });
        it('Should call failCallback with error = "global" after two fail poll', () => {
            const failCallback = jest.fn();

            ajaxJest.mockReturnValue({done: jest.fn(), fail: jest.fn((cb) => cb({}))});

            magicService.init({
                doneCallback: jest.fn(),
                failCallback,
                trackId: 'QWE',
                csrfToken: 'ASD'
            });
            magicService.start();
            jest.advanceTimersToNextTimer(4);

            expect(magicService.timeoutErrorCount).toEqual(3);
            expect(failCallback).toBeCalledWith({error: 'global'});
        });
        it('Should slowdown interval after long time', () => {
            const doneJest = jest.fn((cb) => cb({}));

            ajaxJest.mockReturnValue({done: doneJest, fail: jest.fn()});

            magicService.init({
                doneCallback: jest.fn(),
                failCallback: jest.fn(),
                trackId: 'QWE',
                csrfToken: 'ASD'
            });
            magicService.start();
            const startInterval = magicService.interval;

            jest.advanceTimersToNextTimer(200);
            expect(startInterval < magicService.interval).toEqual(true);
        });
        it('Should stop polling after call stop()', () => {
            const doneCallback = jest.fn();

            ajaxJest.mockReturnValue({done: jest.fn((cb) => cb({})), fail: jest.fn()});

            magicService.init({
                doneCallback,
                failCallback: jest.fn(),
                trackId: 'QWE',
                csrfToken: 'ASD'
            });
            magicService.start();
            magicService.stop();
            jest.advanceTimersToNextTimer(2);

            expect(doneCallback).not.toBeCalled();
        });
    });
});
