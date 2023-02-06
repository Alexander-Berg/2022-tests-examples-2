import {Graph} from '../../../../types';
import {mapToLevel, Matrix} from '../utils';

describe('level', function () {
    it('should ', function () {
        const input: Graph = {
            a: ['b', 'c'],
            b: [],
            c: [],
        };
        const output: Matrix = [
            // первый уровень, одна линия
            [
                ['a', 'b'],
            ],
            // второй уровень, одна линия
            [
                ['a', 'c'],
            ],
        ];
        const result = mapToLevel(input);

        expect(result).toEqual(output);
    });

    it('should 1', function () {
        const input: Graph = {
            a: ['b', 'c'],
            b: ['c'],
            c: [],
        };
        const output: Matrix = [
            // первый уровень, две линии
            [
                ['a', 'b'], ['b', 'c'],
            ],
            // второй уровень, одна линия
            [
                ['a', 'c'],
            ],
        ];
        const result = mapToLevel(input);

        expect(result).toEqual(output);
    });

    it('should 2', function () {
        const input: Graph = {
            a: ['b', 'c'],
            b: ['d', 'e'],
            c: [],
            d: ['e'],
            e: [],
        };
        const output: Matrix = [
            // первый уровень, две линии
            [
                ['a', 'b'], ['b', 'd'], ['d', 'e']
            ],
            // второй уровень, одна линия
            [
                ['a', 'c'],
            ],
            [
                ['b', 'e']
            ],
        ];
        const result = mapToLevel(input);

        expect(result).toEqual(output);
    });

    it('should 3', function () {
        const input: Graph = {
            a: ['b'],
            b: ['a'],
        };
        const output: Matrix = [
            // первый уровень, две линии
            [
                ['a', 'b'], ['b', 'a'],
            ],
        ];
        const result = mapToLevel(input);

        expect(result).toEqual(output);
    });
});
