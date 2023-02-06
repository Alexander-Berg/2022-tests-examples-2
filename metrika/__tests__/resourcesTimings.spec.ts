import * as chai from 'chai';
import sinon, { SinonStub } from 'sinon';
import * as utils from '@src/utils/fnv32a';
import * as sender from '@src/sender';
import { config } from '@src/config';
import * as errorLoggerUtils from '@src/utils/errorLogger';
import { CounterOptions } from '@src/utils/counterOptions';
import * as selfId from '../selfIds';
import { resourcesTimings, ERROR_SCOPE } from '../resourcesTimings';

describe('resourcesTimings.ts', () => {
    let chsumStub: SinonStub<any, any>;
    let errorLoggerStub: SinonStub<any, any>;
    const sandbox = sinon.createSandbox();

    const senderStub = sandbox.stub();
    const counterOptionsStub = {
        id: 1234,
    } as any;
    const timingKeys = {
        timings8: 'timings8',
        scripts: 'scripts',
    } as const;
    type TimingKey = keyof typeof timingKeys;

    const expectedResourceNames: Record<TimingKey, string[]> = {
        timings8: [],
        scripts: [],
    };
    const expectedBrowserInfo = `ar:1:pv:1`;
    const expectedCounterOptions: CounterOptions = {
        id: config.RESOURCES_TIMINGS_COUNTER,
        counterType: '0',
    };
    const expectedUrlParams = {
        'page-url': 'https://whatever.com',
    };

    const generateEntryMock = (isProd = false) => {
        const resourceName = `${isProd ? 'prod' : 'notprod'}-${Math.random()
            .toString()
            .slice(2)}`;
        expectedResourceNames[timingKeys.scripts].push(resourceName);

        if (isProd) {
            expectedResourceNames[timingKeys.timings8].push(resourceName);
        }

        return {
            domainLookupEnd: 1,
            domainLookupStart: 0,
            connectEnd: 1,
            connectStart: 0,
            duration: 2,
            responseEnd: 1,
            requestStart: 0,
            decodedBodySize: 1,
            name: `http://${resourceName}?param=value`,
            initiatorType: 'script',
        };
    };
    const isTiming8Resource = (resourceName: string) => {
        return resourceName.startsWith('prod');
    };
    const entryMocksStub = [
        generateEntryMock(),
        generateEntryMock(),
        generateEntryMock(true),
        generateEntryMock(true),
        generateEntryMock(),
    ];
    const windowStub = {
        performance: {
            getEntriesByType: (type: string) => {
                if (type === 'resource') {
                    return entryMocksStub;
                }

                throw new Error(
                    'Wrong Resource type provided to performance.getEntriesByType',
                );
            },
        },
        location: {
            href: 'https://whatever.com',
        },
        JSON: {
            stringify: JSON.stringify,
        },
    } as unknown as Window;

    const checkTimingsExist = (...timings: TimingKey[]) => {
        const firstCallArgs = senderStub.getCall(0).args;
        chai.expect(firstCallArgs[1]).to.deep.equal(expectedCounterOptions);

        const { brInfo, urlParams, rBody } = firstCallArgs[0];
        chai.expect(brInfo.serialize()).to.eq(expectedBrowserInfo);
        chai.expect(urlParams).to.deep.eq(expectedUrlParams);

        const sessionParams = JSON.parse(rBody);
        const sentResourceParams = Object.keys(sessionParams);
        chai.expect(sentResourceParams.length).to.equal(timings.length);

        timings.forEach((timing) => {
            chai.expect(sentResourceParams).to.include(timing);
            const sentResources = Object.keys(sessionParams[timing]);
            chai.expect(sentResources).to.deep.equal(
                expectedResourceNames[timing],
            );
        });
    };

    beforeEach(() => {
        errorLoggerStub = sandbox.stub(errorLoggerUtils, 'errorLogger');
        sandbox.stub(selfId, 'getSelfIds').returns({});
        chsumStub = sandbox
            .stub(utils, 'fnv32a')
            .callsFake((resourceName: string) => {
                const validVal = 1882689622;
                const invalidVal = 1;
                return isTiming8Resource(resourceName) ? validVal : invalidVal;
            });
        senderStub.resolves();
        sandbox.stub(sender, 'getSender').callsFake(() => senderStub);
    });

    afterEach(() => {
        sandbox.restore();
        senderStub.reset();
    });

    it('should send scripts if 1st sampling is 1', () => {
        resourcesTimings(windowStub, counterOptionsStub, 1, 0);
        chai.expect(senderStub.getCalls().length).to.equal(1);
        checkTimingsExist(timingKeys.scripts);
    });

    it('should send timings8 if 2nd sampling is 1', () => {
        resourcesTimings(windowStub, counterOptionsStub, 0, 1);
        chai.expect(senderStub.getCalls().length).to.equal(1);
        checkTimingsExist(timingKeys.timings8);
    });

    it('should send both if both samplings are 1', () => {
        resourcesTimings(windowStub, counterOptionsStub);
        chai.expect(senderStub.getCalls().length).to.equal(1);
        checkTimingsExist(timingKeys.timings8, timingKeys.scripts);
    });

    it('should do nothing if both samplings are 0', () => {
        resourcesTimings(windowStub, counterOptionsStub, 0, 0);
        chai.expect(chsumStub.notCalled).to.be.true;
    });

    it('send nothing in timings8 field if resource is not external script', () => {
        chsumStub.returns(1);
        resourcesTimings(windowStub, counterOptionsStub, 0, 1);
        chai.expect(senderStub.notCalled).to.be.true;
    });

    it('should not let client errors pass', () => {
        resourcesTimings(windowStub, counterOptionsStub);
        const calls = errorLoggerStub.getCalls();
        chai.expect(calls.length).to.eq(1);

        const [{ args }] = errorLoggerStub.getCalls();
        chai.expect(args[0]).to.eq(windowStub);
        chai.expect(args[1]).to.eq(ERROR_SCOPE);
    });
});
