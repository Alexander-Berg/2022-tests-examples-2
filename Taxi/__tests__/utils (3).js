import {createMessagesLinks} from '../utils';

describe('utils', () => {
    describe('createMessagesLinks', () => {
        test('create links', () => {
            const participants = [
                {
                    id: 'bizarre',
                    role: 'support',
                    avatar_url: '5',
                    nickname: 'Служба поддержки'
                },
                {
                    id: '5c3f2366254e5eb96a2b056c',
                    role: 'driver'
                }
            ];

            const messages = [
                {
                    id: '1',
                    text: 'сообщение без ссылок',
                    metadata: {
                        reply_to: ['unexisted', 'unexisted'],
                        created: '2019-07-04T14:37:26+0000'
                    },
                    sender: {
                        id: 'bizarre',
                        role: 'support'
                    }
                },
                {
                    id: '2',
                    text: 'сообщение на которое ответили 2 раза',
                    metadata: {
                        reply_to: [],
                        created: '2019-07-04T14:37:26+0000'
                    },
                    sender: {
                        id: '5c3f2366254e5eb96a2b056c',
                        role: 'driver'
                    }
                },
                {
                    id: '3',
                    text: 'первый ответ на сообщение 2',
                    metadata: {
                        reply_to: ['2'],
                        created: '2019-07-04T14:37:26+0000'
                    },
                    sender: {
                        id: 'bizarre',
                        role: 'support'
                    }
                },
                {
                    id: '4',
                    text: 'второй ответ на сообщение 2',
                    metadata: {
                        reply_to: ['2'],
                        created: '2019-07-04T14:37:26+0000'
                    },
                    sender: {
                        id: 'bizarre',
                        role: 'support'
                    }
                }
            ];

            expect(createMessagesLinks(messages, participants)).toEqual({
                '1': {
                    replyTo: []
                },
                '2': {
                    replyTo: [],
                    repliedBy: [
                        {
                            id: '3',
                            text: 'первый ответ на сообщение 2',
                            sender: 'Служба поддержки'
                        },
                        {
                            id: '4',
                            text: 'второй ответ на сообщение 2',
                            sender: 'Служба поддержки'
                        }
                    ]
                },
                '3': {
                    replyTo: [
                        {
                            id: '2',
                            text: 'сообщение на которое ответили 2 раза',
                            sender: undefined
                        }
                    ]
                },
                '4': {
                    replyTo: [
                        {
                            id: '2',
                            text: 'сообщение на которое ответили 2 раза',
                            sender: undefined
                        }
                    ]
                }
            });
        });
    });
});
