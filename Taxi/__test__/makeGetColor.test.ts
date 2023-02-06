import {makeFramedColorSelector} from '../colorUtils';

describe('makeFramedColorSelector', () => {
    const minColor: RGB = {
        r: 100,
        g: 100,
        b: 100,
    };
    const maxColor: RGB = {
        r: 200,
        g: 200,
        b: 200,
    };

    const minVal = 10;
    const maxVal = 100;

    const getColor = makeFramedColorSelector(minColor, maxColor);
    test('возвращает минимальный цвет для минимального значения', () => {
        const curVal = minVal;
        expect(getColor(curVal, minVal, maxVal)).toEqual(minColor);
    });

    test('возвращает макимальный цвет для максимального значения', () => {
        const curVal = maxVal;
        expect(getColor(curVal, minVal, maxVal)).toEqual(maxColor);
    });

    test('возвращает средний цвет для 50%', () => {
        const middleColor = {
            r: (minColor.r + maxColor.r) / 2,
            g: (minColor.g + maxColor.g) / 2,
            b: (minColor.b + maxColor.b) / 2,
        };
        const curVal = (maxVal + minVal) / 2;
        expect(getColor(curVal, minVal, maxVal)).toEqual(middleColor);
    });
});
