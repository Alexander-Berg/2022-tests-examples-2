import {getImageResizerScale} from '../utils';

describe('utils', () => {
    describe('getImageResizerScale', () => {
        test('scaling by width', () => {
            expect(getImageResizerScale(300, 500, 150, 200)).toBe(0.4);
        });
        test('scaling by height', () => {
            expect(getImageResizerScale(1500, 500, 150, 200)).toBe(0.1);
        });
        test('scaling small image', () => {
            expect(getImageResizerScale(15, 20, 150, 200)).toBe(1);
        });
    });
});
