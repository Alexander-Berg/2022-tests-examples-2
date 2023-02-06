/* eslint-disable @typescript-eslint/no-explicit-any,@typescript-eslint/unbound-method */

import { parseRules } from '../template';
import { mockReq, Req3ServerMocked } from '../mockReq';

describe('template', () => {
    let generatedClsReq: Req3ServerMocked;

    beforeEach(() => {
        jest.clearAllMocks();
        generatedClsReq = mockReq();
    });

    describe('prefix', function() {
        function wrap(func: (...args: any[]) => string, str: string) {
            return function(data: unknown, req?: Req3) {
                return func(data, req || data, str);
            };
        }
        describe('prefix bem classname', function() {
            let data = { mods: { e: 't' }, mix: 'qq', smth: { mods: { w: 'r' } } };
            let testClassname = wrap(parseRules.bem, 'b-block.class');
            let testClassname2 = wrap(parseRules.bem, 'smth.b-block2.class');

            test('понимает название класса', function() {
                expect(testClassname(data)).toEqual('b-block qq b-block_e_t');
            });

            test('понимает указание источника свойств', function() {
                expect(testClassname2(data)).toEqual('b-block2 b-block2_w_r');
            });
        });

        describe('prefix bem js', function() {
            let data = { js: { w: 1 }, smth: { q: 3 } };
            let testJs = wrap(parseRules.bem, 'js');
            let testJs2 = wrap(parseRules.bem, 'smth.js');

            test('работает как ожидается', function() {
                expect(testJs(data)).toEqual('{&quot;w&quot;:1}');
            });

            test('понимает указание источника свойств', function() {
                expect(testJs2(data)).toEqual('{&quot;q&quot;:3}');
            });
        });

        describe('prefix bem attrs', function() {
            let data = { attrs: { title: 'w', src: 'sdfsdf.png' }, smth: { name: 'q', value: '1' } };
            let testAttrs = wrap(parseRules.bem, 'attrs');
            let testAttrs2 = wrap(parseRules.bem, 'smth.attrs');

            test('работает как ожидается', function() {
                expect(testAttrs(data)).toEqual(' title="w" src="sdfsdf.png"');
            });

            test('понимает указание источника свойств', function() {
                expect(testAttrs2(data)).toEqual(' name="q" value="1"');
            });
        });

        describe('prefix bem classname with generated classes and empty map', function() {
            let data = { mods: { e: 't' }, mix: 'qq', smth: { mods: { w: 'r' } } };
            let testClassname = wrap(parseRules.bem, 'b-block.class');
            let testClassname2 = wrap(parseRules.bem, 'smth.b-block2.class');

            test('понимает название класса', function() {
                expect(testClassname(data, generatedClsReq)).toEqual('b-block qq b-block_e_t');
            });

            test('понимает указание источника свойств', function() {
                expect(testClassname2(data, generatedClsReq)).toEqual('b-block2 b-block2_w_r');
            });
        });

        describe('prefix bem classname with generated classes and fullfilled map', function() {
            let data = { mods: { e: 't' }, mix: 'qq', smth: { mods: { w: 'r' } } };
            let testClassname = wrap(parseRules.bem, 'b-block.class');
            let testClassname2 = wrap(parseRules.bem, 'smth.b-block2.class');

            test('понимает название класса', function() {
                generatedClsReq.cls.full.mockImplementation(val => {
                    return val.replace('b-block', 'bb');
                });
                generatedClsReq.cls.contains.mockReturnValue(true);

                expect(testClassname(data, generatedClsReq)).toEqual('bb qq b-block_e_t');
            });

            test('понимает название класса 2', function() {
                generatedClsReq.cls.full.mockImplementation(val => {
                    return val.replace(/b-block/g, 'bb');
                });
                generatedClsReq.cls.contains.mockReturnValue(true);

                expect(testClassname(data, generatedClsReq)).toEqual('bb qq bb_e_t');
            });

            test('понимает указание источника свойств', function() {
                generatedClsReq.cls.full.mockImplementation(val => {
                    return val.replace('b-block2_w_r', 'bb2_w_r');
                });
                generatedClsReq.cls.contains.mockReturnValue(true);

                expect(testClassname2(data, generatedClsReq)).toEqual('b-block2 bb2_w_r');
            });

            test('понимает название класса с заменённым модификатором', function() {
                generatedClsReq.cls.full.mockImplementation(val => {
                    return val.replace(/b-block/g, 'bb');
                });
                generatedClsReq.cls.contains.mockReturnValue(true);

                expect(testClassname(data, generatedClsReq)).toEqual('bb qq bb_e_t');
            });
        });

        describe('prefix cls', function() {
            let testClassname = wrap(parseRules.cls, 'some-block');
            let testClassname2 = wrap(parseRules.cls, 'some__other');

            test('should work without cls', function() {
                expect(testClassname({})).toEqual('some-block');
                expect(testClassname2({})).toEqual('some__other');
            });

            test('should replace classes', function() {
                generatedClsReq.cls.full.mockImplementation(val => {
                    return val.replace(/some-block/g, 'sb').replace(/some__other/g, 'se__or');
                });
                generatedClsReq.cls.contains.mockReturnValue(true);

                expect(testClassname({}, generatedClsReq)).toEqual('sb');
                expect(testClassname2({}, generatedClsReq)).toEqual('se__or');
            });

            test('should replace classes 2', function() {
                generatedClsReq.cls.full.mockImplementation(val => {
                    return val.replace(/some-block/g, 'sb').replace(/some__other/g, 'se__other');
                });
                generatedClsReq.cls.contains.mockReturnValue(true);

                expect(testClassname({}, generatedClsReq)).toEqual('sb');
                expect(testClassname2({}, generatedClsReq)).toEqual('se__other');
            });
        });
    });
});
