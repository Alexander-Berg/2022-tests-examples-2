import { CLSCore } from '../utils/clsCore';

describe('clsCore', () => {
    test('should return generated cls', () => {
        let cls = new CLSCore({
            list: [
                'row',
                'container__line',
                'heap_direction_column'
            ],
            map: {
                row: 'r',
                container: 'c',
                line: 'l',
                heap: 'h',
                direction: 'd',
                column: 'cl'
            },
            blocks: []
        });

        expect(cls.full('line some__line row, media__row heap_direction_column')).toEqual('line some__line r, media__row h_d_cl');
        expect(cls.part('line some__line row, media__row heap_direction_column')).toEqual('l some__l r, media__r h_d_cl');
    });

    test('should return generated cls with blocks', () => {
        let cls = new CLSCore({
            list: [
            ],
            map: {
                row: 'r',
                container: 'c',
                line: 'l',
                heap: 'h',
                direction: 'd',
                column: 'cl'
            },
            blocks: [
                'row',
                'container',
                'heap'
            ]
        });

        expect(cls.full('line some__line row, media__row heap_direction_column')).toEqual('line some__line r, media__row h_direction_column');
        expect(cls.part('line some__line row, media__row heap_direction_column')).toEqual('l some__l r, media__r h_d_cl');
    });
});
