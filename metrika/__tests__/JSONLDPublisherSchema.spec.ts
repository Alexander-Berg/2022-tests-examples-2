/* eslint-disable max-lines */
import * as chai from 'chai';
import * as sinon from 'sinon';
import * as URLUtils from '@src/utils/url';
import * as timeUtils from '@src/utils/time';
import { JSDOMWrapper } from '@src/__tests__/utils/jsdom';
import * as domUtils from '@src/utils/dom';
import * as nativeFn from '@src/utils/function/isNativeFunction/isNativeFunction';
import {
    PUBLISHER_ARTICLE_TYPE,
    ContentItem,
    PUBLISHER_QA_TYPE,
    PUBLISHER_REVIEW_TYPE,
} from '../const';
import { JSONLDPublisherSchema } from '../JSONLDPublisherSchema';

describe('JSONLDPublisherSchema.js', () => {
    const nowMs = 11111102;
    const articleText = 'This text is not very long...'.repeat(30);

    let urlParaseStub: any = null;
    const sandbox = sinon.createSandbox();

    beforeEach(() => {
        sandbox
            .stub(domUtils, 'getInnerText')
            .callsFake((node?: HTMLElement | null) => {
                return node ? node.textContent || '' : '';
            });
        sandbox.stub(nativeFn, 'isNativeFunction').returns(true);
        sandbox.stub(timeUtils, 'getFromStart').returns(nowMs);
        urlParaseStub = sandbox.stub(URLUtils, 'parseUrl');
        urlParaseStub.callsFake((ctx: Window, url: string) => {
            let hash = url.split('#')[1];
            if (hash) {
                hash = `#${hash}`;
            }

            return {
                hash,
            };
        });
    });
    afterEach(() => {
        sandbox.restore();
    });
    const { window } = new JSDOMWrapper();
    const { document } = window;
    const schema = new JSONLDPublisherSchema(window, '');

    it('Parses simple articles', () => {
        const articleDescriptions = [
            {
                '@id': '1',
                '@context': 'schema.org',
                '@type': 'Article',
                author: { '@type': 'Person', name: 'Vasily Pupkin' },
                url: 'https://example.com/article/1#first-article',
                headline: "Vasily's guide to writing pointless articles",
                text: articleText,
                datePublished: '2018-12-11T08:56:49Z',
                dateModified: '2018-12-14T01:50:49Z',
                about: { '@type': 'Thing', name: 'Postmodern phylosophy' },
            },
            {
                '@id': '2',
                '@context': 'schema.org',
                '@type': 'Article',
                author: [
                    { '@type': 'Person', name: 'Vasily Pupkin' },
                    { '@type': 'Person', name: 'John Doe' },
                ],
            },
            {
                '@id': '3',
                '@context': 'schema.org',
                '@type': 'Article',
                author: { '@type': 'Person', name: 'Vasily Pupkin' },
                url: 'https://example.com/article/1',
                headline:
                    "Another Vasily's guide to writing pointless articles",
                datePublished: '2018-12-11T08:56:49Z',
                dateModified: '2018-12-14T01:50:49Z',
            },
            {
                '@id': '4',
                '@context': 'schema.org',
                '@type': 'Article',
                author: ['Vasily Pupkin', 'John Doe'],
                about: ['Postmodern phylosophy'],
            },
        ];
        document.body.innerHTML = `
            <script id="descr-1" type="application/ld+json">${JSON.stringify(
                articleDescriptions[0],
            )}</script>
            <script id="descr-2" type="application/ld+json">${JSON.stringify(
                articleDescriptions[1],
            )}</script>
            <link rel="canonical" href="https://example.com/pointless-articles-2-electric-boogaloo">
            <h1>Full body article</h1>
            <div id="first-article">
                <h1>Pointless article<h1/>
                <div>Some text from article node...</div>
            <div/>
            <div id="second-article">
                <script id="descr-3" type="application/ld+json">${JSON.stringify(
                    articleDescriptions[2],
                )}</script>
                <h1>Pointless article<h1/>
                <div>${articleText}</div>
            <div/>
            <div id="third-article">
                <script id="descr-4" type="application/ld+json">${JSON.stringify(
                    articleDescriptions[3],
                )}</script>
                <h1>Pointless article<h1/>
                <div>${articleText}</div>
            <div/>`;

        const result = schema.findContent();
        result.forEach((data: ContentItem) => {
            // eslint-disable-next-line no-param-reassign
            // @ts-expect-error
            delete data.update;
        });

        const firstArticle = document.querySelector('#first-article') as any;
        const secondArticle = document.querySelector('#second-article') as any;
        const thirdArticle = document.querySelector('#third-article') as any;
        const [descr1, descr2, descr3, descr4] = [1, 2, 3, 4].map((id) =>
            document.querySelector(`#descr-${id}`),
        );
        const { body } = document;

        const expected = [
            {
                sended: false,
                involvedTime: 0,
                contentElement: firstArticle,
                element: descr1,
                id: 873244444,
                chars: articleDescriptions[0].text!.length,
                authors: [
                    {
                        name: 'Vasily Pupkin',
                    },
                ],
                pageTitle: "Vasily's guide to writing pointless articles",
                updateDate: '2018-12-14T01:50:49Z',
                publicationDate: '2018-12-11T08:56:49Z',
                pageUrlCanonical: 'https://example.com/article/1#first-article',
                topics: [{ name: 'Postmodern phylosophy' }],
                rubric: [],
                stamp: nowMs,
                index: 1,
                type: PUBLISHER_ARTICLE_TYPE,
            },
            {
                sended: false,
                involvedTime: 0,
                id: 923577301,
                contentElement: body,
                element: descr2,
                chars: body.textContent!.length,
                authors: [
                    {
                        name: 'Vasily Pupkin',
                    },
                    {
                        name: 'John Doe',
                    },
                ],
                pageTitle: 'Full body article',
                updateDate: '',
                publicationDate: '',
                pageUrlCanonical:
                    'https://example.com/pointless-articles-2-electric-boogaloo',
                topics: [],
                rubric: [],
                stamp: nowMs,
                index: 2,
                type: PUBLISHER_ARTICLE_TYPE,
            },
            {
                sended: false,
                involvedTime: 0,
                id: 906799682,
                contentElement: secondArticle,
                element: descr3,
                chars: secondArticle.textContent!.length,
                authors: [
                    {
                        name: 'Vasily Pupkin',
                    },
                ],
                pageTitle:
                    "Another Vasily's guide to writing pointless articles",
                updateDate: '2018-12-14T01:50:49Z',
                publicationDate: '2018-12-11T08:56:49Z',
                pageUrlCanonical: 'https://example.com/article/1',
                topics: [],
                rubric: [],
                stamp: nowMs,
                index: 3,
                type: PUBLISHER_ARTICLE_TYPE,
            },
            {
                sended: false,
                involvedTime: 0,
                id: 822911587,
                contentElement: thirdArticle,
                element: descr4,
                chars: thirdArticle.textContent!.length,
                authors: [
                    {
                        name: 'Vasily Pupkin',
                    },
                    {
                        name: 'John Doe',
                    },
                ],
                pageTitle: 'Pointless article',
                updateDate: '',
                publicationDate: '',
                pageUrlCanonical:
                    'https://example.com/pointless-articles-2-electric-boogaloo',
                topics: [{ name: 'Postmodern phylosophy' }],
                rubric: [],
                stamp: nowMs,
                index: 4,
                type: PUBLISHER_ARTICLE_TYPE,
            },
        ];

        chai.expect(result).to.deep.equal(expected);
    });

    it('Parses review', () => {
        const articleDescriptions = [
            {
                '@context': 'schema.org',
                '@type': 'Review',
                author: { '@type': 'Person', name: 'Vasily Pupkin' },
                url: 'https://example.com/article/1#first-review',
                headline: "Vasily's review",
                text: articleText,
                datePublished: '2018-12-11T08:56:49Z',
                dateModified: '2018-12-14T01:50:49Z',
            },
        ];
        document.body.innerHTML = `<script id="review" type="application/ld+json">${JSON.stringify(
            articleDescriptions[0],
        )}</script>
            <link rel="canonical" href="https://example.com/pointless-articles-2-electric-boogaloo">`;

        const result = schema.findContent();
        result.forEach((data: ContentItem) => {
            // eslint-disable-next-line no-param-reassign
            // @ts-expect-error
            delete data.update;
        });

        const element = document.querySelector('#review') as any;
        const { body } = document;

        const expected = [
            {
                sended: false,
                involvedTime: 0,
                contentElement: body,
                element,
                id: 2428669374,
                chars: articleDescriptions[0].text!.length,
                authors: [
                    {
                        name: 'Vasily Pupkin',
                    },
                ],
                pageTitle: "Vasily Pupkin: Vasily's review",
                updateDate: '2018-12-14T01:50:49Z',
                publicationDate: '2018-12-11T08:56:49Z',
                pageUrlCanonical: 'https://example.com/article/1#first-review',
                topics: [],
                rubric: [],
                stamp: nowMs,
                index: 1,
                type: PUBLISHER_REVIEW_TYPE,
            },
        ];

        chai.expect(result).to.deep.equal(expected);
    });

    it('Parses @graph', () => {
        const articleDescriptions = {
            '@context': 'schema.org',
            '@graph': [
                {
                    '@id': '1',
                    '@context': 'schema.org',
                    '@type': 'Article',
                    author: { '@type': 'Person', name: 'Vasily Pupkin' },
                    url: 'https://example.com/article/1#first-article',
                    headline: "Vasily's guide to writing pointless articles",
                    text: articleText,
                    datePublished: '2018-12-11T08:56:49Z',
                    dateModified: '2018-12-14T01:50:49Z',
                    about: { '@type': 'Thing', name: 'Postmodern phylosophy' },
                },
                {
                    '@id': '2',
                    '@context': 'schema.org',
                    '@type': 'Article',
                    author: [
                        { '@type': 'Person', name: 'Vasily Pupkin' },
                        { '@type': 'Person', name: 'John Doe' },
                    ],
                },
                {
                    '@id': '3',
                    '@context': 'schema.org',
                    '@type': 'Article',
                    author: { '@type': 'Person', name: 'Vasily Pupkin' },
                    url: 'https://example.com/article/1#second-article',
                    headline:
                        "Another Vasily's guide to writing pointless articles",
                    datePublished: '2018-12-11T08:56:49Z',
                    dateModified: '2018-12-14T01:50:49Z',
                },
            ],
        };

        document.body.innerHTML = `
            <script id="descr" type="application/ld+json">${JSON.stringify(
                articleDescriptions,
            )}</script>
            <link rel="canonical" href="https://example.com/pointless-articles-2-electric-boogaloo">
            <h1>Full body article</h1>
            <div id="first-article">
                <h1>Pointless article<h1/>
                <div>Some text from article node...</div>
            <div/>
            <div id="second-article">
                <h1>Pointless article<h1/>
                <div>${articleText}</div>
            <div/>`;

        const firstArticle = document.querySelector('#first-article') as any;
        const secondArticle = document.querySelector('#second-article') as any;
        const descriptionsElement = document.querySelector('#descr') as any;

        const { body } = document;

        const result = schema.findContent();
        result.forEach((data: ContentItem) => {
            // eslint-disable-next-line no-param-reassign
            // @ts-expect-error
            delete data.update;
        });
        const expected = [
            {
                sended: false,
                involvedTime: 0,
                contentElement: firstArticle,
                element: descriptionsElement,
                id: 873244444,
                chars: articleDescriptions['@graph'][0].text!.length,
                authors: [
                    {
                        name: 'Vasily Pupkin',
                    },
                ],
                pageTitle: "Vasily's guide to writing pointless articles",
                updateDate: '2018-12-14T01:50:49Z',
                publicationDate: '2018-12-11T08:56:49Z',
                pageUrlCanonical: 'https://example.com/article/1#first-article',
                topics: [{ name: 'Postmodern phylosophy' }],
                rubric: [],
                stamp: nowMs,
                index: 1,
                type: PUBLISHER_ARTICLE_TYPE,
            },
            {
                sended: false,
                involvedTime: 0,
                id: 923577301,
                contentElement: body,
                element: descriptionsElement,
                chars: body.textContent!.length,
                authors: [
                    {
                        name: 'Vasily Pupkin',
                    },
                    {
                        name: 'John Doe',
                    },
                ],
                pageTitle: 'Full body article',
                updateDate: '',
                publicationDate: '',
                pageUrlCanonical:
                    'https://example.com/pointless-articles-2-electric-boogaloo',
                topics: [],
                rubric: [],
                stamp: nowMs,
                index: 2,
                type: PUBLISHER_ARTICLE_TYPE,
            },
            {
                sended: false,
                involvedTime: 0,
                id: 906799682,
                contentElement: secondArticle,
                element: descriptionsElement,
                chars: secondArticle.textContent!.length,
                authors: [
                    {
                        name: 'Vasily Pupkin',
                    },
                ],
                pageTitle:
                    "Another Vasily's guide to writing pointless articles",
                updateDate: '2018-12-14T01:50:49Z',
                publicationDate: '2018-12-11T08:56:49Z',
                pageUrlCanonical:
                    'https://example.com/article/1#second-article',
                topics: [],
                rubric: [],
                stamp: nowMs,
                index: 3,
                type: PUBLISHER_ARTICLE_TYPE,
            },
        ];

        chai.expect(result).to.deep.equal(expected);
    });

    it('Parses QAPage titles correctly', () => {
        const questionText = 'Question';
        const firstAuthor = 'Vasily Pupkin';
        const secondAuthor = 'John Doe';

        const firstAnswerText = 'Answer text answer text';
        const secondAnswerText = 'Answer text';

        const articleDescription = {
            '@context': 'schema.org',
            '@type': 'QAPage',
            mainEntityOfPage: {
                '@type': 'Question',
                '@context': 'schema.org',
                author: [{ name: 'John Doe' }, { name: 'Vasily Pupkin' }],
                headline: 'WUT?',
                text: questionText,
                acceptedAnswer: {
                    '@type': 'Answer',
                    text: firstAnswerText,
                    author: { name: firstAuthor },
                },
                suggestedAnswer: [
                    {
                        '@type': 'Answer',
                        text: firstAnswerText,
                        author: { name: firstAuthor },
                    },
                    {
                        '@type': 'Answer',
                        text: secondAnswerText,
                        author: { name: secondAuthor },
                    },
                ],
            },
        };

        document.body.innerHTML = `
            <script id="descr" type="application/ld+json">${JSON.stringify(
                articleDescription,
            )}</script>
            <link rel="canonical" href="https://example.com/pointless-articles-2-electric-boogaloo">
            <h1>Full body article</h1>
            <div id="first-article">
                <h1>Pointless article<h1/>
                <div>Some text from article node...</div>
            <div/>`;

        const descriptionElement = document.querySelector('#descr');
        const result = schema.findContent();
        result.forEach((data: ContentItem) => {
            // eslint-disable-next-line no-param-reassign
            // @ts-expect-error
            delete data.update;
        });
        const expected = [
            {
                sended: false,
                involvedTime: 0,
                id: 2697778090,
                contentElement: document.body,
                element: descriptionElement,
                chars: firstAnswerText.length,
                authors: [
                    {
                        name: firstAuthor,
                    },
                ],
                pageTitle: `${firstAuthor}: ${questionText}`,
                updateDate: '',
                publicationDate: '',
                pageUrlCanonical:
                    'https://example.com/pointless-articles-2-electric-boogaloo',
                topics: [],
                rubric: [],
                stamp: nowMs,
                index: 1,
                type: PUBLISHER_QA_TYPE,
            },
            {
                sended: false,
                involvedTime: 0,
                id: 3520834922,
                contentElement: document.body,
                element: descriptionElement,
                chars: secondAnswerText.length,
                authors: [
                    {
                        name: secondAuthor,
                    },
                ],
                pageTitle: `${secondAuthor}: ${questionText}`,
                updateDate: '',
                publicationDate: '',
                pageUrlCanonical:
                    'https://example.com/pointless-articles-2-electric-boogaloo',
                topics: [],
                rubric: [],
                stamp: nowMs,
                index: 2,
                type: PUBLISHER_QA_TYPE,
            },
        ];

        chai.expect(result).to.deep.equal(expected);
    });

    it('Parses rubrics', () => {
        const atricleDescriptions = [
            {
                '@id': '1',
                '@context': 'schema.org',
                '@type': 'Article',
                author: { '@type': 'Person', name: 'Vasily Pupkin' },
                headline: "Vasily's guide to writing pointless articles",
                text: articleText,
                datePublished: '2018-12-11T08:56:49Z',
                dateModified: '2018-12-14T01:50:49Z',
            },
            {
                '@id': '2',
                '@context': 'schema.org',
                '@type': 'Article',
                url: 'https://example.com#first-article',
                author: { '@type': 'Person', name: 'Vasily Pupkin' },
                headline: 'How to eat children and be happy',
                text: articleText,
                datePublished: '2018-12-11T08:56:49Z',
                dateModified: '2018-12-14T01:50:49Z',
            },
            {
                '@id': '3',
                '@context': 'schema.org',
                '@type': 'Article',
                url: 'https://example.com#first-article',
                author: { '@type': 'Person', name: 'Vasily Pupkin' },
                headline: 'This one is in the graph',
                text: articleText,
                datePublished: '2018-12-11T08:56:49Z',
                dateModified: '2018-12-14T01:50:49Z',
            },
        ];
        const breadcrumbsDescriptions = [
            {
                '@context': 'schema.org',
                '@type': 'BreadcrumbList',
                itemListElement: [
                    {
                        position: 1,
                        item: {
                            name: 'rubric one',
                        },
                    },
                    {
                        position: 2,
                        item: {
                            name: 'rubric two',
                        },
                    },
                ],
            },
            {
                '@context': 'schema.org',
                '@type': 'BreadcrumbList',
                itemListElement: [
                    {
                        position: 1,
                        item: {
                            name: 'ORA! ORA! ORA! ORA!',
                        },
                    },
                    {
                        position: 2,
                        item: {
                            name: 'Mandatory jojo reference',
                        },
                    },
                ],
            },
            {
                '@context': 'schema.org',
                '@type': 'BreadcrumbList',
                itemListElement: [
                    {
                        position: 1,
                        item: {
                            name: 'ZAWARUDOOOOOOO!!!!!!!!',
                        },
                    },
                    {
                        position: 2,
                        item: {
                            name: 'Mandatory jojo reference',
                        },
                    },
                ],
            },
        ];
        document.body.innerHTML = `
            <script id="descr-1" type="application/ld+json">${JSON.stringify(
                atricleDescriptions[0],
            )}</script>
            <script type="application/ld+json">${JSON.stringify(
                breadcrumbsDescriptions[0],
            )}</script>
            <link rel="canonical" href="https://example.com/pointless-articles-2-electric-boogaloo">
            <script id="descr-2" type="application/ld+json">${JSON.stringify({
                '@context': 'schema.org',
                '@graph': [atricleDescriptions[2], breadcrumbsDescriptions[2]],
            })}</script>
            <h1>Full body article</h1>
            <div id="first-article">
                <script type="application/ld+json">${JSON.stringify(
                    breadcrumbsDescriptions[1],
                )}</script>
                <script id="descr-3" type="application/ld+json">${JSON.stringify(
                    atricleDescriptions[1],
                )}</script>
                <h1>Pointless article<h1/>
                <div>Some text from article node...</div>
            <div/>
        `;
        const [descr1, descr2, descr3] = [1, 2, 3].map((id) =>
            document.querySelector(`#descr-${id}`),
        );
        const result = schema.findContent();
        result.forEach(function k(data) {
            // eslint-disable-next-line no-param-reassign
            // @ts-expect-error
            delete data.update;
        });
        const expected = [
            {
                sended: false,
                involvedTime: 0,
                contentElement: document.body,
                element: descr1,
                id: 873244444,
                chars: atricleDescriptions[0].text.length,
                authors: [
                    {
                        name: 'Vasily Pupkin',
                    },
                ],
                pageTitle: "Vasily's guide to writing pointless articles",
                updateDate: '2018-12-14T01:50:49Z',
                publicationDate: '2018-12-11T08:56:49Z',
                pageUrlCanonical:
                    'https://example.com/pointless-articles-2-electric-boogaloo',
                topics: [],
                rubric: [
                    { name: 'rubric one', position: 1 },
                    { name: 'rubric two', position: 2 },
                ],
                stamp: nowMs,
                index: 1,
                type: PUBLISHER_ARTICLE_TYPE,
            },
            {
                sended: false,
                involvedTime: 0,
                contentElement: document.querySelector('#first-article'),
                element: descr2,
                id: 906799682,
                chars: atricleDescriptions[2].text.length,
                authors: [
                    {
                        name: 'Vasily Pupkin',
                    },
                ],
                pageTitle: 'This one is in the graph',
                updateDate: '2018-12-14T01:50:49Z',
                publicationDate: '2018-12-11T08:56:49Z',
                pageUrlCanonical: 'https://example.com#first-article',
                topics: [],
                rubric: [
                    { name: 'ZAWARUDOOOOOOO!!!!!!!!', position: 1 },
                    { name: 'Mandatory jojo reference', position: 2 },
                ],
                stamp: nowMs,
                index: 2,
                type: PUBLISHER_ARTICLE_TYPE,
            },
            {
                sended: false,
                involvedTime: 0,
                contentElement: document.querySelector('#first-article'),
                element: descr3,
                id: 923577301,
                chars: atricleDescriptions[1].text.length,
                authors: [
                    {
                        name: 'Vasily Pupkin',
                    },
                ],
                pageTitle: 'How to eat children and be happy',
                updateDate: '2018-12-14T01:50:49Z',
                publicationDate: '2018-12-11T08:56:49Z',
                pageUrlCanonical: 'https://example.com#first-article',
                topics: [],
                rubric: [
                    { name: 'ORA! ORA! ORA! ORA!', position: 1 },
                    { name: 'Mandatory jojo reference', position: 2 },
                ],
                stamp: nowMs,
                index: 3,
                type: PUBLISHER_ARTICLE_TYPE,
            },
        ];

        chai.expect(result).to.deep.equal(expected);
    });

    it('Parses array in script tag', () => {
        const text =
            'В среду, 6 ноября, в Москве был побит температурный рекорд, зафиксированный в 1922 году. Температура воздуха составила плюс 12,1 градуса по Цельсию, как сообщает центр Фобос. В среду, 6 ноября, в Москве был побит температурный рекорд, зафиксированный в 1922 году. Температура воздуха составила плюс 12,1 градуса по Цельсию, как сообщает центр Фобос. В среду, 6 ноября, в Москве был побит температурный рекорд, зафиксированный в 1922 году. Температура воздуха составила плюс 12,1 градуса по Цельсию, как сообщает центр Фобос. В среду, 6 ноября, в Москве был побит температурный рекорд, зафиксированный в 1922 году. Температура воздуха составила плюс 12,1 градуса по Цельсию, как сообщает центр Фобос.';
        const arr = [
            {
                '@type': 'BreadcrumbList',
                itemListElement: [
                    {
                        '@type': 'ListItem',
                        position: 1,
                        item: {
                            '@id': '//example-news.ru/life',
                            name: 'Жизнь',
                        },
                    },
                    {
                        '@type': 'ListItem',
                        position: 2,
                        item: {
                            '@id': '//example-news.ru/life/weather',
                            name: 'Погода',
                        },
                    },
                ],
            },
            {
                '@type': 'NewsArticle',
                '@id': 'https://www.example-news.com/life/weather/moscow#cao',
                text,
                author: [{ '@type': 'Person', name: 'Иван Иванов' }],
                about: {
                    '@type': 'Event',
                    name: 'Москва',
                },
                url: 'https://www.example-news.com/life/weather/moscow#cao',
            },
        ];

        document.body.innerHTML = `
            <script id="script-el" type="application/ld+json">${JSON.stringify(
                arr,
            )}</script>
            <div>test</div>
        `;

        const result = schema.findContent();
        result.forEach((data: ContentItem) => {
            // eslint-disable-next-line no-param-reassign
            // @ts-expect-error
            delete data.update;
        });

        const expected = [
            {
                sended: false,
                involvedTime: 0,
                id: 1429240319,
                contentElement: document.body,
                chars: text.length,
                updateDate: '',
                publicationDate: '',
                pageTitle: undefined,
                authors: [
                    {
                        name: 'Иван Иванов',
                    },
                ],
                pageUrlCanonical:
                    'https://www.example-news.com/life/weather/moscow#cao',
                rubric: [
                    { name: 'Жизнь', position: 1 },
                    { name: 'Погода', position: 2 },
                ],
                topics: [{ name: 'Москва' }],
                stamp: nowMs,
                index: 1,
                type: PUBLISHER_ARTICLE_TYPE,
                element: document.querySelector('#script-el'),
            },
        ];

        chai.expect(result).to.deep.equal(expected);
    });
});
