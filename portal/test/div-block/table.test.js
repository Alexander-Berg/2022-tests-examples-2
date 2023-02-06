const describe = require('mocha').describe;
const chai = require('chai');
const assert = chai.assert;
const {Table} = require('../../src/div/block');
const {DivRow, DivCell} = require('../../src/div/element');
const {PropertyRequiredError, InvalidInstanceError} = require('../../src/infra').errorTypes;

describe('Div table test', () => {
    describe('#createTable', () => {
        describe('with valid inputs', () => {

            it('should create empty table', () => {
                const table = new Table({rows:[]});
                assert.deepEqual(table.clean, {
                    rows:[],
                    type: 'div-table-block'
                });
            });

            it('should create table with row', () => {
                const table = new Table({rows:[
                        new DivRow({
                            cells:[new DivCell({text:'cell'})]
                        })
                    ]});

                assert.deepEqual(table.clean, {
                    rows:[
                        {
                            cells:[
                                {
                                    text:'cell'
                                }
                            ],
                            type: 'row_element'
                        }
                    ],
                    type: 'div-table-block'
                });
            });
        });

        describe('with invalid inputs', () => {
            it('should throw PropertyRequiredError', () => {
                assert.throws(() => {
                    new Table();
                }, PropertyRequiredError, 'Property: rows is required');
            });

            it('should throw InvalidInstanceError', () => {
                assert.throws(() => {
                    new Table({
                        rows:[],
                        action: {}
                    });
                }, InvalidInstanceError, 'Invalid instance.');
            });
        });
    });
});