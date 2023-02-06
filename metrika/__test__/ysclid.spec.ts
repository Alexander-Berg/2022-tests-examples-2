import * as sinon from 'sinon';
import * as history from '@src/utils/history';
import chai from 'chai';
import { ysclid, replaceHrefParam } from '../ysclid';

describe('ysclid', () => {
    const ysclidParam = 'ysclid=123';
    const stubSearchWithYsclid = `?a=1&${ysclidParam}&b=2`;
    const stubHrefWithYsclid = `https://metrika.yandex.ru/promo${stubSearchWithYsclid}`;
    const stubSearch = replaceHrefParam(stubSearchWithYsclid);
    const stubHref = `https://metrika.yandex.ru/promo${stubSearch}`;
    const win = {
        location: {
            href: stubHrefWithYsclid,
            search: stubSearchWithYsclid,
        },
    } as any as Window;
    const sandbox = sinon.createSandbox();
    let replaceStateStub: sinon.SinonStub<any, any>;

    beforeEach(() => {
        replaceStateStub = sandbox.stub(history, 'replaceState');
    });
    afterEach(() => {
        sandbox.restore();
    });

    it('replace url', () => {
        ysclid(win);
        sinon.assert.calledOnce(replaceStateStub);
        sinon.assert.calledWith(replaceStateStub, win, stubHref);
    });

    it('no ysclid param', () => {
        win.location.href = stubHref;
        win.location.search = stubSearch;
        ysclid(win);
        sinon.assert.notCalled(replaceStateStub);
    });

    [
        {
            href: 'https://metrika.yandex.ru',
            validReplace: 'https://metrika.yandex.ru',
        },
        {
            href: 'https://metrika.yandex.ru?a=1',
            validReplace: 'https://metrika.yandex.ru?a=1',
        },
        {
            href: `https://metrika.yandex.ru?${ysclidParam}`,
            validReplace: 'https://metrika.yandex.ru?',
        },
        {
            href: `https://metrika.yandex.ru?a${ysclidParam}`,
            validReplace: `https://metrika.yandex.ru?a${ysclidParam}`,
        },
        {
            href: `https://metrika.yandex.ru?a=1&${ysclidParam}`,
            validReplace: 'https://metrika.yandex.ru?a=1&',
        },
        {
            href: `https://metrika.yandex.ru?${ysclidParam}&a=1`,
            validReplace: 'https://metrika.yandex.ru?a=1',
        },
        {
            href: `https://metrika.yandex.ru?a=1&${ysclidParam}&b=2`,
            validReplace: 'https://metrika.yandex.ru?a=1&b=2',
        },
    ].forEach(({ href, validReplace }) => {
        it(`check replace ${href} to ${validReplace}`, () => {
            chai.expect(validReplace).to.equal(replaceHrefParam(href));
        });
    });
});
