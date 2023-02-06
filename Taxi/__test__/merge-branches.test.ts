import {escapeString} from '../merge-branches';

test('escapeString', () => {
    expect(escapeString('xxx "yyy" `zzz" \'vvv\' bbb')).toBe('xxx yyy zzz vvv bbb');
});
