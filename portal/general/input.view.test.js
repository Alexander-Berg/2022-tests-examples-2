import {Input} from 'input/input.view';

(function (execView) {
    'use strict';

    describe('common input', function() {
        it('should render normal input', function() {
            execView(Input, {
            }).should.equal('<span class="input input_theme_normal i-bem" data-bem="{&quot;input&quot;:{}}">' +
                '<span class="input__box">' +
                '<input class="input__control input__input"/>' +
                '<span class="input__clear" unselectable="on">&nbsp;</span>' +
            '</span>' +
        '</span>');
        });

        it('should render textarea', function() {
            execView(Input, {
                mods: {
                    type: 'textarea'
                }
            }).should.equal('<span class="input input_type_textarea input_theme_normal i-bem" data-bem="{&quot;input&quot;:{}}">' +
                '<span class="input__box">' +
                    '<textarea class="input__control input__input"></textarea>' +
                    '<span class="input__clear" unselectable="on">&nbsp;</span>' +
                '</span>' +
            '</span>');
        });

        it('should account for mods and mix', function() {
            execView(Input, {
                mods: {
                    theme: 'pink',
                    foo: 'bar'
                },
                mix: 'baz'
            }).should.equal('<span class="input baz input_theme_pink input_foo_bar i-bem" data-bem="{&quot;input&quot;:{}}">' +
                '<span class="input__box">' +
                    '<input class="input__control input__input"/>' +
                    '<span class="input__clear" unselectable="on">&nbsp;</span>' +
                '</span>' +
            '</span>');
        });

        it('should render w/o clear', function() {
            execView(Input, {
                noclear: true
            }).should.equal('<span class="input input_theme_normal i-bem" data-bem="{&quot;input&quot;:{}}">' +
                '<span class="input__box">' +
                    '<input class="input__control input__input"/>' +
                '</span>' +
            '</span>');
        });

        it('should account for control attrs', function() {
            execView(Input, {
                name: 'foo',
                value: 'baz',
                control: {
                    attrs: {
                        title: 'w!'
                    }
                }
            }).should.equal('<span class="input input_theme_normal i-bem" data-bem="{&quot;input&quot;:{}}">' +
                '<span class="input__box">' +
                    '<input class="input__control input__input" title="w!" value="baz" name="foo"/>' +
                    '<span class="input__clear" unselectable="on">&nbsp;</span>' +
                '</span>' +
            '</span>');
        });

        it('should render input hint', function() {
            execView(Input, {
                control: {
                    attrs: {
                        id: 'inputID'
                    }
                },
                hint: 'foo'
            }).should.equal('<span class="input input_theme_normal i-bem" data-bem="{&quot;input&quot;:{}}">' +
                '<label for="inputID" class="input__hint input__hint_fallback_yes">foo</label>' +
                '<span class="input__box">' +
                    '<input class="input__control input__input" id="inputID" placeholder="foo"/>' +
                    '<span class="input__clear" unselectable="on">&nbsp;</span>' +
                '</span>' +
            '</span>');
        });
    });

})(views.execView);