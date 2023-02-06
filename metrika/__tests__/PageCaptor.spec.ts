import * as chai from 'chai';
import * as sinon from 'sinon';
import * as dom from '@src/utils/dom';
import * as locationUtils from '@src/utils/location';
import { PAGE_EVENT_TYPE } from '../../AbstractCaptor/AbstractCaptor';
import { PageCaptor } from '../PageCaptor';

describe('PageCaptor', () => {
    const sandbox = sinon.createSandbox();
    const location = {
        host: 'example.com',
        protocol: 'https',
        pathname: '/some-path',
    };

    beforeEach(() => {
        sandbox.stub(locationUtils, 'getLocation').returns(location as any);
        sandbox.stub(dom, 'getViewportSize').returns([100, 100]);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('Captures page', () => {
        const ctx = {
            document: {
                title: 'title',
                referrer: 'referrer',
                documentElement: {
                    something: 'something',
                },
            },
            navigator: {
                userAgent: 'ie6',
            },
            screen: {
                height: 1024,
                width: 768,
            },
            location: {
                href: 'https://example.com/some-path#123?id=123',
            },
        } as any;

        const indexerNodesAdd = sinon.stub();
        const sendEventObject = sinon.stub();

        const recorder = {
            getPageInfo: () => ({
                getBase: () => 'base',
                getDoctype: () => 'doctype',
                getTabId: () => 'tabid',
            }),
            getRecordStamp: () => 100,
            getIndexer: () => ({
                handleNodesAdd: indexerNodesAdd,
            }),
            getEventWrapper: () => ({}),
            sendEventObject,
        } as any;

        const content = [
            {
                name: 'div',
                id: 123,
                attributes: {
                    a: '1',
                    b: '2',
                },
                node: 'this should be removed',
            },
        ];

        const pageCaptor = new PageCaptor(ctx, recorder, 'a');
        pageCaptor.start();

        const [{ nodes, sendResult }] = indexerNodesAdd.getCall(0).args;
        chai.expect(nodes).to.deep.equal([ctx.document.documentElement]);

        sendResult(content);
        const [type, data, event, stamp] = sendEventObject.getCall(0).args;
        chai.expect(type).to.equal(PAGE_EVENT_TYPE);
        chai.expect(event).to.equal(PAGE_EVENT_TYPE);
        chai.expect(stamp).to.equal(0);
        chai.expect({
            content: [
                {
                    name: 'div',
                    id: 123,
                    attributes: {
                        a: '1',
                        b: '2',
                    },
                },
            ],
            base: 'base',
            hasBase: true,
            viewport: {
                height: 100,
                width: 100,
            },
            title: 'title',
            doctype: 'doctype',
            address: 'https://example.com/some-path#123?id=123',
            ua: 'ie6',
            referrer: 'referrer',
            screen: {
                width: 768,
                height: 1024,
            },
            location: {
                host: 'example.com',
                protocol: 'https',
                path: '/some-path',
            },
            recordStamp: 100,
            tabId: 'tabid',
        }).to.deep.equal(data);
    });
});
