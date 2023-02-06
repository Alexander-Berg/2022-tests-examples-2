import { color } from '../color';

describe('home.color', function() {
    test('should parse different vals and stringify them', function() {
        expect(color('#fff').toString()).toEqual(color('#ffffff').toString());
        let str = color('#ababab').setOpacity(0.5).toString();
        expect(str).toEqual('rgba(171,171,171,0.5)');
    });

    test('should convert rgb into rgb and hsl', function() {
        expect(color('#fff').rgb).toEqual({ r: 255, g: 255, b: 255 });
        expect(color('#fff').hsl).toEqual({ h: 0, s: 0, l: 1 });

        expect(color('#000').rgb).toEqual({ r: 0, g: 0, b: 0 });
        expect(color('#000').hsl).toEqual({ h: 0, s: 0, l: 0 });

        expect(color('#4eb0da').rgb).toEqual({ r: 78, g: 176, b: 218 });
        expect(Math.round(color('#4eb0da').hsl.h * 360)).toEqual(198);
        expect(Math.round(color('#4eb0da').hsl.s * 100)).toEqual(65);
        expect(Math.round(color('#4eb0da').hsl.l * 100)).toEqual(58);
    });

    test('should modify colors', function() {
        expect(color('#fff').lighter(10).toString()).toEqual('#ffffff');
        expect(color('#fff').lighter(-10).toString()).toEqual('#e6e6e6');
        expect(color('#fff').lighter(-10).lighter(-20).toString()).toEqual('#b8b8b8');

        expect(color('#000').lighter(10).toString()).toEqual('#1a1a1a');
        expect(color('#000').lighter(-10).toString()).toEqual('#000000');

        expect(color('#4eb0da').lighter(10).toString()).toEqual('#60b8de');
        expect(color('#4eb0da').lighter(-10).toString()).toEqual('#36a5d5');
    });
});
