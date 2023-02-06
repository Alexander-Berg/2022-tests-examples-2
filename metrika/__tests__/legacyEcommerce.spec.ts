import * as chai from 'chai';
import * as sinon from 'sinon';
import * as ecommerceModule from '@src/utils/ecommerce';
import { CounterOptions } from '@src/utils/counterOptions';
import { METHOD_NAME_PARAMS } from '@src/providers/params/const';
import { useLegacyEcommerce } from '@src/providers/legacyEcommerce';
import * as counter from '@src/utils/counter';
import { getRandom } from '@src/utils/number';

describe('legacyEcommerce', () => {
    const win = {
        setTimeout,
        Math,
    } as unknown as Window;
    let counterOptions: CounterOptions;
    let getCounterStub: sinon.SinonStub<any, any>;
    describe('useLegacyEcommerce: ', () => {
        const sandbox = sinon.createSandbox();

        let validateEcommerceDataStub: sinon.SinonStub<any, any>;
        let dataGTagFormatToEcommerceFormatStub: sinon.SinonStub<any, any>;
        beforeEach(() => {
            getCounterStub = sandbox.stub(counter, 'getCounterInstance');
            counterOptions = {
                id: getRandom(win, 1000, 10000),
                counterType: '0',
            };

            validateEcommerceDataStub = sandbox.stub(
                ecommerceModule,
                'validateEcommerceData',
            );
            dataGTagFormatToEcommerceFormatStub = sandbox.stub(
                ecommerceModule,
                'dataGTagFormatToEcommerceFormat',
            );
        });
        afterEach(() => {
            sandbox.restore();
        });

        it('return undefined if counter undefined', () => {
            const params = sinon.spy(() => {});
            getCounterStub.returns({
                [METHOD_NAME_PARAMS]: params,
            });

            const result = useLegacyEcommerce('add', win, counterOptions)({});

            chai.expect(result).to.be.an('undefined');
            chai.expect(params.notCalled).to.be.ok;
        });

        it('return undefined if data is invalid', () => {
            const params = sandbox.spy(() => {});

            counterOptions.ecommerce = 'testName';
            getCounterStub.returns({
                [METHOD_NAME_PARAMS]: params,
            });
            validateEcommerceDataStub.returns(false);

            const result = useLegacyEcommerce('add', win, counterOptions)({});

            chai.expect(result).to.be.an('undefined');
            chai.expect(params.notCalled).to.be.ok;
        });

        it('dosen`t send params without data', () => {
            counterOptions.ecommerce = 'testName';

            const params = sandbox.spy(() => {});
            getCounterStub.returns({
                [METHOD_NAME_PARAMS]: params,
            });

            dataGTagFormatToEcommerceFormatStub.returns(undefined);
            validateEcommerceDataStub.returns(true);

            const result = useLegacyEcommerce('add', win, counterOptions)({});

            chai.expect(result).to.be.an('undefined');
            chai.expect(params.notCalled).to.be.ok;
        });

        it('ecommerceMethod: call send params with valid data', () => {
            counterOptions.ecommerce = 'testName';

            const params = sandbox.spy(() => {});
            getCounterStub.returns({
                [METHOD_NAME_PARAMS]: params,
            });
            dataGTagFormatToEcommerceFormatStub.returns({});
            validateEcommerceDataStub.returns(true);

            useLegacyEcommerce('add', win, counterOptions)({});

            chai.expect(params.calledOnce).to.be.ok;
        });
    });
});
