import i18n from '_pkg/utils/localization/i18n';

import {PredicateCheckTypes} from '../../../../types';
import {isDisabledUploadFileButton} from '../utils';

describe('upload checking', () => {
    test('should enable by empty check', () => {
        const {isDisabled} = isDisabledUploadFileButton();

        expect(isDisabled).toBeFalsy();
    });

    // Number Range
    test('should enable by correct number range', () => {
        const {isDisabled} = isDisabledUploadFileButton({
            type: 'range' as PredicateCheckTypes.NumberRange,
            rangeFrom: 100,
            rangeTo: 200
        });

        expect(isDisabled).toBeFalsy();
    });

    test('should disable by number range where from >= to', () => {
        const {isDisabled, reason} = isDisabledUploadFileButton({
            type: 'range' as PredicateCheckTypes.NumberRange,
            rangeFrom: 200,
            rangeTo: 100
        });

        expect(isDisabled).toBeTruthy();
        expect(reason).toEqual(i18n.print('left_border_must_be_less_than_right'));
    });

    test('should disable by number range with alone from', () => {
        const {isDisabled, reason} = isDisabledUploadFileButton({
            type: 'range' as PredicateCheckTypes.NumberRange,
            rangeFrom: 100
        });

        expect(isDisabled).toBeTruthy();
        expect(reason).toEqual(i18n.print('must_be_two_or_zero_correct_params'));
    });

    test('should disable by number range with alone to', () => {
        const {isDisabled, reason} = isDisabledUploadFileButton({
            type: 'range' as PredicateCheckTypes.NumberRange,
            rangeTo: 100
        });

        expect(isDisabled).toBeTruthy();
        expect(reason).toEqual(i18n.print('must_be_two_or_zero_correct_params'));
    });

    test('should disable by number range with "double" type params', () => {
        const {isDisabled} = isDisabledUploadFileButton({
            type: 'range' as PredicateCheckTypes.NumberRange,
            rangeFrom: 1.0,
            rangeTo: 2.35
        });

        expect(isDisabled).toBeFalsy();
    });

    // String Length
    test('should enable by correct string length', () => {
        const {isDisabled} = isDisabledUploadFileButton({
            type: 'length' as PredicateCheckTypes.StringLength,
            rangeFrom: 1,
            rangeTo: 2
        });

        expect(isDisabled).toBeFalsy();
    });

    test('should enable by correct fixed string length', () => {
        const {isDisabled} = isDisabledUploadFileButton({
            type: 'length' as PredicateCheckTypes.StringLength,
            rangeFrom: 2,
            rangeTo: 2
        });

        expect(isDisabled).toBeFalsy();
    });

    test('should enable by correct string length with alone to', () => {
        const {isDisabled} = isDisabledUploadFileButton({
            type: 'length' as PredicateCheckTypes.StringLength,
            rangeTo: 5
        });

        expect(isDisabled).toBeFalsy();
    });

    test('should disable by string length where from >= to', () => {
        const {isDisabled, reason} = isDisabledUploadFileButton({
            type: 'length' as PredicateCheckTypes.StringLength,
            rangeFrom: 2,
            rangeTo: 1
        });

        expect(isDisabled).toBeTruthy();
        expect(reason).toEqual(i18n.print('left_border_must_not_be_more_than_right'));
    });

    test('should disable by string length with alone from', () => {
        const {isDisabled, reason} = isDisabledUploadFileButton({
            type: 'length' as PredicateCheckTypes.StringLength,
            rangeFrom: 100
        });

        expect(isDisabled).toBeTruthy();
        expect(reason).toEqual(i18n.print('right_border_must_be_more_than_zero'));
    });

    // StringRegExp
    test('should enable by correct string regexp', () => {
        const check = {
            type: 'regexp' as PredicateCheckTypes.StringRegExp
        };

        const correctRegExps = ['hello', '\(hello\)', '$.?\.+([a-z]*?)'];

        for (const regExp of correctRegExps) {
            const {isDisabled} = isDisabledUploadFileButton({
                ...check,
                regExp
            });

            expect(isDisabled).toBeFalsy();
        }
    });

    test('should disable by string regexp with incorrect regExp', () => {
        const check = {
            type: 'regexp' as PredicateCheckTypes.StringRegExp
        };

        const incorrectRegExps = ['(', '[', 'hi)'];

        for (const regExp of incorrectRegExps) {
            const {isDisabled, reason} = isDisabledUploadFileButton({
                ...check,
                regExp
            });

            expect(isDisabled).toBeTruthy();
            expect(reason).toEqual(i18n.print('incorrect_regular_expression'));
        }
    });
});
