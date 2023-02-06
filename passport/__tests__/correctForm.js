import {correctForm} from '../correctForm';

describe('routes/authRegComplete/correctForm', () => {
    it.each([
        [{form: {type: 'complete_lite', validation: {method: 'phone'}}, hasRecoveryMethod: true}, undefined],
        [{form: {type: 'complete_lite', validation: {method: 'phone'}}, hasRecoveryMethod: false}, 'phone'],
        [{form: {type: 'complete_lite', validation: {method: 'phone'}}, hasRecoveryMethod: true}, undefined],
        [{form: {type: 'complete_lite', validation: {method: 'phone'}}, hasRecoveryMethod: false}, 'phone'],
        [{form: {type: 'complete_neophonish', validation: {method: 'phone'}}, hasRecoveryMethod: true}, undefined],
        [{form: {type: 'complete_neophonish', validation: {method: 'phone'}}, hasRecoveryMethod: false}, undefined]
    ])('should for args %o return form.validation.method = %o', (args, expected) => {
        correctForm(args);
        expect(args.form.validation.method).toEqual(expected);
    });
    it.each([
        [{form: {type: 'complete_lite'}, isMobile: false}, 'complete_lite_v3'],
        [{form: {type: 'complete_neophonis'}, isMobile: true}, 'complete_neophonis_v3_mobile']
    ])('should for args %o return prefix = %o', (args, expected) => {
        correctForm(args);
        expect(args.form.prefix).toEqual(expected);
    });
});
