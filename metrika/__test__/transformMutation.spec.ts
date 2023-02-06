import chai from 'chai';
import {
    ATTR_CHANGE_EVENT_NAME,
    NODE_REMOVE_EVENT_NAME,
    TEXT_CHANGE_EVENT_NAME,
    NODE_ADD_EVENT_NAME,
} from '@private/src/providers/webvisor2/recorder/captors/MutationsCaptor/MutationsCaptor';
import { transformMutation } from '../transformMutation';

describe('mutation transformer', () => {
    it('transforms change attributes mutation', () => {
        const mutation = {
            stamp: 100,
            frameId: 0,
            event: ATTR_CHANGE_EVENT_NAME,
            data: {
                index: 1,
                target: 1,
                attributes: {
                    id: '123',
                    woop: 'a',
                    ass: null,
                },
            },
        } as any;
        const result = transformMutation(mutation);

        chai.expect({
            type: 'mutation',
            stamp: 100,
            data: {
                frameId: 0,
                meta: {
                    index: 1,
                    changes: [
                        {
                            c: [
                                {
                                    id: 1,
                                    i: 1,
                                    at: {
                                        id: {
                                            o: '',
                                            n: '123',
                                            r: false,
                                        },
                                        woop: {
                                            o: '',
                                            n: 'a',
                                            r: false,
                                        },
                                        ass: {
                                            o: '',
                                            n: null,
                                            r: true,
                                        },
                                    },
                                },
                            ],
                        },
                    ],
                },
            },
        }).to.deep.equal(result);
    });

    it('transforms node remove mutation', () => {
        const mutation = {
            frameId: 0,
            stamp: 100,
            event: NODE_REMOVE_EVENT_NAME,
            data: {
                index: 1,
                nodes: [1, 2, 3, 4],
            },
        } as any;

        const result = transformMutation(mutation);
        chai.expect({
            type: 'mutation',
            stamp: 100,
            data: {
                frameId: 0,
                meta: {
                    index: 1,
                    changes: [
                        {
                            a: [
                                {
                                    id: 1,
                                    i: 1,
                                },
                                {
                                    id: 2,
                                    i: 1,
                                },
                                {
                                    id: 3,
                                    i: 1,
                                },
                                {
                                    id: 4,
                                    i: 1,
                                },
                            ],
                        },
                    ],
                },
            },
        }).to.deep.equal(result);
    });

    it('transforms node add mutation', () => {
        const mutation = {
            stamp: 100,
            event: NODE_ADD_EVENT_NAME,
            type: 'mutation',
            frameId: 0,
            data: {
                index: 1,
                nodes: [
                    {
                        id: 100,
                        name: 'div',
                        attributes: {
                            class: 'c1',
                            id: 'id1',
                        },
                        namespace: 'some namespace',
                        content: 'content',
                        parent: '123',
                        prev: 122,
                        next: 125,
                        hidden: true,
                    },
                ],
                target: 124,
            },
        } as any;

        const result = transformMutation(mutation);
        chai.expect({
            type: 'mutation',
            stamp: 100,
            data: {
                frameId: 0,
                meta: {
                    index: 1,
                    changes: [
                        {
                            b: [
                                {
                                    id: 100,
                                    nm: 'div',
                                    ns: 'some namespace',
                                    at: {
                                        class: 'c1',
                                        id: 'id1',
                                    },
                                    ct: 'content',
                                    pa: '123',
                                    pr: 122,
                                    nx: 125,
                                    i: 1,
                                    h: true,
                                },
                            ],
                        },
                    ],
                },
            },
        }).to.deep.equal(result);
    });

    it('transforms text content change mutation', () => {
        const mutation = {
            stamp: 100,
            frameId: 0,
            event: TEXT_CHANGE_EVENT_NAME,
            data: {
                index: 1,
                target: 1,
                value: 'new text',
            },
        } as any;

        const result = transformMutation(mutation);
        chai.expect({
            type: 'mutation',
            stamp: 100,
            data: {
                frameId: 0,
                meta: {
                    index: 1,
                    changes: [
                        {
                            d: [
                                {
                                    id: 1,
                                    ct: {
                                        o: '',
                                        n: 'new text',
                                    },
                                    i: 1,
                                },
                            ],
                        },
                    ],
                },
            },
        }).to.deep.equal(result);
    });
});
