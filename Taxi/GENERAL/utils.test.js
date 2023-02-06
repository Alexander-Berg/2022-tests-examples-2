const {isMultiSteps, isRequirementField, getTranslate, getValue, checkCondition, validate} = require('./utils');

const condition = {
    key1: {$in: {type: 'string', stringValue: 'Доверенность'}},
    key2: {$nin: {type: 'string', stringValue: '5'}},
    key3: {$eq: {type: 'number', numberValue: 6}},
    key4: {$ne: {type: 'string', stringValue: 'key4'}}
};

const trueValues1 = {key1: {type: 'string', stringValue: 'Доверенность'}};
const trueValues2 = {key2: {type: 'string', stringValue: '6'}};
const trueValues3 = {key3: {type: 'number', numberValue: 6}};
const trueValues4 = {key4: {type: 'string', stringValue: 'not key4'}};
const trueValues = {...trueValues1, ...trueValues2, ...trueValues3, ...trueValues4};

const falseValues1 = {key1: {type: 'string', stringValue: 'Доверенн'}};
const falseValues2 = {key2: {type: 'string', stringValue: '5'}};
const falseValues3 = {key3: {type: 'number', numberValue: 5}};
const falseValues4 = {key4: {type: 'string', stringValue: 'key4'}};
const falseValues = {...falseValues1, ...falseValues2, ...falseValues3, ...falseValues4};

const conditions = {test: condition};

describe('yandex/static/bundels/app/forms/components/form/utils', () => {
    describe('isMultiSteps', () => {
        it('not multi', () => {
            expect(isMultiSteps(0)).toBeFalsy();
            expect(isMultiSteps(1)).toBeFalsy();
        });

        it('multi', () => {
            expect(isMultiSteps(2)).toBeTruthy();
            expect(isMultiSteps(99)).toBeTruthy();
        });
    });
    describe('getTranslate', () => {
        it('not translate', () => {
            expect(getTranslate({})).toBeUndefined();
            expect(getTranslate(null)).toBeUndefined();
            expect(getTranslate(1)).toBeUndefined();
            expect(getTranslate(1, {})).toBeUndefined();
        });

        it('translate', () => {
            expect(getTranslate({translation: 'name'})).toEqual('name');
            expect(getTranslate({translation: 1})).toEqual(1);
            expect(getTranslate({}, {translation: 1})).toEqual(1);
        });
    });
    describe('getValue', () => {
        it('not value', () => {
            expect(getValue({})).toBeUndefined();
            expect(getValue(null)).toBeNull();
            expect(getValue(1)).toBeUndefined();
            expect(getValue({type: 'string'})).toBeUndefined();
            expect(getValue({type: 'string', stringV: 'V'})).toBeUndefined();
            expect(getValue({type: 'string', numberValue: 'V'})).toBeUndefined();
        });

        it('value', () => {
            expect(getValue({type: 'string', stringValue: 'value'})).toEqual('value');
            expect(getValue({type: 'number', numberValue: 'number'})).toEqual('number');
        });
    });
    describe('checkCondition', () => {
        it('true', () => {
            expect(checkCondition(condition, trueValues)).toBeTruthy();
        });

        it('false', () => {
            const testValues = [falseValues1, falseValues2, falseValues3, falseValues4, falseValues];
            for (const values of testValues) {
                expect(checkCondition(condition, values)).toBeFalsy();
            }
        });
    });
    describe('isRequirementField', () => {
        it('Requirement', () => {
            const requirementsR = {requirement: true};
            const requirementsRRC = {requirement: true, requirement_condition: 'test'};
            const requirementsRC = {requirement: false, requirement_condition: 'test'};

            expect(isRequirementField(requirementsR, trueValues, conditions)).toBeTruthy();
            expect(isRequirementField(requirementsR, falseValues, conditions)).toBeTruthy();
            expect(isRequirementField(requirementsRRC, trueValues, conditions)).toBeTruthy();
            expect(isRequirementField(requirementsRRC, falseValues, conditions)).toBeTruthy();
            expect(isRequirementField(requirementsRC, trueValues, conditions)).toBeTruthy();
        });

        it('not Requirement', () => {
            const requirements = {requirement: false};
            const requirementsRC = {requirement: false, requirement_condition: 'test'};

            expect(isRequirementField(requirements, trueValues, conditions)).toBeFalsy();
            expect(isRequirementField(requirements, falseValues, conditions)).toBeFalsy();
            expect(isRequirementField(requirementsRC, falseValues, conditions)).toBeFalsy();
        });
    });
    describe('validate', () => {
        const stages = [
            {fields: [{code: 'key1'}, {code: 'key2'}, {code: 'key3'}, {code: 'key4'}]},
            {
                fields: [
                    {code: 'key1', obligatory: true, visible: true},
                    {code: 'key2', obligatory: true, visible: true},
                    {code: 'key3', obligatory: true, visible: true},
                    {code: 'key4', obligatory: true, visible: true}
                ]
            },
            {
                fields: [
                    {code: 'key1', obligatory: true, obligation_condition: 'test', visible: true},
                    {code: 'key2', obligatory: true, obligation_condition: 'test', visible: true},
                    {code: 'key3', obligatory: true, obligation_condition: 'test', visible: true},
                    {code: 'key4', obligatory: true, obligation_condition: 'test', visible: true}
                ]
            },
            {
                fields: [
                    {code: 'key1', obligatory: true, obligation_condition: 'test', visibility_condition: 'test'},
                    {code: 'key2', obligatory: true, obligation_condition: 'test', visibility_condition: 'test'},
                    {code: 'key3', obligatory: true, obligation_condition: 'test', visibility_condition: 'test'},
                    {code: 'key4', obligatory: true, obligation_condition: 'test', visibility_condition: 'test'}
                ]
            },
            {
                fields: [
                    {code: 'key1', obligation_condition: 'test', visible: true},
                    {code: 'key2', obligatory: true, obligation_condition: 'test', visible: true},
                    {code: 'key3', obligatory: true, obligation_condition: 'test', visible: true},
                    {code: 'key4', obligatory: true, obligation_condition: 'test', visible: true}
                ]
            },
            {
                fields: [
                    {code: 'key1', obligatory: true, obligation_condition: 'test', visibility_condition: 'test2'},
                    {code: 'key2', obligatory: true, obligation_condition: 'test', visibility_condition: 'test2'},
                    {code: 'key3', obligatory: true, obligation_condition: 'test', visibility_condition: 'test2'},
                    {code: 'key4', obligatory: true, obligation_condition: 'test', visibility_condition: 'test2'}
                ]
            },
            {
                fields: [
                    {code: 'key1', obligatory: true, obligation_condition: 'test', visibility_condition: 'test2'},
                    {code: 'key2', obligatory: true, obligation_condition: 'test', visibility_condition: 'test2'},
                    {code: 'key3', obligatory: true, obligation_condition: 'test', visibility_condition: 'test2'},
                    {code: 'key4', obligatory: true, obligation_condition: 'test', visibility_condition: 'test2'}
                ]
            }
        ];

        const condition2 = {
            key1: {$in: {type: 'string', stringValue: 'Доверенн'}},
            key2: {$nin: {type: 'string', stringValue: '6'}},
            key3: {$eq: {type: 'number', numberValue: 5}},
            key4: {$ne: {type: 'string', stringValue: 'not key4'}}
        };

        const requirement = {stages, currentStep: 1, conditions};
        const allError = {key1: true, key2: true, key3: true, key4: true};

        const conditionsVO = {
            test: {key1: condition.key1, key2: condition.key2},
            test2: {key3: condition2.key3, key4: condition2.key4}
        };

        const notVisibleAndObligatory = {stages, currentStep: 6, conditions: conditionsVO};
        expect(validate(trueValues, notVisibleAndObligatory)).toEqual({});

        it('validate', () => {
            const notRequirement = {stages, currentStep: 0, conditions};
            expect(validate(trueValues, notRequirement)).toEqual({});
            expect(validate(falseValues, notRequirement)).toEqual({});

            expect(validate(trueValues, requirement)).toEqual({});
            expect(validate(falseValues, requirement)).toEqual({});

            const requirementCondition = {stages, currentStep: 2, conditions};
            expect(validate(trueValues, requirementCondition)).toEqual({});
            expect(validate(falseValues, requirementCondition)).toEqual({});

            const requirementConditionAndVisible = {stages, currentStep: 3, conditions};
            expect(validate(trueValues, requirementConditionAndVisible)).toEqual({});
            expect(validate(falseValues, requirementConditionAndVisible)).toEqual({});

            const conditionsVO = {
                ...conditions,
                test2: condition2
            };
            const notVisible = {stages, currentStep: 5, conditions: conditionsVO};

            expect(validate(trueValues, notVisible)).toEqual({});
            expect(validate(falseValues, notVisible)).toEqual({});
        });

        it('not validate', () => {
            const requirement = {stages, currentStep: 1, conditions};
            const requirementWithCondition = {stages, currentStep: 4, conditions};
            const errors = {key2: true, key3: true, key4: true};

            expect(validate({}, requirement)).toEqual(allError);
            expect(validate(falseValues1, requirement)).toEqual(errors);
            expect(validate(trueValues1, requirementWithCondition)).toEqual(errors);
        });
    });
});
