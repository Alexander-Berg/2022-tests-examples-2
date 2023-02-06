const describe = require('mocha').describe;
const chai = require('chai');
const assert = chai.assert;
const {DivTabs} = require('../../src/div/composite-block');
const {DivItem} = require('../../src/div');
const {PropertyRequiredError} = require('../../src/infra/index').errorTypes;

describe('Div Tabs test', () => {
    describe('#createTabs', () => {
        describe('with valid inputs', () => {

            it('should create simple tabs with one item', () => {
                const tabs = new DivTabs({
                    items: [new DivItem({
                    })]
                });
                assert.deepEqual(tabs.clean, {
                        'has_delimiter': 0,
                        'items': [{}],
                        'type': 'div-tabs-block'
                    }
                );
            });
        });

        describe('with invalid inputs', () => {
            it('should throw PropertyRequiredError', () => {
                assert.throws(() => {
                    new DivTabs();
                }, PropertyRequiredError, 'Property: items is required');
            });
        });
    });
});