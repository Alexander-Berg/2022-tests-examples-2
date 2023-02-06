import { pixelsInsideElement } from '../pixels-inside-viewport';

describe('percentageInViewport', function() {
    const makeTest = (clientRect: {height: number; top: number; bottom: number}, document: {clientHeight: number}) => {
        const element = {
            getBoundingClientRect() {
                return clientRect;
            }
        };
        return pixelsInsideElement(element as HTMLElement, document as HTMLElement);
    };
    test('is element inside a viewport', () => {
        const result = makeTest({
            height: 100,
            top: 0,
            bottom: 100
        }, {
            clientHeight: 100
        });
        expect(result).toEqual(100);
    });
    test('is higher than a viewport', () => {
        const result = makeTest({
            height: 100,
            top: 100,
            bottom: 200
        }, {
            clientHeight: 100
        });
        expect(result).toEqual(0);
    });
    test('is lower than a viewport', () => {
        const result = makeTest({
            height: 100,
            top: 200,
            bottom: 300
        }, {
            clientHeight: 100
        });
        expect(result).toEqual(0);
    });
    test('is top higher but bottom inside', () => {
        const result = makeTest({
            height: 150,
            top: -50,
            bottom: 100
        }, {
            clientHeight: 100
        });
        expect(result).toEqual(100);
    });
    test('is top inside but bottom lower', () => {
        const result = makeTest({
            height: 150,
            top: 0,
            bottom: 150
        }, {
            clientHeight: 100
        });
        expect(result).toEqual(100);
    });
    test('is more than a viewport', () => {
        const result = makeTest({
            height: 200,
            top: -100,
            bottom: 200
        }, {
            clientHeight: 100
        });
        expect(result).toEqual(100);
    });
});
