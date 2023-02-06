import {Spacing} from '../../system';
import {calcAlphaShade, calcHex, changeAlpha, convertRGBAToHex} from '../colors';
import {isValidTime} from '../dateTime';
import {calcSpace, cn} from '../index';

test('isValidTime', () => {
    expect(isValidTime('')).toBe(false);
    expect(isValidTime('oo:oo')).toBe(false);
    expect(isValidTime('000:00')).toBe(false);
    expect(isValidTime('00:000')).toBe(false);
    expect(isValidTime('0:0')).toBe(false);
    expect(isValidTime('24:00')).toBe(false);
    expect(isValidTime('23:60')).toBe(false);
    expect(isValidTime(' 00:00 ')).toBe(false);
    expect(isValidTime('00:00 00:00')).toBe(false);

    expect(isValidTime('00:00')).toBe(true);
    expect(isValidTime('09:59')).toBe(true);
    expect(isValidTime('10:11')).toBe(true);
    expect(isValidTime('09:22')).toBe(true);
    expect(isValidTime('20:33')).toBe(true);
    expect(isValidTime('23:44')).toBe(true);
});

test('calcSpace', () => {
    expect(calcSpace('')).toBe('');
    expect(calcSpace('18px')).toBe('18px');
    expect(calcSpace('_XS')).toBe('_XS');
    expect(calcSpace('1_')).toBe('1_');

    expect(calcSpace('XS')).toBe(`${Spacing.XS}px`);
    expect(calcSpace('s')).toBe(`${Spacing.S}px`);
    expect(calcSpace('M')).toBe(`${Spacing.M}px`);
    expect(calcSpace('l')).toBe(`${Spacing.L}px`);
    expect(calcSpace('xL')).toBe(`${Spacing.XL}px`);

    expect(calcSpace('-1_XS')).toBe(`${-1 * Spacing.XS}px`);
    expect(calcSpace('20_S')).toBe(`${20 * Spacing.S}px`);
    expect(calcSpace('-0.5_M')).toBe(`${-0.5 * Spacing.M}px`);
    expect(calcSpace('0.4_L')).toBe(`${0.4 * Spacing.L}px`);
    expect(calcSpace('-15_XL')).toBe(`${-15 * Spacing.XL}px`);

    expect(calcSpace('1_Xs')).toBe(`${1 * Spacing.XS}px`);
    expect(calcSpace('2_s')).toBe(`${2 * Spacing.S}px`);
    expect(calcSpace('3_m')).toBe(`${3 * Spacing.M}px`);
    expect(calcSpace('4_l')).toBe(`${4 * Spacing.L}px`);
    expect(calcSpace('5_xL')).toBe(`${5 * Spacing.XL}px`);
});

test('changeAlpha', () => {
    expect(changeAlpha('rgba(12,123,1,0.23)', 0.45)).toBe('rgba(12,123,1,0.45)');
    expect(changeAlpha('rgba(0,0,0,0)', 0.45)).toBe('rgba(0,0,0,0.45)');

    expect(changeAlpha('rgba( 12, 123,1 , 0.23 )', 0.45)).toBe('rgba(12,123,1,0.45)');
});

test('calcAlphaShade', () => {
    expect(calcAlphaShade(255, 0.45)).toBe(255);
    expect(calcAlphaShade(200, 0.6)).toBe(222);
});

test('calcHex', () => {
    expect(calcHex(255)).toBe('ff');
    expect(calcHex(0)).toBe('00');
    expect(calcHex(126)).toBe('7e');
});

test('convertRGBAToHex', () => {
    expect(convertRGBAToHex('rgba(33,32,31,1)')).toBe('#21201f');
    expect(convertRGBAToHex('rgba(245, 244, 242, 1)')).toBe('#f5f4f2');
    expect(convertRGBAToHex('rgba(0, 0, 0, 0.3)')).toBe('#b3b3b3');
});

test('merge', () => {
    expect(
        cn.merge(
            {
                x: 'x',
                c: 'c',
                a: 'a',
            },
            {
                b: 'b',
                c: 'c2',
                d: 'd',
                x: 'x2',
                z: 'z',
            },
        ),
    ).toEqual({
        a: 'a',
        b: 'b',
        d: 'd',
        c: 'c c2',
        x: 'x x2',
        z: 'z',
    });

    expect(cn.merge({}, {a: 'a'})).toEqual({a: 'a'});
    expect(cn.merge({a: 'a'}, {})).toEqual({a: 'a'});
    expect(cn.merge(undefined, {a: 'a'})).toEqual({a: 'a'});
    expect(cn.merge({a: 'a'}, undefined)).toEqual({a: 'a'});
    expect(cn.merge(null, {a: 'a'})).toEqual({a: 'a'});
    expect(cn.merge({a: 'a'}, null)).toEqual({a: 'a'});
    expect(cn.merge(undefined, null)).toEqual({});
});
