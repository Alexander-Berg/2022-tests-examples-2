import {deepEqual} from '../../../../utils';

import * as extracted from '../mails_block.js';

jest.mock('../../../../utils', () => ({
    deepEqual: jest.fn((objA, objB) => objA === objB)
}));

describe('Morda.MailsBlock', () => {
    let obj = null;

    beforeEach(() => {
        obj = {
            props: {
                emails: {
                    emails: {}
                }
            }
        };
    });
    afterEach(() => {
        deepEqual.mockClear();
    });
    describe('processEmails', () => {
        test('if it works correctly', () => {
            const emails = {
                forRestoreConfirmed: {
                    category: 'for_restore',
                    confirmed: true
                },
                forRestoreUnconfirmed: {
                    category: 'for_restore',
                    confirmed: false
                },
                forNotifications: {
                    category: 'for_notifications'
                },
                native: {
                    category: 'native'
                },
                mative: {
                    category: 'native'
                },
                other: {
                    category: 'other'
                },
                lol: {
                    category: 'lol'
                },
                rpop: {
                    category: 'rpop'
                }
            };

            expect(extracted.processEmails(emails)).toEqual({
                forRestore: [
                    {
                        category: 'for_restore',
                        confirmed: true,
                        name: 'forRestoreConfirmed'
                    },
                    {
                        category: 'for_restore',
                        confirmed: false,
                        name: 'forRestoreUnconfirmed'
                    }
                ],
                forRestoreConfirmed: [
                    {
                        category: 'for_restore',
                        confirmed: true,
                        name: 'forRestoreConfirmed'
                    }
                ],
                forRestoreUnconfirmed: [
                    {
                        category: 'for_restore',
                        confirmed: false,
                        name: 'forRestoreUnconfirmed'
                    }
                ],
                forNotifications: [
                    {
                        category: 'for_notifications',
                        name: 'forNotifications'
                    }
                ],
                other: [
                    {
                        category: 'other',
                        name: 'other'
                    },
                    {
                        category: 'lol',
                        name: 'lol'
                    }
                ],
                native: [
                    {
                        category: 'native',
                        name: 'native'
                    },
                    {
                        category: 'native',
                        name: 'mative'
                    }
                ],
                rpop: [
                    {
                        category: 'rpop',
                        name: 'rpop'
                    }
                ],
                hasEmails: true,
                hasNoNative: true
            });
        });
    });
    describe('setProcessedEmails', () => {
        it('should have emails object', () => {
            extracted.setProcessedEmails.call(obj, {
                emails: {}
            });
            expect(typeof obj.emails).toBe('object');
        });
        it('should have undefined emails', () => {
            extracted.setProcessedEmails.call(obj, obj.props);
            expect(typeof obj.emails).toBe('undefined');
        });
        it('should fallback on empty object', () => {
            delete obj.props.emails.emails;
            extracted.setProcessedEmails.call(obj, {
                emails: {}
            });
            expect(obj.emails).toEqual(extracted.processEmails({}));
        });
    });
    describe('construct', () => {
        it('should have emails object', () => {
            extracted.construct.call(obj, obj.props);
            expect(typeof obj.emails).toBe('object');
        });
        it('should fallback on empty object', () => {
            delete obj.props.emails.emails;
            extracted.construct.call(obj, obj.props);
            expect(obj.emails).toEqual(extracted.processEmails({}));
        });
    });
});
