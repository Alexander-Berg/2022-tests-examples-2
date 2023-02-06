import * as chai from 'chai';
import * as sinon from 'sinon';
import * as flags from '@inject';
import * as middleware from '@src/sender/middleware';
import * as numberUtils from '@src/utils/number';
import { CONTENT_TYPE_HEADER } from '@src/sender/default/const';
import { browserInfo } from '@src/utils/browserInfo';
import * as globalStorage from '@src/storage/global';
import { REQUEST_MODE_KEY, WATCH_WMODE_IMAGE } from '@src/transport/watchModes';
import { HID_NAME } from '@src/middleware/watchSyncFlags/brinfoFlags/hid';
import { PREPROD_FEATURE } from '@generated/features';
import { WATCH_URL_PARAM } from '@src/sender/watch';
import {
    useSenderWebvisor,
    WEBVISOR_TYPE_KEY,
    WEBVISOR_PART_KEY,
    WEBVISOR_HID_KEY,
    WEBVISOR_RANDOM_NUMBER_KEY,
    WEBVISOR_TYPE_WEBVISOR_AND_PUBLISHER_JSON,
    WEBVISOR_TYPE_WEBVISOR_AND_PUBLISHER_PROTO,
    WEBVISOR_TYPE_WEBVISOR_JSON,
    WEBVISOR_TYPE_WEBVISOR_PROTO,
} from '../webvisor';

describe('sender/webvisor', () => {
    const randomNumber = 100;
    const hitId = 100;
    const sandbox = sinon.createSandbox();

    let defaultSenderStub: sinon.SinonStub<any, any>;
    let randomStub: sinon.SinonStub<any, any>;
    let globalStorageStub: sinon.SinonStub<any, any>;
    let senderSpy: sinon.SinonStub<any, any>;
    let flagsStub: sinon.SinonStub<any, any>;

    beforeEach(() => {
        flagsStub = sandbox.stub(flags, 'flags');
        flagsStub.value({
            [PREPROD_FEATURE]: false,
        });
        senderSpy = sandbox.stub();
        senderSpy.resolves();
        randomStub = sandbox.stub(numberUtils, 'getRandom');
        randomStub.returns(randomNumber);
        globalStorageStub = sandbox.stub(globalStorage, 'getGlobalStorage');
        globalStorageStub.returns({
            getVal: (key: string) => {
                if (key === HID_NAME) {
                    return hitId;
                }
                return null;
            },
        } as any);

        defaultSenderStub = sandbox.stub(middleware, 'useMiddlewareSender');
        defaultSenderStub.returns(senderSpy);
    });

    afterEach(() => {
        sandbox.reset();
        sandbox.restore();
    });

    const checkSenderAndWVType = (
        isBinary: boolean,
        containsPublisherData: boolean,
        WVType: string,
        WVTypePassed?: string,
    ) => {
        const counterOptions = {
            id: 123,
        } as any;
        const part = 1;
        const brInfo = browserInfo();
        const initialSenderParams = {
            debugStack: [],
            brInfo,
            isBinData: isBinary,
            rBody: 'body',
            urlParams: {
                [WEBVISOR_TYPE_KEY]: WVTypePassed,
            } as any,
            containsPublisherData,
        };
        const pageUrl = 'http://example.com';
        const sender = useSenderWebvisor(
            {
                location: {
                    href: pageUrl,
                },
            } as any,
            [],
            [],
        );

        return sender(initialSenderParams, counterOptions, part).then(() => {
            const [senderParams, backendUrls, options] =
                senderSpy.getCall(0).args;

            chai.expect(backendUrls).to.be.equal(
                `webvisor/${counterOptions.id}`,
            );
            chai.expect(options).to.be.deep.eq({
                rHeaders: {
                    [CONTENT_TYPE_HEADER]: 'text/plain',
                },
                verb: 'POST',
            });
            chai.expect(senderParams).to.be.deep.eq({
                brInfo,
                rBody: 'body',
                isBinData: isBinary,
                debugStack: [],
                containsPublisherData,
                urlParams: {
                    [WEBVISOR_HID_KEY]: `${hitId}`,
                    [REQUEST_MODE_KEY]: WATCH_WMODE_IMAGE,
                    [WEBVISOR_TYPE_KEY]: WVType,
                    [WEBVISOR_PART_KEY]: part.toString(),
                    [WEBVISOR_RANDOM_NUMBER_KEY]: randomNumber.toString(),
                    [WATCH_URL_PARAM]: pageUrl,
                },
            });
        });
    };

    it('Sets all the parameters needed for WEBVISOR_TYPE_WEBVISOR_AND_PUBLISHER_JSON', () => {
        return checkSenderAndWVType(
            false,
            true,
            WEBVISOR_TYPE_WEBVISOR_AND_PUBLISHER_JSON,
        );
    });

    it('Sets all the parameters needed for WEBVISOR_TYPE_PUBLISHER_PROTO', () => {
        return checkSenderAndWVType(
            true,
            true,
            WEBVISOR_TYPE_WEBVISOR_AND_PUBLISHER_PROTO,
        );
    });

    it('Sets all the parameters needed for WEBVISOR_TYPE_WEBVISOR_JSON', () => {
        return checkSenderAndWVType(false, false, WEBVISOR_TYPE_WEBVISOR_JSON);
    });

    it('Sets all the parameters needed for WEBVISOR_TYPE_WEBVISOR_PROTO', () => {
        return checkSenderAndWVType(true, false, WEBVISOR_TYPE_WEBVISOR_PROTO);
    });

    it('Sets wvType passedDown', () => {
        return checkSenderAndWVType(true, false, '123', '123');
    });
});
