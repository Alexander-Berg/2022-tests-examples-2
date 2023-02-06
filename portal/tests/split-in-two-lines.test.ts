import { splitItTwoLines } from '../split-in-two-lines';

describe('split-in-two-lines', () => {
    test('split', () => {
        expect(splitItTwoLines('', 'nobr')).toEqual('');
        expect(splitItTwoLines('test', 'nobr')).toEqual('<span class="nobr">test</span>');
        expect(splitItTwoLines('a test', 'nobr')).toEqual('<span class="nobr">a&nbsp;test</span>');
        expect(splitItTwoLines('test test', 'nobr')).toEqual('<span class="nobr">test</span><br><span class="nobr">test</span>');
        expect(splitItTwoLines('test   test', 'nobr')).toEqual('<span class="nobr">test</span><br><span class="nobr">test</span>');
        expect(splitItTwoLines('test test test test', 'nobr')).toEqual('<span class="nobr">test test</span><br><span class="nobr">test test</span>');
        expect(splitItTwoLines('test test test', 'nobr')).toEqual('<span class="nobr">test</span><br><span class="nobr">test test</span>');
        expect(splitItTwoLines('пробки в Картах', 'nobr')).toEqual('<span class="nobr">пробки</span><br><span class="nobr">в&nbsp;Картах</span>');
    });
});
