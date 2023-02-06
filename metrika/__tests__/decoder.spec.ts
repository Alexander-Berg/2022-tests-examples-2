import chai from 'chai';
import * as isNativeFn from '@src/utils/function/isNativeFunction/isNativeFn';
import sinon from 'sinon';
import { decoder } from '../decoder';

describe('ecommerceParser', () => {
    const window = { JSON } as Window;
    const sandbox = sinon.createSandbox();

    beforeEach(() => {
        sandbox.stub(isNativeFn, 'isNativeFn').returns(true);
    });

    afterEach(() => {
        sandbox.restore();
    });

    describe('decoder, version 1 not supported', () => {
        [
            {
                value: '',
                test: [],
            },
            {
                value: '1',
                test: [],
            },
            {
                value: 'AQBUsOjql7Fy3Wejcq95d5+uGLlus9G5V7y7z9cMWxbFsX6AgA1nvD49t53YcPYti3TA',
                test: [],
            },
            {
                value: 'AQBWsOjfhSOa4o1WWznsXoXGNLC+5IAQHt+mWak6Ri9C4xpYX3JACA9v0yzUnSMWxbFsWse287sOHsWxbpg=',
                test: [],
            },
            {
                value: 'AQCxsPfhSOa4o6pexehcY0sL7kgBAe36ZZqTpI7lXvGL0LjGlhfckAID2/TLNSdJHcq94xdG/Ckc1xR1S+hi2Lj5+uLrtyr3jF6NUvMjXJkjhaVQXArHeGMZKu1b7FgQHpKSB3UjpGLXQBAekpIHcmgCSKkKRA9vupBSFZrMBJFjr83T',
                test: [],
            },
            {
                value: 'AQBgSI9IlkiVSJTTdKl6cFD5Ft3c5342WRW3aT8R3VbJSuTT1NN2EiOTT6RG2T1krSFZtKBpEhZwEkXb0iaREkSdIppyRBIUnSJopBpiRL2TAExIjLJYOyfskslFk6kPbmmrKmqaVEcjZ6RJJKVtk01kp0j0Jt2SmCA',
                test: [],
            },
        ].forEach(({ value, test }) => {
            it(`decode ${value} to ${test}`, () => {
                chai.expect(decoder(window, value)).to.be.deep.eq(test);
            });
        });
    });

    describe('decoder, version 2 is supported', () => {
        [
            {
                value: 'AgDgdTPQabw7Gw6gRfpk8wiBvrGz0v61xnw1i/TJ5hEDfWNnpf1rjPhrF+meg03h2Lj0fUMbDqBF+mTzCIG+sbPS/rXGfDWL9MnmEQN9Y2el/WuM+GsX6Z+tD282djYdQIv0yZb8flnYyy3/zLf/TLfj8s7bGW/Hu1Z6jLf/TLOxO1ry7TsEX6Z+tD282di49H1DGw6gRfpk9aHt5s7Fx6PqGNObHIA=',
                test: [
                    '/basket-page',
                    '#currencyWithTotal',
                    '#currencyWithTotal',
                    '/basket-mobile-page',
                    '#currencyWithTotal',
                    '#currencyWithTotal',
                    '/checkout-page',
                    '#кнопка-купить',
                    '/checkout-mobile-page',
                    '#checkout-mobile-btn',
                ],
            },
            {
                value: 'AgDudTPQabw7Gw6gRfpk4+GsX6ZPMIgb6xi/TPQabw7Fx6PqGNh1Ai/TJx8NYv0yeYRA31jF+mfrQ9vNnY2HUCL9MmW/H5Z2Mst/8y3/0y34/LO2xlvx7tWeoy3/0yzsTta8u07BF+mfrQ9vNnYuPR9QxsOoEX6ZPWh7ebOxcej6hjTmxfonYn+CL9E2c6xi/RPP6oRfonYn+CL9E2c6xi/RPP6oRyA=',
                test: [
                    '/basket-page',
                    '#total',
                    '#currency',
                    '/basket-mobile-page',
                    '#total',
                    '#currency',
                    '/checkout-page',
                    '#кнопка-купить',
                    '/checkout-mobile-page',
                    '#checkout-mobile-btn',
                    '.price',
                    '.qty',
                    '.title',
                    '.price',
                    '.qty',
                    '.title',
                ],
            },
        ].forEach(({ value, test }) => {
            it(`decode ${value} to ${test}`, () => {
                chai.expect(decoder(window, value)).to.be.deep.eq(test);
            });
        });
    });
});
