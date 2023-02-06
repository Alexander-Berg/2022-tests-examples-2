import * as chai from 'chai';
import * as sinon from 'sinon';
import * as timeUtils from '@src/utils/time';
import { JSDOMWrapper } from '@src/__tests__/utils/jsdom';
import * as domUtils from '@src/utils/dom';
import { PUBLISHER_ARTICLE_TYPE, ContentItem } from '../const';
import { OpengraphPublisherSchema } from '../OpengraphPublisherSchema';

const nowMs = 11111102;

describe('OpengraphPublisherSchema.ts', () => {
    const text = 'Content, sort of...'.repeat(30);
    const { window } = new JSDOMWrapper();
    const { document } = window;
    const schema = new OpengraphPublisherSchema!(window, '');
    const sandbox = sinon.createSandbox();

    beforeEach(() => {
        // jsdom
        sandbox
            .stub(domUtils, 'getInnerText')
            .callsFake((node?: HTMLElement | null) => {
                return node ? node.textContent || '' : '';
            });
        sandbox.stub(timeUtils, 'getFromStart').returns(nowMs);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('Parses articles', () => {
        document.head.innerHTML = `<meta property="og:type" content="article">
            <meta property="og:author" content="John Doe">
            <meta property="og:author" content="Jack Shit">
            <meta property="og:title" content="Some inconsequential article">
            <meta property="og:modified_time" content="2018-12-11T08:56:49Z">
            <meta property="og:published_time" content="2018-12-09T08:56:49Z">
            <meta property="og:url" content="https://example.com/artcicle-example">
            <meta property="og:tag" content="tag1">
            <meta property="og:tag" content="tag2">
            <meta property="og:section" content="Beeing generally useless">
            <meta property="og:section" content="Inernet garbage">`;
        document.body.innerHTML = `<link rel="canonical" href="https://example.com/pointless-articles-2-electric-boogaloo">
            <div id="second-articele">
              <h1>Another useless article</h1>
              <div>${text}</div>
              <meta property="og:type" content="article">
              <meta property="og:tag" content="tag1">
              <meta property="og:author" content="Jack Shit">
              <meta property="og:modified_time" content="2018-12-11T08:56:49Z">
              <meta property="og:published_time" content="2018-12-09T08:56:49Z">
              <meta property="og:section" content="Inernet garbage">
            </div>`;
        const result = schema.findContent();
        result.forEach((data: ContentItem) => {
            // eslint-disable-next-line no-param-reassign
            // @ts-expect-error
            delete data.update;
        });

        const { body } = document;
        const secondArticle = document.querySelector('#second-articele') as any;
        const descrElemBody = document.body.querySelector('meta');

        const expected = [
            {
                contentElement: body,
                element: document.head,
                sended: false,
                involvedTime: 0,
                chars: body.textContent!.length,
                authors: [
                    {
                        name: 'John Doe',
                    },
                    {
                        name: 'Jack Shit',
                    },
                ],
                topics: [
                    {
                        name: 'tag1',
                    },
                    {
                        name: 'tag2',
                    },
                ],
                pageTitle: 'Some inconsequential article',
                updateDate: '2018-12-11T08:56:49Z',
                publicationDate: '2018-12-09T08:56:49Z',
                pageUrlCanonical: 'https://example.com/artcicle-example',
                rubric: [
                    {
                        name: 'Beeing generally useless',
                    },
                    {
                        name: 'Inernet garbage',
                    },
                ],
                stamp: nowMs,
                id: 4040331233,
                index: 1,
                type: PUBLISHER_ARTICLE_TYPE,
            },
            {
                contentElement: secondArticle,
                element: descrElemBody,
                sended: false,
                involvedTime: 0,
                chars: secondArticle.textContent.length,
                authors: [
                    {
                        name: 'Jack Shit',
                    },
                ],
                topics: [
                    {
                        name: 'tag1',
                    },
                ],
                pageTitle: 'Another useless article',
                updateDate: '2018-12-11T08:56:49Z',
                publicationDate: '2018-12-09T08:56:49Z',
                pageUrlCanonical:
                    'https://example.com/pointless-articles-2-electric-boogaloo',
                rubric: [
                    {
                        name: 'Inernet garbage',
                    },
                ],
                stamp: nowMs,
                id: 3958097156,
                index: 2,
                type: PUBLISHER_ARTICLE_TYPE,
            },
        ];

        chai.expect(result).to.deep.equal(expected);
    });
    it('Parses articles with og:article/article: prefixes', () => {
        document.head.innerHTML = '';
        document.body.innerHTML = `<div id="articele">
            <h1>Another useless article</h1>
            <div>${text}</div>
            <meta property="og:type" content="article">
            <meta property="og:article:tag" content="tag1">
            <meta property="article:author" content="Jack Shit">
            <meta property="article:modified_time" content="2018-12-11T08:56:49Z">
            <meta property="og:published_time" content="2018-12-09T08:56:49Z">
            <meta property="og:section" content="Inernet garbage">
        </div>`;
        const descrElem = document.body.querySelector('meta');
        const article = document.querySelector('#articele') as any;

        const result = schema.findContent();
        result.forEach((data: ContentItem) => {
            // eslint-disable-next-line no-param-reassign
            // @ts-expect-error
            delete data.update;
        });
        const expected = [
            {
                contentElement: article,
                element: descrElem,
                sended: false,
                involvedTime: 0,
                chars: article.textContent.length,
                authors: [
                    {
                        name: 'Jack Shit',
                    },
                ],
                topics: [
                    {
                        name: 'tag1',
                    },
                ],
                pageUrlCanonical: undefined,
                pageTitle: 'Another useless article',
                updateDate: '2018-12-11T08:56:49Z',
                publicationDate: '2018-12-09T08:56:49Z',
                rubric: [
                    {
                        name: 'Inernet garbage',
                    },
                ],
                stamp: nowMs,
                id: 3958097156,
                index: 1,
                type: PUBLISHER_ARTICLE_TYPE,
            },
        ];
        chai.expect(result).to.deep.equal(expected);
    });
});
