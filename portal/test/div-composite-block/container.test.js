const describe = require('mocha').describe;
const chai = require('chai');
const assert = chai.assert;
const DivCard = require('../../');
const {Title} = DivCard.Blocks;
const {DivContainer, DivTabs} = DivCard.CompositeBlocks;
const {DivFrame} = DivCard.DivElements;
const {BorderStyle, DivDirection, PredefinedSize, NumericSize, Backgrounds, BackgroundTypes} = DivCard.Styles;
const {Action} = DivCard;
const {PropertyRequiredError, InvalidInstanceError} = DivCard.Infra.errorTypes;

describe('Div container test', () => {
    describe('#createContainer', () => {
        let children = [];
        let simpleContainer;

        before(() => {
            children.push(new Title());
            simpleContainer = new DivContainer({
                children: children,
                width: new PredefinedSize(PredefinedSize.MATH_PARENT),
                height: new PredefinedSize(PredefinedSize.WRAP_CONTENT)
            });
        });
        describe('with valid inputs', () => {

            it('should create simple container', () => {

                assert.deepEqual(simpleContainer.clean, {
                    'children': [
                        {
                            'type': 'div-title-block'
                        }
                    ],
                    'height': {
                        'type': 'predefined',
                        'value': 'wrap_content'
                    },
                    'type': 'div-container-block',
                    'width': {
                        'type': 'predefined',
                        'value': 'match_parent'
                    }
                });
            });

            it('should create simple container with background', () => {

                const containerBg = new Backgrounds();

                containerBg.add(BackgroundTypes.SOLID('#ffffff'));
                const container = new DivContainer({
                    children: children,
                    width: new PredefinedSize(PredefinedSize.MATH_PARENT),
                    height: new PredefinedSize(PredefinedSize.WRAP_CONTENT),
                    background: containerBg
                });

                assert.deepEqual(container.clean, {
                    'children': [
                        {
                            'type': 'div-title-block'
                        }
                    ],
                    'height': {
                        'type': 'predefined',
                        'value': 'wrap_content'
                    },
                    'type': 'div-container-block',
                    'width': {
                        'type': 'predefined',
                        'value': 'match_parent'
                    },
                    'background': [{
                        color: '#ffffff',
                        type: 'div-solid-background'
                    }]
                });
            });


            it('should create full container', () => {
                const container = new DivContainer({
                    children: children,
                    direction: DivDirection.VERTICAL,
                    width: new PredefinedSize(PredefinedSize.MATH_PARENT),
                    height: new NumericSize(200, NumericSize.DP),
                    action: new Action({url: 'url', id: 'id'}),
                    frame: new DivFrame({style: BorderStyle.ROUND})
                });
                assert.deepEqual(container.clean, {
                    'children': [
                        {
                            'type': 'div-title-block'
                        }
                    ],
                    direction: 'vertical',
                    'height': {
                        'type': 'numeric',
                        'value': 200,
                        'unit': 'dp'
                    },
                    'type': 'div-container-block',
                    'width': {
                        'type': 'predefined',
                        'value': 'match_parent'
                    },
                    action: {
                        log_id: 'id',
                        url: 'url'
                    },
                    frame: {
                        style: 'only_round_corners'
                    }
                });
            });

        });

        describe('with invalid inputs', () => {
            it('without children input should throw PropertyRequiredError', () => {
                assert.throws(() => {
                    new DivContainer();
                }, PropertyRequiredError, 'Property: children is required');
            });

            it('without width input should throw PropertyRequiredError', () => {
                assert.throws(() => {
                    new DivContainer({
                        children: children,
                        height: new PredefinedSize(PredefinedSize.MATH_PARENT)
                    });
                }, PropertyRequiredError, 'Property: width is required');
            });

            it('without height input should throw PropertyRequiredError', () => {
                assert.throws(() => {
                    new DivContainer({
                        children: children,
                        width: new PredefinedSize(PredefinedSize.MATH_PARENT)
                    });
                }, PropertyRequiredError, 'Property: height is required');
            });

            it('should throw InvalidInstanceError for invalid height and width', () => {
                assert.throws(() => {
                    new DivContainer({
                        children: children,
                        height: 111,
                        width: 111
                    });
                }, InvalidInstanceError, 'Invalid instance.');
            });

            it('should throw InvalidInstanceError if one of the child is instance of DivTabs', () => {
                assert.throws(() => {
                    new DivContainer({
                        children: [new DivTabs({items: [simpleContainer]})],
                        height: new PredefinedSize(PredefinedSize.MATH_PARENT),
                        width: new PredefinedSize(NumericSize.DP)
                    });
                }, InvalidInstanceError, 'Invalid instance.');
            });
        });
    });
});