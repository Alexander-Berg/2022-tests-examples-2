import { CounterOptions } from '@src/utils/counterOptions';
import * as sinon from 'sinon';
import { expect } from 'chai';
import * as counterLib from '@src/utils/counter';
import { CounterObject } from '@src/utils/counter/type';
import * as debugConsole from '@src/providers/debugConsole';
import { AnyFunc } from '@src/utils/function/types';
import {
    firstPartyMethodHashed,
    encodeRecursiveHashed,
} from '../firstPartyMethodHashed';
import { FirstPartyInputData, FirstPartyOutputData } from '../const';

describe('firstPartyMethodHashed', () => {
    const sandbox = sinon.createSandbox();
    let paramsSpy: sinon.SinonSpy<any[], any>;
    let getCounterInstanceStub: sinon.SinonStub<
        [ctx: Window, counterOptions: CounterOptions],
        CounterObject | undefined
    >;
    let getLoggerFnStub: sinon.SinonStub<
        [
            ctx: Window,
            counterOptions: CounterOptions,
            message: string,
            params?: Record<string, any> | string,
        ],
        AnyFunc
    >;
    let loggerFnStub: sinon.SinonSpy<any[], any>;

    const win = {} as Window;
    const opt = {
        id: 1,
        counterType: '0',
    } as CounterOptions;

    beforeEach(() => {
        paramsSpy = sandbox.spy();
        loggerFnStub = sandbox.spy();
        getCounterInstanceStub = sandbox
            .stub(counterLib, 'getCounterInstance')
            .returns({ params: paramsSpy } as unknown as CounterObject);
        getLoggerFnStub = sandbox
            .stub(debugConsole, 'getLoggerFn')
            .returns(loggerFnStub);
    });

    afterEach(() => {
        // последовательность важна! restore очищает все стабы из песочницы
        sandbox.reset();
        sandbox.restore();
    });

    describe('firstPartyMethodHashed', () => {
        it('does nothing if counter instance not found', () => {
            getCounterInstanceStub.returns(undefined);
            const testObj: FirstPartyInputData = {};
            firstPartyMethodHashed(win, opt, testObj);
            sinon.assert.notCalled(getLoggerFnStub);
            sinon.assert.notCalled(paramsSpy);
        });

        it('reports if input is not an object and exits', () => {
            const testObj = '1';

            firstPartyMethodHashed(
                win,
                opt,
                testObj as unknown as FirstPartyInputData,
            );

            sinon.assert.calledOnceWithExactly(
                getLoggerFnStub,
                win,
                opt,
                'First party params error. Not an object.',
            );
            sinon.assert.calledOnce(loggerFnStub);
            sinon.assert.notCalled(paramsSpy);
        });

        it('throws an error if input object has no properties', () => {
            const testObj: FirstPartyInputData = {};

            firstPartyMethodHashed(win, opt, testObj);

            sinon.assert.calledOnceWithExactly(
                getLoggerFnStub,
                win,
                opt,
                'First party params error. Empty object.',
            );
            sinon.assert.calledOnce(loggerFnStub);
            sinon.assert.notCalled(paramsSpy);
        });

        it('encodes and sends valid data', () => {
            const testObj: FirstPartyInputData = {
                a: '1',
                obj: { d: '2', e: '3' },
            };

            expect(() =>
                firstPartyMethodHashed(win, opt, testObj),
            ).to.not.throw();
            sinon.assert.calledOnceWithExactly(paramsSpy, {
                ['__ym']: {
                    [`fpmh`]: [
                        ['a', '1'],
                        [
                            'obj',
                            [
                                ['d', '2'],
                                ['e', '3'],
                            ],
                        ],
                    ],
                },
            });
        });

        it('encodes but does not send a valid input object with no valid properties', () => {
            const testObj = {
                a: 1,
                b: '',
                obj: { c: 2 },
            } as unknown as FirstPartyInputData;

            expect(() =>
                firstPartyMethodHashed(win, opt, testObj),
            ).to.not.throw();
            sinon.assert.notCalled(paramsSpy);
        });
    });

    describe('encodeRecursiveHashed', () => {
        it('recursively converts an object into a multilevel array', () => {
            const testObj: FirstPartyInputData = {
                a: '1',
                obj: { d: '2', e: '3' },
            };

            const result = encodeRecursiveHashed(testObj);
            expect(result).to.be.lengthOf(2);
            const [dataA, dataObj] = result;

            const [keyNameA, valA] = dataA;
            expect(keyNameA).to.eq('a');
            expect(valA).to.eq('1');

            const [keyNameObj, valObj] = dataObj;
            expect(keyNameObj).to.eq('obj');

            expect(valObj).to.be.lengthOf(2);
            const [dataD, dataE] = valObj as FirstPartyOutputData[];

            const [keyNameD, valD] = dataD;
            expect(keyNameD).to.eq('d');
            expect(valD).to.eq('2');

            const [keyNameE, valE] = dataE;
            expect(keyNameE).to.eq('e');
            expect(valE).to.eq('3');
        });

        it('drops non-string values', () => {
            const testObj = { a: '1', b: 2 } as unknown as FirstPartyInputData;

            const result = encodeRecursiveHashed(testObj);
            expect(result).to.be.lengthOf(1);
            const [dataA, rest] = result;

            const [keyNameA, valA] = dataA;
            expect(keyNameA).to.eq('a');
            expect(valA).to.eq('1');
            expect(rest).to.be.undefined;
        });
    });
});
