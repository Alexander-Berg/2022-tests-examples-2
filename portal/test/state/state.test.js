const describe = require('mocha').describe;
const chai = require('chai');
const assert = chai.assert;
const {State} = require('../../src/state');
const {Blocks, DivBlock} = require('../../src/div');
const {errorTypes} = require('../../src/infra');
const {PropertyRequiredError, InvalidInstanceError} = errorTypes;

describe('State test', () => {
    describe('#createState', () => {
        describe('with valid inputs', () => {
            let state, secondState;

            before(() => {
                state = new State({id: 1});
                secondState = new State({id: 1, blocks: new Blocks()})
            });

            it('should create state with given id', () => {
                assert.deepEqual(state, {
                    state_id: 1,
                    blocks: []
                });
            });

            it('should has a field "blocks" of instance Blocks', () => {
                assert.isTrue(state.blocks instanceof Blocks);
                assert.isTrue(secondState.blocks instanceof Blocks);
            });

            it('should has an empty blocks', () => {
                assert.deepEqual(state.blocks.length, 0);
                assert.deepEqual(secondState.blocks.length, 0);
            });

            it('should add a new block', () => {
                state.addBlock(new DivBlock({}, 'div-table-block'));
                secondState.addBlock(new DivBlock({}, 'div-title-block'));
                secondState.addBlock(new DivBlock({}, 'div-universal-block'));
                assert.deepEqual(state.blocks.length, 1);
                assert.deepEqual(secondState.blocks.length, 2);
                assert.deepEqual(secondState, {
                    blocks: [
                        {
                            type: 'div-title-block'
                        },
                        {
                            type: 'div-universal-block'
                        }
                    ],
                    state_id: 1
                })
            });
        });

        describe('with invalid inputs', () => {
            it('should throw PropertyRequiredError', () => {
                assert.throws(() => {
                    new State();
                }, PropertyRequiredError, 'Property: id is required');
            });

            it('should throw InvalidInstanceError', () => {
                assert.throws(() => {
                    new State({id: 1, blocks: [1]});
                }, InvalidInstanceError, 'Invalid instance.');
            });
        });
    });
});