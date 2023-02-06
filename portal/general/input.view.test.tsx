import { execView } from '@lib/views/execView';
import { Input } from '@block/input/input.view';

describe('common input', function() {
    it('should render normal input', function() {
        expect(execView(Input, {}))
            .toEqual('<span class="input input_theme_normal i-bem" data-bem="{&quot;input&quot;:{}}">' +
                '<span class="input__box">' +
                '<span class="input__clear" unselectable="on">&nbsp;</span>' +
                '<input class="input__control input__input"/>' +
            '</span>' +
        '</span>');
    });

    it('should render textarea', function() {
        expect(execView(Input, {
            mods: {
                type: 'textarea'
            }
        })).toEqual('<span class="input input_type_textarea input_theme_normal i-bem" data-bem="{&quot;input&quot;:{}}">' +
                '<span class="input__box">' +
                    '<span class="input__clear" unselectable="on">&nbsp;</span>' +
                    '<textarea class="input__control input__input"></textarea>' +
                '</span>' +
            '</span>');
    });

    it('should account for mods and mix', function() {
        expect(execView(Input, {
            mods: {
                theme: 'pink',
                foo: 'bar'
            },
            mix: 'baz'
        })).toEqual('<span class="input baz input_theme_pink input_foo_bar i-bem" data-bem="{&quot;input&quot;:{}}">' +
                '<span class="input__box">' +
                    '<span class="input__clear" unselectable="on">&nbsp;</span>' +
                    '<input class="input__control input__input"/>' +
                '</span>' +
            '</span>');
    });

    it('should render w/o clear', function() {
        expect(execView(Input, {
            noclear: true
        })).toEqual('<span class="input input_theme_normal i-bem" data-bem="{&quot;input&quot;:{}}">' +
                '<span class="input__box">' +
                    '<input class="input__control input__input"/>' +
                '</span>' +
            '</span>');
    });

    it('should account for control attrs', function() {
        expect(execView(Input, {
            name: 'foo',
            value: 'baz',
            control: {
                attrs: {
                    title: 'w!'
                }
            }
        })).toEqual('<span class="input input_theme_normal i-bem" data-bem="{&quot;input&quot;:{}}">' +
                '<span class="input__box">' +
                    '<span class="input__clear" unselectable="on">&nbsp;</span>' +
                    '<input class="input__control input__input" title="w!" value="baz" name="foo"/>' +
                '</span>' +
            '</span>');
    });

    it('should render input hint', function() {
        expect(execView(Input, {
            control: {
                attrs: {
                    id: 'inputID'
                }
            },
            placeholder: 'foo'
        })).toEqual('<span class="input input_theme_normal i-bem" data-bem="{&quot;input&quot;:{}}">' +
                '<span class="input__box">' +
                    '<span class="input__clear" unselectable="on">&nbsp;</span>' +
                    '<input class="input__control input__input" id="inputID" placeholder="foo"/>' +
                '</span>' +
            '</span>');
    });
});
