import { CounterOptions } from '@src/utils/counterOptions';
import * as sinon from 'sinon';
import { noop } from '@src/utils/function';
import { assert, expect } from 'chai';
import * as counterLib from '@src/utils/counter';
import * as loc from '@src/utils/location';
import { rawFirstPartyMethod, encodeRecursive } from '../firstPartyMethod';
import { FirstPartyOutputData } from '../const';

describe('first party data', function test(this: any) {
    this.sandbox = sinon.createSandbox();
    const { sandbox } = this;
    const testHashResult = 'aaaaa';
    const testResult = 'testResult';
    beforeEach(() => {
        this.encodeStub = sandbox.stub().named('encoderStub');
        this.readStub = sandbox.stub();
        this.fileReader = {
            readAsDataURL: this.readStub,
        };
        this.readStub.callsFake(() => {
            (this.fileReader as any).onload({
                target: {
                    result: `,${testResult}`,
                },
            });
        });
        this.windowSpy = {
            TextEncoder: sandbox.stub().named('initEncoder'),
            FileReader: sandbox.stub(),
            Blob: sandbox.stub(),
            crypto: {
                subtle: {
                    digest: sandbox.stub(),
                },
            },
        } as any;
        this.windowSpy.TextEncoder.returns({
            encode: this.encodeStub,
        });
        this.opt = {
            id: 1,
            counterType: '0',
        } as CounterOptions;
        this.paramsSpy = sandbox.spy();
        this.windowSpy.crypto.subtle.digest.resolves(testHashResult);
        this.windowSpy.FileReader.returns(this.fileReader as any);
        this.isHttpsStub = sandbox.stub(loc, 'isHttps').returns(true);
        this.getCounterInstanceStub = sandbox
            .stub(counterLib, 'getCounterInstance')
            .returns({ params: this.paramsSpy } as any);
    });
    afterEach(() => {
        // последовательность важна! restore очищает все стабы из песочницы
        sandbox.reset();
        sandbox.restore();
    });
    it('skip yandex_cid', () => {
        const testObj = { yandex_cid: '1', obj: { d: '1', e: '1' } };
        const result = encodeRecursive(this.windowSpy, testObj);
        return result.then(([dataA]) => {
            const [keyName, val] = dataA;
            expect(keyName).to.be.eq('yandex_cid');
            expect(val).to.be.eq('1');
        });
    });
    it('encode nested objects', () => {
        const testObj = { a: '1', obj: { d: '1', e: '1' } };
        const result = encodeRecursive(this.windowSpy, testObj);
        return result.then(([dataA, dataB]) => {
            let [keyName, val] = dataA;
            expect(keyName).to.be.eq('a');
            expect(val).to.be.eq(testResult);
            const [keyObj, dataCFull] = dataB;
            expect(keyObj).to.be.eq('obj');
            expect(dataCFull).to.be.lengthOf(2);
            const [dataD, dataE] = dataCFull as FirstPartyOutputData[];
            [keyName, val] = dataD;
            expect(keyName).to.be.eq('d');
            expect(val).to.be.eq(testResult);
            [keyName, val] = dataE;
            expect(keyName).to.be.eq('e');
            expect(val).to.be.eq(testResult);
        });
    });
    it('encode flat objects', () => {
        const testObj = { a: '1', b: '123' };
        const result = encodeRecursive(this.windowSpy, testObj);
        return result.then((fullData) => {
            expect(fullData).to.be.lengthOf(2);
            const [dataA, dataB] = fullData;
            const [keyName, val] = dataA;
            expect(keyName).to.be.eq('a');
            expect(val).to.be.eq(testResult);
            const [keyNameB, valB] = dataB;
            expect(keyNameB).to.be.eq('b');
            expect(valB).to.be.eq(testResult);
        });
    });
    it('rejects if digest broken', () => {
        this.windowSpy.crypto.subtle.digest.rejects(testHashResult);
        this.encodeStub.returns(1);
        const testObj = { a: '1' };
        const result = encodeRecursive(this.windowSpy, testObj);
        return result.catch((data) => {
            const { name: firstResult } = data;
            sandbox.assert.calledOnce(this.windowSpy.TextEncoder);
            sandbox.assert.calledWith(
                this.windowSpy.crypto.subtle.digest,
                'SHA-256',
                1,
            );
            expect(firstResult).to.be.eq(testHashResult);
        });
    });
    it('calls recursive encoder', () => {
        this.windowSpy.crypto.subtle.digest.rejects(testHashResult);
        const result = rawFirstPartyMethod(this.windowSpy, this.opt);
        const testObj = { a: '1' };
        const someNewResult = result(testObj) as Promise<unknown>;
        return someNewResult.then(() => {
            sandbox.assert.calledOnce(this.windowSpy.TextEncoder);
        });
    });
    it('return some method which works with objects with keys', () => {
        const result = rawFirstPartyMethod(this.windowSpy, this.opt);
        const testObj = {};
        const someNewResult = result(testObj) as Promise<unknown>;
        return someNewResult
            .then(() => assert.fail('error'))
            .catch((r) => {
                expect(r).to.have.property('message', 'err.kn(25)fpm.l');
            });
    });
    it('return some method which works with objects only', () => {
        const result = rawFirstPartyMethod(this.windowSpy, this.opt);
        expect(result).to.be.not.eq(noop);
        const someNewResult = result(1 as any) as Promise<unknown>;
        return someNewResult
            .then(() => assert.fail('error'))
            .catch((r) => {
                expect(r).to.have.property('message', 'err.kn(25)fpm.o');
            });
    });
    it('fail if it not https', () => {
        this.isHttpsStub.returns(false);
        const result = rawFirstPartyMethod(this.windowSpy, this.opt);
        expect(result).to.be.eq(noop);
    });
    it("fail if counter doesn't exist", () => {
        this.getCounterInstanceStub.returns(null);
        const result = rawFirstPartyMethod(this.windowSpy, this.opt);
        expect(result).to.be.eq(noop);
    });
    it('fail if not supported', () => {
        const win = {} as Window;
        const result = rawFirstPartyMethod(win, this.opt);
        expect(result).to.be.eq(noop);
    });

    describe('normalizes phones', () => {
        it('replaces starting "8" with "7', () => {
            const initialPhone = '8123456';
            const processedPhone = `7123456`;
            const testObj = { phone_number: initialPhone };
            const result = encodeRecursive(this.windowSpy, testObj);
            return result.then((fullData) => {
                expect(fullData).to.be.lengthOf(1);
                const [dataA] = fullData;
                const [keyNameA, valA] = dataA;
                expect(keyNameA).to.be.eq('phone_number');
                expect(valA).to.be.eq(testResult);
                sandbox.assert.calledOnce(this.windowSpy.TextEncoder);
                sandbox.assert.calledWith(this.encodeStub, processedPhone);
            });
        });

        it('keep only digits', () => {
            const initialPhone = ' (123) 456-789  ';
            const processedPhone = '123456789';
            const testObj = { phone_number: initialPhone };
            const result = encodeRecursive(this.windowSpy, testObj);
            return result.then((fullData) => {
                expect(fullData).to.be.lengthOf(1);
                const [dataA] = fullData;
                const [keyNameA, valA] = dataA;
                expect(keyNameA).to.be.eq('phone_number');
                expect(valA).to.be.eq(testResult);
                sandbox.assert.calledOnce(this.windowSpy.TextEncoder);
                sandbox.assert.calledWith(this.encodeStub, processedPhone);
            });
        });
    });

    describe('normalizes emails', () => {
        const testCases = [
            {
                description: 'normalizes "ya.ru" to "yandex.ru"',
                initial: 'name@ya.ru',
                processed: 'name@yandex.ru',
            },
            {
                description: 'normalizes "yandex.com" to "yandex.ru"',
                initial: 'name@yandex.com',
                processed: 'name@yandex.ru',
            },
            {
                description: 'normalizes "yandex.com.tr" to "yandex.ru""',
                initial: 'name@yandex.com.tr',
                processed: 'name@yandex.ru',
            },
            {
                description: 'replaces dots with dashes for yandex domains',
                initial: 'name.namovich@yandex.ru',
                processed: 'name-namovich@yandex.ru',
            },
            {
                description: 'normalizes "googlemail.com" to "gmail.com"',
                initial: 'name@googlemail.com',
                processed: 'name@gmail.com',
            },
            {
                description: 'removes dots for gmail',
                initial: 'name.naimovich@gmail.com',
                processed: 'namenaimovich@gmail.com',
            },
            {
                description: 'removes suffix after "+" in name for gmail',
                initial: 'name+commercial@gmail.com',
                processed: 'name@gmail.com',
            },
        ];

        testCases.forEach(({ description, initial, processed }) => {
            it(description, () => {
                const testObj = { email: initial };
                const result = encodeRecursive(this.windowSpy, testObj);
                return result.then((fullData) => {
                    expect(fullData).to.be.lengthOf(1);
                    const [dataA] = fullData;
                    const [keyNameA, valA] = dataA;
                    expect(keyNameA).to.be.eq('email');
                    expect(valA).to.be.eq(testResult);
                    sandbox.assert.calledOnce(this.windowSpy.TextEncoder);
                    sandbox.assert.calledWith(this.encodeStub, processed);
                });
            });
        });
    });
});
