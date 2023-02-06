import * as chai from 'chai';
import * as sinon from 'sinon';
import * as timeUtils from '@src/utils/time';
import * as domUtils from '@src/utils/dom';
import * as dConsole from '@src/providers/debugConsole';
import { JSDOMWrapper } from '@src/__tests__/utils/jsdom';
import { AbstractPublisherSchema } from '../AbstractPublisherSchema';
import { PUBLISHER_ARTICLE_TYPE } from '../const';

describe('AbstractPublisherSchema', () => {
    const { window } = new JSDOMWrapper();
    const { document } = window;

    const createNode = (chars: number, id: number): HTMLElement => {
        const div = document.createElement('div');
        div.innerHTML =
            '<div someField="someValue" someOtherField="someOtherValue">' +
            `<h1>Some title ${id}</h1>` +
            `<div id="testText">${'.'.repeat(chars)}</div>` +
            '</div>';
        return div.firstChild! as HTMLElement;
    };

    const descriptionNode = createNode(501, 1);
    const smallDescriptionNode = createNode(1, 1);

    const textLength = descriptionNode.textContent!.length;

    class ConcretePublishersSchema extends AbstractPublisherSchema {
        id = 'c';

        fields = {
            ['someField' as any](data: any) {
                return data.element.getAttribute('someField');
            },
            ['someOtherField' as any](data: any) {
                return data.element.getAttribute('someOtherField');
            },
            ['chars' as any](data: any) {
                return data.element.textContent!.length;
            },
            ['type' as any]() {
                return PUBLISHER_ARTICLE_TYPE;
            },
        };

        findContentDescriptionNodes() {
            return [
                descriptionNode as HTMLElement,
                smallDescriptionNode as HTMLElement,
            ];
        }
    }
    const schema = new ConcretePublishersSchema(window, '');
    const nowMs = 11111102;

    const sandbox = sinon.createSandbox();
    beforeEach(() => {
        sandbox
            .stub(domUtils, 'getInnerText')
            .callsFake((node?: HTMLElement | null) => {
                return node ? node.textContent || '' : '';
            });
        sandbox.stub(dConsole, 'consoleLog');
        sandbox.stub(timeUtils, 'getFromStart').returns(nowMs);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('Finds content and postprocesses data', () => {
        const result = schema.findContent();
        result.forEach((data: any) => {
            // eslint-disable-next-line no-param-reassign
            delete data.update;
            // eslint-disable-next-line no-param-reassign
            delete data.type;
        });
        const expected = [
            {
                index: 1,
                element: descriptionNode,
                contentElement: descriptionNode,
                sended: false,
                involvedTime: 0,
                someField: 'someValue',
                someOtherField: 'someOtherValue',
                stamp: nowMs,
                pageTitle: 'Some title 1',
                id: 256829096,
                chars: textLength,
                pageUrlCanonical: undefined,
            },
        ];

        chai.expect(result).lengthOf(1);
        chai.expect(result).to.deep.equal(expected);
    });
});
