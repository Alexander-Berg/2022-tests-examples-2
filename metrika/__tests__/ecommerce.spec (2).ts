import * as chai from 'chai';
import * as sinon from 'sinon';
import { validateEcommerceData } from '@src/utils/ecommerce';
import { EcommerceMethods } from '@src/providers/legacyEcommerce/const';
import * as debugConsole from '@src/providers/debugConsole';

describe('Ecommerce', () => {
    describe('validateEcommerceData: ', () => {
        const ctxStub: any = {
            /* eslint-disable no-restricted-globals */
            isFinite,
            isNaN,
        };
        const validData = {
            id: '3002',
            goods: [
                {
                    id: 'ug_0026',
                    name: 'box of something',
                },
                {
                    id: 'ug_0027',
                    name: 'box of something other',
                },
            ],
        };

        const validPurchaseData = { id: '3002' };
        const noIdData = { index: '3002' };
        const emptyData = {};
        const noObjectData: [] = [];
        const emptyGoodsData = {
            id: '3002',
            goods: [],
        };
        const noGoodsIdData = {
            id: '3002',
            goods: [{ index: 'ug_0026' }, { index: 'ug_0027' }],
        };
        const invalidData: { [key: string]: any } = {
            noIdData,
            emptyData,
            noObjectData,
            emptyGoodsData,
            noGoodsIdData,
        };

        const sandbox = sinon.createSandbox();
        beforeEach(() => {
            sandbox.stub(debugConsole, 'consoleLog');
        });

        afterEach(() => {
            sandbox.restore();
        });

        it('return true with valid data for detail,add,remove method', () => {
            const methods = ['detail', 'add', 'remove'];
            methods.forEach((method) => {
                const isValid = validateEcommerceData(
                    method as EcommerceMethods,
                    validData,
                    ctxStub,
                );

                chai.expect(isValid).to.be.true;
            });
        });

        describe('return false with invalid data', () => {
            const methods = ['detail', 'add', 'remove'];
            methods.forEach((method) => {
                Object.keys(invalidData).forEach((key) => {
                    it(`method: ${method}, data: ${key}`, () => {
                        const isValid = validateEcommerceData(
                            method as EcommerceMethods,
                            invalidData[key],
                            ctxStub,
                        );

                        chai.expect(isValid).to.be.false;
                    });
                });
            });
        });

        it('return true with valid data for purchase method', () => {
            const isValid = validateEcommerceData(
                'purchase',
                validPurchaseData,
                ctxStub,
            );

            chai.expect(isValid).to.be.true;
        });

        it('return false with invalid data for purchase method', () => {
            const isValid = validateEcommerceData(
                'purchase',
                noIdData,
                ctxStub,
            );

            chai.expect(isValid).to.be.false;
        });
    });
});
