const describe = require('mocha').describe;
const chai = require('chai');
const assert = chai.assert;
const Card = require('../../src/card/card');
const {State, States} = require('../../src/state');
const {Blocks} = require('../../src/div');
const {errorTypes} = require('../../src/infra');
const {PropertyRequiredError, InvalidInstanceError} = errorTypes;

describe('Div blocks test', () => {
    describe('#createCard', () => {
        let card, cardParams;

        before(() => {
            const states = new States();
            states.add(new State({id: 1, blocks: new Blocks()}));
            cardParams = {
                id: 'sport',
                topic: 'sport_card',
                exportParams: {}
            };

            card = new Card({
                ...cardParams,
                states: states
            });
        });

        describe('with valid inputs', () => {
            it('should create card with given id', () => {
                assert.deepEqual(card.id, 'sport');
            });

            it('should create card with given topic', () => {
                assert.deepEqual(card.topic, 'sport_card');
            });

            it('should create card with one state', () => {
                assert.deepEqual(card.data.states.length, 1);
            });

            it('should add second state to card', () => {
                card.addState(new State({id: 2}));
                assert.deepEqual(card.data.states[1], {
                    state_id: 2,
                    blocks: []
                });
            });
        });

        describe('with invalid inputs', () => {
            it('should throw PropertyRequiredError', () => {
                assert.throws(() => {
                    new Card();
                }, PropertyRequiredError, 'Property: id is required');
            });

            it('should throw InvalidInstanceError', () => {
                assert.throws(() => {
                    new Card({...cardParams, states: []});
                }, InvalidInstanceError, 'Invalid instance. An object must be an instance of States.');
                assert.throws(() => {
                    new Card({...cardParams, background: []});
                }, InvalidInstanceError, 'Invalid instance. An object must be an instance of Backgrounds.');
            });
        });
    });
});