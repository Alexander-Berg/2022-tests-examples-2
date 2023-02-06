import {mapObject} from 'service/utils/object/map-object/map-object';

describe('mapObject', () => {
    it('just works', () => {
        const objectToMap: {a: number; b: undefined; c: string} = {
            a: 125,
            b: undefined,
            c: '125'
        };

        const mappedObject = mapObject(objectToMap, (value: number | string) => {
            if (typeof value === 'number') {
                return value * 2;
            }

            return value + value;
        });

        expect(mappedObject).toEqual({
            a: 250,
            b: undefined,
            c: '125125'
        });
    });
});
