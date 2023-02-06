import * as chai from 'chai';
import * as sinon from 'sinon';
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
import { MicrodataPublisherSchema } from '../MicrodataPublisherSchema';

describe('MicrodataPublisherSchema.js', () => {
    const nowMs = 11111102;
    const { window } = new JSDOMWrapper();
    const { document } = window;
    const schema = new MicrodataPublisherSchema!(window, '');
    const sandbox = sinon.createSandbox();

    beforeEach(() => {
        // jsdom
        sandbox
            .stub(domUtils, 'getInnerText')
            .callsFake((node?: HTMLElement | null) => {
                return node ? node.textContent || '' : '';
            });
        sandbox.stub(nativeFn, 'isNativeFunction').returns(true);
        sandbox.stub(timeUtils, 'getFromStart').returns(nowMs);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('Parses articles', () => {
        document.body.innerHTML = `<link rel="canonical" href="https://example.com/pointless-articles-2-electric-boogaloo">
            <div id="article" itemtype="http://schema.org/Article">
              <div itemtype="http://schema.org/BreadcrumbList">
                <div itemprop="itemListElement" itemtype="http://schema.org/ListItem">
                  <meta itemprop="name" content="DRIVE2"/>
                  <link itemprop="item" href="https://www.drive2.ru/">
                  <meta itemprop="position" content="1"/>
                </div>
                <div itemprop="itemListElement" itemtype="http://schema.org/ListItem">
                  <meta itemprop="name" content="ZHOPA"/>
                  <link itemprop="item" href="https://www.drive2.ru/ZHOPA">
                  <meta itemprop="position" content="2"/>
                </div>
              </div>
              <h1 itemprop="headline">How to drive</h1>
              <div itemprop="author" itemtype="http://schema.org/Person">
                <div itemprop="name" >Vasily Pupkin</div>
              </div>
              <div itemprop="author" itemtype="http://schema.org/Person">
                <div itemprop="name">John Doe</div>
              </div>
              <div itemprop="datePublished">2018-12-14T01:50:49Z</div>
              <div itemprop="dateModified">2018-12-11T08:56:49Z</div>
              <div itemprop="about">DRIVING! FOR GOD'S SAKE THIS SITE CALLED DRIVE2! WHAT ELSE THIS SHIT IS ABOUT!?</div>
              <div id="article-body" itemprop="articleBody">
                ${"You just DO IT! JUST DO IT! DON'T LET YOUR DREAMS BE DREAMS! JUST DO IT!".repeat(
                    10,
                )}
              </div>
            </div>`;
        const result = schema.findContent();
        result.forEach((data: ContentItem) => {
            // eslint-disable-next-line no-param-reassign
            // @ts-expect-error
            delete data.update;
        });

        const firstArticle = document.querySelector('#article') as any;
        const articleBody = document.querySelector('#article-body') as any;

        const expected = [
            {
                sended: false,
                involvedTime: 0,
                id: 2662746106,
                contentElement: firstArticle,
                element: firstArticle,
                chars: articleBody.textContent!.length,
                topics: [
                    {
                        name: "DRIVING! FOR GOD'S SAKE THIS SITE CALLED DRIVE2! WHAT ELSE THIS SHIT IS ABOUT!?",
                    },
                ],
                rubric: [
                    {
                        name: 'DRIVE2',
                        position: '1',
                    },
                    {
                        name: 'ZHOPA',
                        position: '2',
                    },
                ],
                updateDate: '2018-12-11T08:56:49Z',
                publicationDate: '2018-12-14T01:50:49Z',
                pageUrlCanonical:
                    'https://example.com/pointless-articles-2-electric-boogaloo',
                pageTitle: 'How to drive',
                authors: [
                    {
                        name: 'Vasily Pupkin',
                    },
                    {
                        name: 'John Doe',
                    },
                ],
                stamp: nowMs,
                index: 1,
                type: PUBLISHER_ARTICLE_TYPE,
            },
        ];

        chai.expect(result).to.deep.equal(expected);
    });
    it('Parses QAPage', () => {
        document.body.innerHTML = `<link rel="canonical" href="https://example.com/pointless-articles-2-electric-boogaloo">
            <div itemtype="http://schema.org/QAPage">
              <div itemprop="mainEntityOfPage" itemtype="http://schema.org/Question">
                <h1 itemprop="headline">Question title</h1>
                <div itemprop="text">Question</div>
                <div itemprop="author" itemtype="http://schema.org/Person">
                  <div itemprop="name">Vasily Pupkin</div>
                </div>
                <div id="answer" itemprop="suggestedAnswer acceptedAnswer" itemscope itemtype="http://schema.org/Answer">
                    <div itemprop="text">Answer text answer text</div>
                    <div itemprop="author" itemscope itemtype="http://schema.org/Person">
                        <span itemprop="name">Vasily Pupkin</span>
                    </div>
                </div>
              </div>
            </div>`;
        const result = schema.findContent();
        result.forEach((data: ContentItem) => {
            // eslint-disable-next-line no-param-reassign
            // @ts-expect-error
            delete data.update;
        });

        const answer = document.querySelector('#answer') as any;

        const expected = [
            {
                sended: false,
                involvedTime: 0,
                id: 2697778090,
                contentElement: answer,
                element: answer,
                chars: 23,
                topics: [],
                rubric: [],
                updateDate: '',
                publicationDate: '',
                pageUrlCanonical:
                    'https://example.com/pointless-articles-2-electric-boogaloo',
                pageTitle: 'Vasily Pupkin: Question',
                authors: [
                    {
                        name: 'Vasily Pupkin',
                    },
                ],
                stamp: nowMs,
                index: 1,
                type: PUBLISHER_QA_TYPE,
            },
        ];

        chai.expect(result).to.deep.equal(expected);
    });
    it('Parses review', () => {
        document.body.innerHTML = `<link rel="canonical" href="https://example.com/pointless-articles-2-electric-boogaloo">
            <div id="review" itemtype="http://schema.org/Review">
              <h1 itemprop="headline">Vasily's review</h1>
              <div itemprop="author" itemtype="http://schema.org/Person">
                <div itemprop="name" >Vasily Pupkin</div>
              </div>
              <div itemprop="datePublished">2018-12-14T01:50:49Z</div>
              <div itemprop="dateModified">2018-12-11T08:56:49Z</div>
              <div id="review-body" itemprop="articleBody">
                ${"You just DO IT! JUST DO IT! DON'T LET YOUR DREAMS BE DREAMS! JUST DO IT!".repeat(
                    10,
                )}
              </div>
            </div>`;
        const result = schema.findContent();
        result.forEach((data: ContentItem) => {
            // eslint-disable-next-line no-param-reassign
            // @ts-expect-error
            delete data.update;
        });

        const review = document.querySelector('#review') as any;
        const reviewBody = document.querySelector('#review-body') as any;

        const expected = [
            {
                sended: false,
                involvedTime: 0,
                id: 2428669374,
                contentElement: review,
                element: review,
                chars: reviewBody.textContent!.length,
                topics: [],
                rubric: [],
                updateDate: '2018-12-11T08:56:49Z',
                publicationDate: '2018-12-14T01:50:49Z',
                pageUrlCanonical:
                    'https://example.com/pointless-articles-2-electric-boogaloo',
                pageTitle: "Vasily Pupkin: Vasily's review",
                authors: [
                    {
                        name: 'Vasily Pupkin',
                    },
                ],
                stamp: nowMs,
                index: 1,
                type: PUBLISHER_REVIEW_TYPE,
            },
        ];

        chai.expect(result).to.deep.equal(expected);
    });
});
