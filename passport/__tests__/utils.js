import {persistSyntheticEvent} from '@blocks/utils';

describe('@blocks', () => {
    describe('utils', () => {
        describe('persistSyntheticEvent', () => {
            it('should call persist method before original function', () => {
                const funcMock = jest.fn();
                const eventMock = {
                    persist: jest.fn()
                };

                persistSyntheticEvent(funcMock)(eventMock);
                const persistOrder = eventMock.persist.mock.invocationCallOrder[0];
                const funcMockOrder = funcMock.mock.invocationCallOrder[0];

                expect(persistOrder).toBeLessThan(funcMockOrder);
                // expect(eventMock.persist).toHaveBeenCalledBefore(funcMock);
            });
        });
    });
});
