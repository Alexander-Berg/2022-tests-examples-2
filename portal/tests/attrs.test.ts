import { getAttributes } from '../attrs';

describe('attrs', function() {
    test('возвращает атрибуты', function() {
        expect(getAttributes()).toEqual('');
        expect(getAttributes({})).toEqual('');
        expect(getAttributes({
            role: 'dialog'
        })).toEqual(' role="dialog"');
        expect(getAttributes({
            role: 'dialog',
            tabindex: 0
        })).toEqual(' role="dialog" tabindex="0"');
        expect(getAttributes({
            tabindex: 1,
            disabled: ''
        })).toEqual(' tabindex="1"');
        expect(getAttributes({
            autofocus: home.emptyAttr
        })).toEqual(' autofocus');
    });
});
