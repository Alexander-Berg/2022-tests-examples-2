import {NativeMobileApiTransport} from '../NativeMobileApiTransport';

let transport;

let mockPostMessage;

describe('NativeMobileApiTransport', () => {
    beforeEach(() => {
        mockPostMessage = jest.fn();

        window.webkit = {
            messageHandlers: {
                nativeAM: {
                    postMessage: mockPostMessage
                }
            }
        };

        transport = new NativeMobileApiTransport(0, 'ios', {});
    });

    it('shpuld send message once', () => {
        transport.sendMessageToNativeApiOnce('test', {});
        transport.sendMessageToNativeApiOnce('test', {});
        transport.sendMessageToNativeApiOnce('test', {});

        expect(mockPostMessage).toBeCalledTimes(1);
        expect(mockPostMessage).toBeCalledWith(
            expect.objectContaining({
                message: 'test'
            })
        );
    });
});
