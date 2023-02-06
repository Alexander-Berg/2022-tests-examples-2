import * as sinon from 'sinon';
import { JSDOMWrapper } from '@src/__tests__/utils/jsdom';
import chai from 'chai';
import * as isNativeFn from '@src/utils/function/isNativeFunction/isNativeFn';
import { scrambleContent, isHiddenContent } from '../isHiddenContent';

describe('webvisor / is hidden content', () => {
    const { window } = new JSDOMWrapper(`
        <body>
            <div>
                <div id="totally-not-hidden">
                    this is not hidden content
                </div>
                <div class="ym-hide-content">
                    <div id="hidden">
                        this is not hidden content
                    </div>
                    <div id="force-shown" class="ym-show-content">
                        this is hidden content
                    </div>
                </div>
            </div>
        </body>
    `);
    const { document } = window;
    const sandbox = sinon.createSandbox();

    beforeEach(() => {
        sandbox.stub(isNativeFn, 'isNativeFn').returns(true);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('scrambles content', () => {
        const original = '123 content to SCRAMBLE!';
        const scrambled = scrambleContent(window, original);
        chai.assert(original !== scrambled);
        chai.assert(/^\d{3} [a-z]{7} [a-z]{2} [A-Z]{8}!$/);
    });

    it('determines if content is hidden', () => {
        const hiddenDiv = document.querySelector('#hidden');
        const notHidden = document.querySelector('#totally-not-hidden');
        const forceShownHidden = document.querySelector('#force-shown');

        chai.assert(
            isHiddenContent(window, hiddenDiv!.childNodes[0]! as HTMLElement),
        );
        chai.assert(
            !isHiddenContent(window, notHidden!.childNodes[0]! as HTMLElement),
        );
        chai.assert(
            !isHiddenContent(
                window,
                forceShownHidden!.childNodes[0]! as HTMLElement,
            ),
        );
    });
});
