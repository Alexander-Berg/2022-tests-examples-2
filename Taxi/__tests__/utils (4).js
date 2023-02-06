import {mergeChatContent, createChatMode, needScrollAfterUpdate} from '../utils';
import {CHAT_MODE} from '../consts';

describe('utils', () => {
    describe('mergeChatContent', () => {
        const current = {
            messages: ['current'],
            attribute: 'current'
        };

        test('when data to update not exists', () => {
            expect(mergeChatContent(current, undefined)).toBe(undefined);
        });

        test('when data to update exists', () => {
            const update = {
                messages: ['update'],
                attribute: 'update'
            };

            expect(mergeChatContent(current, update)).toEqual({
                messages: ['current', 'update'],
                attribute: 'update'
            });
        });
    });

    describe('createChatMode', () => {
        test('when data not exists', () => {
            expect(createChatMode()).toBe(CHAT_MODE.EMPTY);
        });

        test('rate', () => {
            expect(createChatMode({status: {ask_csat: true}})).toBe(CHAT_MODE.RATE);
        });

        test('opened', () => {
            expect(createChatMode({status: {is_open: true}})).toBe(CHAT_MODE.OPENED);
        });

        test('closed', () => {
            expect(createChatMode({status: {is_open: false}})).toBe(CHAT_MODE.CLOSED);
        });
    });

    describe('needScrollAfterUpdate', () => {
        test('false', () => {
            expect(
                needScrollAfterUpdate(
                    {
                        data: {
                            messages: ['current']
                        }
                    },
                    {
                        data: {
                            messages: ['current']
                        }
                    }
                )
            ).toBe(false);
        });

        test('true', () => {
            expect(
                needScrollAfterUpdate(
                    {
                        data: {
                            messages: ['current']
                        }
                    },
                    {
                        data: {
                            messages: ['current', 'new']
                        }
                    }
                )
            ).toBe(true);

            expect(
                needScrollAfterUpdate(
                    {
                        data: {
                            messages: ['current']
                        },
                        mode: CHAT_MODE.OPENED
                    },
                    {
                        data: {
                            messages: ['current']
                        },
                        mode: CHAT_MODE.RATE
                    }
                )
            ).toBe(true);
        });
    });
});
