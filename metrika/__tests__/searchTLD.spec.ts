import * as sinon from 'sinon';
import * as loc from '@src/utils/location';
import * as config from '@src/config';
import { getDomainAndTLD } from '@src/providers/searchTLD';
import * as parse from '@src/utils/url';
import * as flagsModule from '@inject';
import { SEARCH_TLD_FEATURE, LOCAL_FEATURE } from '@generated/features';
import { expect } from 'chai';

describe('search TLD', () => {
    const sandbox = sinon.createSandbox();
    let isYandexSearchDomainStub: sinon.SinonStub<any, any>;
    let urlParserStub: sinon.SinonStub<any, any>;
    let configStub: sinon.SinonStub<any, any>;
    let hostStub: sinon.SinonStub<any, any>;
    let baseDomainStub: sinon.SinonStub<any, any>;
    let flagStub: sinon.SinonStub<any, any>;
    let tldStub: sinon.SinonStub<any, any>;

    const testPtotocol = 'proto';
    const testDomain = 'testDomain';
    const testTld = 'test';
    const testHost = `${testDomain}.${testTld}`;

    beforeEach(() => {
        isYandexSearchDomainStub = sandbox.stub(loc, 'isYandexSearchDomain');

        urlParserStub = sandbox.stub(parse, 'parseUrl');
        urlParserStub.returns({
            host: '',
        });
        baseDomainStub = sandbox.stub(config, 'BASE_DOMAIN');
        baseDomainStub.value(testDomain);
        hostStub = sandbox.stub(config, 'host');
        hostStub.value(testHost);
        configStub = sandbox.stub(config, 'config');
        configStub.value({
            protocol: testPtotocol,
        });
        flagStub = sandbox.stub(flagsModule, 'flags');
        flagStub.value({
            [SEARCH_TLD_FEATURE]: true,
            [LOCAL_FEATURE]: false,
        });
        tldStub = sandbox.stub(config, 'BASE_TLD');
        tldStub.value(testTld);
    });

    afterEach(() => {
        sandbox.restore();
    });

    it('check tld', () => {
        const newTld = 'yandex';
        const testRef = 'test';
        const win = {
            document: {
                referrer: testRef,
            },
        };
        isYandexSearchDomainStub.returns(newTld);
        const tld = getDomainAndTLD(win as any);
        sinon.assert.calledWith(urlParserStub, win, testRef);
        expect(tld).to.be.eq(`${testDomain}.${newTld}`);
    });
});
