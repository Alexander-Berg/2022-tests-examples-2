import { convertColor, convertPXToEM, processText } from '../divjsonUtils';

describe('home.divjsonUtils', function() {
    test('should convert app color', function() {
        expect(convertColor('red')).toEqual('red');
        expect(convertColor('#ffffff')).toEqual('#ffffff');
        expect(convertColor('#80ffffff')).toEqual('rgba(255,255,255,0.50)');
        expect(convertColor('#80ffcc00')).toEqual('rgba(255,204,0,0.50)');
        expect(convertColor('#8fc0')).toEqual('rgba(255,204,0,0.53)');
        expect(convertColor('#fc0')).toEqual('#fc0');
    });

    test('should process text', function() {
        expect(processText('abcde')).toEqual('abcde');
        expect(processText('<font>abcde</font>')).toEqual('<font>abcde</font>');
        expect(processText('<font color="#ffffff">abcde</font>')).toEqual('<font color="#ffffff">abcde</font>');
        expect(processText('<font color="#80ffffff">abcde</font>')).toEqual('<font>abcde</font>');
        expect(processText('1234 ₽')).toEqual('1234 <span class="rouble">₽</span>');
    });

    test('should convert px', function() {
        expect(convertPXToEM(20)).toEqual('1.0000em');
        expect(convertPXToEM(10)).toEqual('0.5000em');
        expect(convertPXToEM(13)).toEqual('0.6500em');
    });
});
