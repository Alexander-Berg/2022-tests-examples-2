/* globals views */

(function (execView) {
    'use strict';
    describe('common button', function() {
        describe('as button', function() {
            it('should render button', function() {
                execView('button', {
                    content: 'text'
                }).should.equal('<button class="button button_theme_normal i-bem" data-bem="{&quot;button&quot;:{}}" role="button" type="button">' +
                        '<span class="button__text">text</span></button>');
            });

            it('should render pseudo button', function() {
                execView('button', {
                    content: 'text',
                    mods: {pseudo: 'yes'}
                }).should.equal('<button class="button button_pseudo_yes button_theme_pseudo i-bem" data-bem="{&quot;button&quot;:{}}" role="button" type="button">' +
                        '<span class="button__text">text</span></button>');
            });

            it('should use custom theme', function() {
                execView('button', {
                    content: 'text',
                    mods: {theme: 'light'}
                }).should.equal('<button class="button button_theme_light i-bem" data-bem="{&quot;button&quot;:{}}" role="button" type="button">' +
                        '<span class="button__text">text</span></button>');
            });

            it('should be disabled', function() {
                execView('button', {
                    content: 'text',
                    mods: {disabled: 'yes'}
                }).should.equal('<button class="button button_disabled_yes button_theme_normal i-bem" data-bem="{&quot;button&quot;:{}}" ' +
                    'role="button" type="button" disabled="disabled">' +
                        '<span class="button__text">text</span></button>');
            });

            it('should account for mods', function() {
                execView('button', {
                    content: 'text',
                    mods: {foo: 'bar'}
                }).should.equal('<button class="button button_foo_bar button_theme_normal i-bem" data-bem="{&quot;button&quot;:{}}" role="button" type="button">' +
                        '<span class="button__text">text</span></button>');
            });

            it('should account for mix', function() {
                execView('button', {
                    content: 'text',
                    mix: 'baz'
                }).should.equal('<button class="button baz button_theme_normal i-bem" data-bem="{&quot;button&quot;:{}}" role="button" type="button">' +
                        '<span class="button__text">text</span></button>');
            });

            it('should use name and value', function() {
                execView('button', {
                    content: 'text',
                    name: 'foo',
                    value: 'bar'
                }).should.equal('<button class="button button_theme_normal i-bem" data-bem="{&quot;button&quot;:{}}" role="button" type="button" name="foo" value="bar">' +
                        '<span class="button__text">text</span></button>');
            });

            it('should use attrs', function() {
                execView('button', {
                    content: 'text',
                    attrs: {
                        id: 'quack'
                    }
                }).should.equal('<button class="button button_theme_normal i-bem" data-bem="{&quot;button&quot;:{}}" id="quack" role="button" type="button">' +
                    '<span class="button__text">text</span></button>');
            });
        });

        describe('as link', function() {
            it('should render button', function() {
                execView('button', {
                    content: 'text',
                    url: '/path/to/smth'
                }).should.equal('<a class="button button_theme_normal i-bem" data-bem="{&quot;button&quot;:{}}" role="button" href="/path/to/smth">' +
                        '<span class="button__text">text</span></a>');
            });

            it('should use target', function() {
                execView('button', {
                    content: 'text',
                    url: '/path/to/smth',
                    target: '_blank'
                }).should.equal('<a class="button button_theme_normal i-bem" data-bem="{&quot;button&quot;:{}}" role="button" href="/path/to/smth" target="_blank">' +
                        '<span class="button__text">text</span></a>');

            });

            it('should account for mix', function() {
                execView('button', {
                    content: 'text',
                    url: '/path/to/smth',
                    mix: 'baz'
                }).should.equal('<a class="button baz button_theme_normal i-bem" data-bem="{&quot;button&quot;:{}}" role="button" href="/path/to/smth">' +
                        '<span class="button__text">text</span></a>');
            });

            it('should become pseudo', function() {
                execView('button', {
                    content: 'text',
                    mods: {pseudo: 'yes'},
                    url: '/path/to/smth'
                }).should.equal('<a class="button button_pseudo_yes button_theme_pseudo i-bem" data-bem="{&quot;button&quot;:{}}" role="button" href="/path/to/smth">' +
                        '<span class="button__text">text</span></a>');
            });

            it('should use custom theme', function() {
                execView('button', {
                    content: 'text',
                    mods: {theme: 'light'},
                    url: '/path/to/smth'
                }).should.equal('<a class="button button_theme_light i-bem" data-bem="{&quot;button&quot;:{}}" role="button" href="/path/to/smth">' +
                        '<span class="button__text">text</span></a>');
            });

            it('should account for mods', function() {
                execView('button', {
                    content: 'text',
                    mods: {foo: 'bar'},
                    url: '/path/to/smth'
                }).should.equal('<a class="button button_foo_bar button_theme_normal i-bem" data-bem="{&quot;button&quot;:{}}" role="button" href="/path/to/smth">' +
                        '<span class="button__text">text</span></a>');
            });

            it('should be disabled', function() {
                execView('button', {
                    content: 'text',
                    mods: {disabled: 'yes'},
                    url: '/path/to/smth'
                }).should.equal('<a class="button button_disabled_yes button_theme_normal i-bem" data-bem="{&quot;button&quot;:{}}" ' +
                    'role="button" href="/path/to/smth" aria-disabled="true">' +
                        '<span class="button__text">text</span></a>');

            });

            it('shouldn\'t use name and value', function() {
                execView('button', {
                    content: 'text',
                    name: 'foo',
                    value: 'bar',
                    url: '/path/to/smth'
                }).should.equal('<a class="button button_theme_normal i-bem" data-bem="{&quot;button&quot;:{}}" role="button" href="/path/to/smth">' +
                        '<span class="button__text">text</span></a>');
            });

            it('should use attrs', function() {
                execView('button', {
                    content: 'text',
                    attrs: {id: 'quack'},
                    url: '/path/to/smth'
                }).should.equal('<a class="button button_theme_normal i-bem" data-bem="{&quot;button&quot;:{}}" id="quack" role="button" href="/path/to/smth">' +
                        '<span class="button__text">text</span></a>');
            });

        });
    });


})(views.execView);
