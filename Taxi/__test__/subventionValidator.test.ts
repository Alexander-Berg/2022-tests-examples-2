import {createRate} from '../../../__test__/utils';
import {Rate, RateWithId} from '../../../types';
import {getGroupedRateValidationRules} from '../subventionValidator';

function addId(rate: Rate, id: number): RateWithId {
    return {
        ...rate,
        id,
    };
}

describe('getGroupedRateValidationRules', function () {
    it('должен работать с пустым массивом', () => {
        expect(getGroupedRateValidationRules([])).toEqual([]);
    });

    it('нет пересечений', () => {
        const rates = [
            createRate('fri', '10:00', 'mon', '20:00', 'A'),
            createRate('mon', '20:00', 'thu', '10:00', 'A'),
            createRate('thu', '10:00', 'fri', '10:00', 'A'),
        ].map(addId);
        expect(getGroupedRateValidationRules(rates)).toEqual([]);
    });

    it('пересечение 2х одинаковых отрезка', () => {
        const rates = [
            createRate('fri', '10:00', 'mon', '20:00', 'A'),
            createRate('fri', '10:00', 'mon', '20:00', 'A'),
        ].map(addId);
        expect(getGroupedRateValidationRules(rates)).toEqual([
            {idx: 1, startInvalid: true, endInvalid: true},
        ]);
    });

    it('пересечение с началом второго', () => {
        const rates = [
            createRate('mon', '10:00', 'mon', '12:00', 'A'),
            createRate('mon', '11:00', 'mon', '13:00', 'A'),
        ].map(addId);
        expect(getGroupedRateValidationRules(rates)).toEqual([
            {idx: 1, startInvalid: true, endInvalid: false},
        ]);
    });

    it('пересечение с концом второй части второго отрезка', () => {
        const rates = [
            createRate('mon', '10:00', 'mon', '12:00', 'A'),
            createRate('mon', '19:00', 'mon', '11:00', 'A'),
        ].map(addId);
        expect(getGroupedRateValidationRules(rates)).toEqual([
            {idx: 1, startInvalid: false, endInvalid: true},
        ]);
    });

    it('пересечение 3x отрезков', () => {
        const rates = [
            createRate('mon', '19:00', 'mon', '21:00', 'A'),
            createRate('mon', '10:00', 'mon', '20:00', 'A'),
            createRate('mon', '09:00', 'mon', '11:00', 'A'),
        ].map(addId);
        expect(getGroupedRateValidationRules(rates)).toEqual([
            {idx: 1, startInvalid: false, endInvalid: true},
            {idx: 2, startInvalid: false, endInvalid: true},
        ]);
    });

    it('пересечение с концом второй части первого отрезка', () => {
        const rates = [
            createRate('fri', '00:00', 'mon', '20:00', 'A'),
            createRate('mon', '19:00', 'mon', '20:00', 'A'),
        ].map(addId);
        expect(getGroupedRateValidationRules(rates)).toEqual([
            {idx: 1, startInvalid: true, endInvalid: true},
        ]);
    });

    it('интервал заканчивается в конце недели, пересечения нет', () => {
        const rates = [
            createRate('fri', '00:00', 'mon', '00:00', 'A'),
            createRate('mon', '00:00', 'mon', '20:00', 'A'),
        ].map(addId);
        expect(getGroupedRateValidationRules(rates)).toEqual([]);
    });

    it('пересечение двух интервалов, один заканчивается в конце недели', () => {
        const rates = [
            createRate('fri', '00:00', 'sun', '00:00', 'A'),
            createRate('sat', '00:00', 'mon', '00:00', 'A'),
        ].map(addId);
        expect(getGroupedRateValidationRules(rates)).toEqual([
            {idx: 1, startInvalid: true, endInvalid: false},
        ]);
    });

    it('пересечение двух интервалов, оба заканчиваются в конце недели #1', () => {
        const rates = [
            createRate('fri', '00:00', 'mon', '00:00', 'A'),
            createRate('sat', '00:00', 'mon', '00:00', 'A'),
        ].map(addId);
        expect(getGroupedRateValidationRules(rates)).toEqual([
            {idx: 1, startInvalid: true, endInvalid: true},
        ]);
    });

    it('пересечение двух интервалов, оба заканчиваются в конце недели #2', () => {
        const rates = [
            createRate('sat', '00:00', 'mon', '00:00', 'A'),
            createRate('fri', '00:00', 'mon', '00:00', 'A'),
        ].map(addId);
        expect(getGroupedRateValidationRules(rates)).toEqual([
            {idx: 1, startInvalid: false, endInvalid: true},
        ]);
    });

    it('должен отметить не валидный промежуток', () => {
        const rates = [
            createRate('mon', '19:00', 'mon', '20:__', 'A'),
        ].map(addId);
        expect(getGroupedRateValidationRules(rates)).toEqual([
            {idx: 0, startInvalid: false, endInvalid: true},
        ]);
    });

    it('должен отметить 3 промежутка с невалидными значениями', () => {
        const rates = [
            createRate('fri', '__:00', 'mon', '20:00', 'A'), // invalid
            createRate('mon', '19:00', 'mon', '20:__', 'A'), // invalid
            createRate('mon', '', 'mon', ':', 'A'), // invalid
            createRate('mon', '00:00', 'mon', '10:00', 'A'), // valid
        ].map(addId);
        expect(getGroupedRateValidationRules(rates)).toEqual([
            {idx: 0, startInvalid: true, endInvalid: false},
            {idx: 1, startInvalid: false, endInvalid: true},
            {idx: 2, startInvalid: true, endInvalid: true},
        ]);
    });

    it('должен показать пересечение и невалидный промежуток', () => {
        const rates = [
            createRate('mon', '10:00', 'mon', '12:00', 'A'),
            createRate('mon', '11:00', 'mon', '12:__', 'A'), // invalid
            createRate('mon', '11:00', 'mon', '13:00', 'A'),
        ].map(addId);
        expect(getGroupedRateValidationRules(rates)).toEqual([
            {idx: 1, startInvalid: false, endInvalid: true}, // invalid input
            {idx: 2, startInvalid: true, endInvalid: false}, // overlap
        ]);
    });
});
