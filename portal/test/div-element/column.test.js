const describe = require('mocha').describe;
const chai = require('chai');
const assert = chai.assert;
const {InvalidInstanceError} = require('../../src/infra').errorTypes;
const {DivColumn} = require('../../').DivElements;
const {TextStyle, DivSize, DivPosition} = require('../../').Styles;

describe('DivColumn element test', () => {
    describe('with valid inputs', () => {
        it('should create empty column', () => {
            const column = new DivColumn();
            assert.deepEqual(column.clean, {});
        });

        it('should create weighted column', () => {
            const column = new DivColumn({
                weight: 11
            });
            assert.deepEqual(column.clean, {
                weight: 11
            });
        });

        it('should create weighted column with padding', () => {
            const column = new DivColumn({
                weight: 2,
                leftPadding: DivSize.L,
                rightPadding: DivSize.XL

            });
            assert.deepEqual(column.clean, {
                weight: 2,
                left_padding: 'l',
                right_padding: 'xl'
            });
        });
    });

    describe('with invalid inputs', () => {
        it('should throw InvalidInstanceError', () => {
            assert.throws(() => {
                new DivColumn({
                    weight: 10,
                    leftPadding: 's'
                });

            }, InvalidInstanceError, 'Invalid instance');

            assert.throws(() => {
                new DivColumn({
                    rightPadding: 'xxl'
                });

            }, InvalidInstanceError, 'Invalid instance');
        });
    });
});