import * as chai from 'chai';
import { transformPage } from '../transformPage';

describe('transform page', () => {
    it('transforms page', () => {
        const page = {
            stamp: 0,
            frameId: 0,
            data: {
                content: [
                    {
                        id: 100,
                        name: 'div',
                        attributes: {
                            class: 'c1',
                            id: 'id1',
                        },
                        content: 'content',
                        parent: 123,
                        prev: 122,
                        next: 125,
                    },
                ],
                base: 'base',
                hasBase: true,
                viewport: { height: 100, width: 100 },
                title: 'my page',
                doctype: 'thml',
                address: 'http://example.com/gay',
                ua: 'netscape',
                referrer: 'http://example2.com',
                screen: {
                    width: 10,
                    height: 20,
                },
                location: {
                    host: 'example.com',
                    protocol: 'http',
                    path: 'gay',
                },
                recordStamp: 123134,
                tabId: 'some-guid',
            },
        } as any;
        const result = transformPage(page);

        chai.expect({
            type: 'page',
            data: {
                content: [
                    {
                        id: 100,
                        name: 'div',
                        attributes: {
                            class: 'c1',
                            id: 'id1',
                        },
                        content: 'content',
                        parent: 123,
                        prev: 122,
                        next: 125,
                    },
                ],
                frameId: 0,
                recordStamp: 123134,
                tabId: 'some-guid',
                meta: {
                    base: 'base',
                    hasBase: true,
                    viewport: {
                        height: 100,
                        width: 100,
                    },
                    title: 'my page',
                    doctype: 'thml',
                    address: 'http://example.com/gay',
                    ua: 'netscape',
                    referrer: 'http://example2.com',
                    screen: {
                        width: 10,
                        height: 20,
                    },
                    location: {
                        host: 'example.com',
                        protocol: 'http',
                        path: 'gay',
                    },
                },
            },
        }).to.deep.equal(result);
    });
});
