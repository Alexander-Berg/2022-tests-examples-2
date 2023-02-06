import { execView } from '@lib/views/execView';
import { Button } from '@block/button/button.view';

describe('common button', function() {
    describe('as button', function() {
        it('should render button', function() {
            expect(execView(Button, {
                content: 'text'
            })).toEqual('<button class="button button_theme_normal i-bem" data-bem="{&quot;button&quot;:{}}" role="button" type="button">' +
                        '<span class="button__text">text</span></button>');
        });

        it('should render pseudo button', function() {
            expect(execView(Button, {
                content: 'text',
                mods: { pseudo: 'yes' }
            })).toEqual('<button class="button button_pseudo_yes button_theme_pseudo i-bem" data-bem="{&quot;button&quot;:{}}" role="button" type="button">' +
                        '<span class="button__text">text</span></button>');
        });

        it('should use custom theme', function() {
            expect(execView(Button, {
                content: 'text',
                mods: { theme: 'light' }
            })).toEqual('<button class="button button_theme_light i-bem" data-bem="{&quot;button&quot;:{}}" role="button" type="button">' +
                        '<span class="button__text">text</span></button>');
        });

        it('should be disabled', function() {
            expect(execView(Button, {
                content: 'text',
                mods: { disabled: 'yes' }
            })).toEqual(
                '<button class="button button_disabled_yes button_theme_normal i-bem" data-bem="{&quot;button&quot;:{}}" role="button" type="button" disabled="disabled">' +
                        '<span class="button__text">text</span></button>');
        });

        it('should account for mods', function() {
            expect(execView(Button, {
                content: 'text',
                mods: { foo: 'bar' }
            })).toEqual('<button class="button button_foo_bar button_theme_normal i-bem" data-bem="{&quot;button&quot;:{}}" role="button" type="button">' +
                        '<span class="button__text">text</span></button>');
        });

        it('should account for mix', function() {
            expect(execView(Button, {
                content: 'text',
                mix: 'baz'
            })).toEqual('<button class="button baz button_theme_normal i-bem" data-bem="{&quot;button&quot;:{}}" role="button" type="button">' +
                        '<span class="button__text">text</span></button>');
        });

        it('should use name and value', function() {
            expect(execView(Button, {
                content: 'text',
                name: 'foo',
                value: 'bar'
            })).toEqual('<button class="button button_theme_normal i-bem" data-bem="{&quot;button&quot;:{}}" role="button" type="button" name="foo" value="bar">' +
                        '<span class="button__text">text</span></button>');
        });

        it('should use attrs', function() {
            expect(execView(Button, {
                content: 'text',
                attrs: {
                    id: 'quack'
                }
            })).toEqual('<button class="button button_theme_normal i-bem" data-bem="{&quot;button&quot;:{}}" id="quack" role="button" type="button">' +
                    '<span class="button__text">text</span></button>');
        });
    });

    describe('as link', function() {
        it('should render button', function() {
            expect(execView(Button, {
                content: 'text',
                url: '/path/to/smth'
            })).toEqual('<a class="button button_theme_normal i-bem" data-bem="{&quot;button&quot;:{}}" role="button" href="/path/to/smth">' +
                        '<span class="button__text">text</span></a>');
        });

        it('should use target', function() {
            expect(execView(Button, {
                content: 'text',
                url: '/path/to/smth',
                target: '_blank'
            })).toEqual(
                '<a class="button button_theme_normal i-bem" data-bem="{&quot;button&quot;:{}}" role="button" href="/path/to/smth" target="_blank" rel="noopener">' +
                        '<span class="button__text">text</span></a>');
        });

        it('should account for mix', function() {
            expect(execView(Button, {
                content: 'text',
                url: '/path/to/smth',
                mix: 'baz'
            })).toEqual('<a class="button baz button_theme_normal i-bem" data-bem="{&quot;button&quot;:{}}" role="button" href="/path/to/smth">' +
                        '<span class="button__text">text</span></a>');
        });

        it('should become pseudo', function() {
            expect(execView(Button, {
                content: 'text',
                mods: { pseudo: 'yes' },
                url: '/path/to/smth'
            })).toEqual('<a class="button button_pseudo_yes button_theme_pseudo i-bem" data-bem="{&quot;button&quot;:{}}" role="button" href="/path/to/smth">' +
                        '<span class="button__text">text</span></a>');
        });

        it('should use custom theme', function() {
            expect(execView(Button, {
                content: 'text',
                mods: { theme: 'light' },
                url: '/path/to/smth'
            })).toEqual('<a class="button button_theme_light i-bem" data-bem="{&quot;button&quot;:{}}" role="button" href="/path/to/smth">' +
                        '<span class="button__text">text</span></a>');
        });

        it('should account for mods', function() {
            expect(execView(Button, {
                content: 'text',
                mods: { foo: 'bar' },
                url: '/path/to/smth'
            })).toEqual('<a class="button button_foo_bar button_theme_normal i-bem" data-bem="{&quot;button&quot;:{}}" role="button" href="/path/to/smth">' +
                        '<span class="button__text">text</span></a>');
        });

        it('should be disabled', function() {
            expect(execView(Button, {
                content: 'text',
                mods: { disabled: 'yes' },
                url: '/path/to/smth'
            })).toEqual(
                '<a class="button button_disabled_yes button_theme_normal i-bem" data-bem="{&quot;button&quot;:{}}" role="button" href="/path/to/smth" aria-disabled="true">' +
                        '<span class="button__text">text</span></a>');
        });

        it('shouldn\'t use name and value', function() {
            expect(execView(Button, {
                content: 'text',
                name: 'foo',
                value: 'bar',
                url: '/path/to/smth'
            })).toEqual('<a class="button button_theme_normal i-bem" data-bem="{&quot;button&quot;:{}}" role="button" href="/path/to/smth">' +
                        '<span class="button__text">text</span></a>');
        });

        it('should use attrs', function() {
            expect(execView(Button, {
                content: 'text',
                attrs: { id: 'quack' },
                url: '/path/to/smth'
            })).toEqual('<a class="button button_theme_normal i-bem" data-bem="{&quot;button&quot;:{}}" id="quack" role="button" href="/path/to/smth">' +
                        '<span class="button__text">text</span></a>');
        });
    });
});
