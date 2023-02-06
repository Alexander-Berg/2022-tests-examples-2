import { execView } from '@lib/views/execView';

// todo move to imports

describe('common button2', function() {
    describe('as button2', function() {
        it('should render button2', function() {
            expect(execView('Button2', {
                content: 'text'
            })).toEqual('<button class="button2 button2_theme_normal button2_view_classic i-bem" ' +
                    'role="button" type="button" data-bem="{&quot;button2&quot;:{}}">' +
                        '<span class="button2__text">text</span>' +
                    '</button>');
        });

        it('should render pseudo button2', function() {
            expect(execView('Button2', {
                content: 'text',
                mods: { pseudo: 'yes' }
            })).toEqual('<button class="button2 button2_pseudo_yes button2_theme_pseudo button2_view_classic i-bem" ' +
                    'role="button" type="button" data-bem="{&quot;button2&quot;:{}}">' +
                        '<span class="button2__text">text</span>' +
                    '</button>');
        });

        it('should use custom theme', function() {
            expect(execView('Button2', {
                content: 'text',
                mods: { theme: 'light' }
            })).toEqual('<button class="button2 button2_theme_light button2_view_classic i-bem" ' +
                    'role="button" type="button" data-bem="{&quot;button2&quot;:{}}">' +
                        '<span class="button2__text">text</span>' +
                    '</button>');
        });

        it('should be disabled', function() {
            expect(execView('Button2', {
                content: 'text',
                mods: { disabled: 'yes' }
            })).toEqual('<button class="button2 button2_disabled_yes button2_theme_normal button2_view_classic i-bem" ' +
                    'role="button" type="button" disabled="disabled" data-bem="{&quot;button2&quot;:{}}">' +
                        '<span class="button2__text">text</span>' +
                    '</button>');
        });

        it('should account for mods', function() {
            expect(execView('Button2', {
                content: 'text',
                mods: { foo: 'bar' }
            })).toEqual('<button class="button2 button2_foo_bar button2_theme_normal button2_view_classic i-bem" ' +
                    'role="button" type="button" data-bem="{&quot;button2&quot;:{}}">' +
                        '<span class="button2__text">text</span>' +
                    '</button>');
        });

        it('should account for mix', function() {
            expect(execView('Button2', {
                content: 'text',
                mix: 'baz'
            })).toEqual('<button class="button2 baz button2_theme_normal button2_view_classic i-bem" ' +
                    'role="button" type="button" data-bem="{&quot;button2&quot;:{}}">' +
                        '<span class="button2__text">text</span>' +
                    '</button>');
        });

        it('should use name and value', function() {
            expect(execView('Button2', {
                content: 'text',
                name: 'foo',
                value: 'bar'
            })).toEqual('<button class="button2 button2_theme_normal button2_view_classic i-bem" ' +
                    'role="button" type="button" name="foo" value="bar" data-bem="{&quot;button2&quot;:{}}">' +
                        '<span class="button2__text">text</span>' +
                    '</button>');
        });

        it('should use attrs', function() {
            expect(execView('Button2', {
                content: 'text',
                attrs: {
                    id: 'quack'
                }
            })).toEqual('<button class="button2 button2_theme_normal button2_view_classic i-bem" ' +
                    'id="quack" role="button" type="button" data-bem="{&quot;button2&quot;:{}}">' +
                        '<span class="button2__text">text</span>' +
                    '</button>');
        });
    });

    describe('as link', function() {
        it('should render button2', function() {
            expect(execView('Button2', {
                content: 'text',
                url: '/path/to/smth'
            })).toEqual('<a class="button2 button2_theme_normal button2_view_classic i-bem" ' +
                    'role="button" href="/path/to/smth" data-bem="{&quot;button2&quot;:{}}">' +
                        '<span class="button2__text">text</span>' +
                    '</a>');
        });

        it('should use target', function() {
            expect(execView('Button2', {
                content: 'text',
                url: '/path/to/smth',
                target: '_blank'
            })).toEqual('<a class="button2 button2_theme_normal button2_view_classic i-bem" ' +
                    'role="button" href="/path/to/smth" target="_blank" rel="noopener" data-bem="{&quot;button2&quot;:{}}">' +
                        '<span class="button2__text">text</span>' +
                    '</a>');
        });

        it('should account for mix', function() {
            expect(execView('Button2', {
                content: 'text',
                url: '/path/to/smth',
                mix: 'baz'
            })).toEqual('<a class="button2 baz button2_theme_normal button2_view_classic i-bem" role="button" href="/path/to/smth" data-bem="{&quot;button2&quot;:{}}">' +
                        '<span class="button2__text">text</span>' +
                    '</a>');
        });

        it('should become pseudo', function() {
            expect(execView('Button2', {
                content: 'text',
                mods: { pseudo: 'yes' },
                url: '/path/to/smth'
            })).toEqual('<a class="button2 button2_pseudo_yes button2_theme_pseudo button2_view_classic i-bem" ' +
                    'role="button" href="/path/to/smth" data-bem="{&quot;button2&quot;:{}}">' +
                        '<span class="button2__text">text</span>' +
                    '</a>');
        });

        it('should use custom theme', function() {
            expect(execView('Button2', {
                content: 'text',
                mods: { theme: 'light' },
                url: '/path/to/smth'
            })).toEqual('<a class="button2 button2_theme_light button2_view_classic i-bem" ' +
                    'role="button" href="/path/to/smth" data-bem="{&quot;button2&quot;:{}}">' +
                        '<span class="button2__text">text</span>' +
                    '</a>');
        });

        it('should account for mods', function() {
            expect(execView('Button2', {
                content: 'text',
                mods: { foo: 'bar' },
                url: '/path/to/smth'
            })).toEqual('<a class="button2 button2_foo_bar button2_theme_normal button2_view_classic i-bem" ' +
                    'role="button" href="/path/to/smth" data-bem="{&quot;button2&quot;:{}}">' +
                        '<span class="button2__text">text</span>' +
                    '</a>');
        });

        it('should be disabled', function() {
            expect(execView('Button2', {
                content: 'text',
                mods: { disabled: 'yes' },
                url: '/path/to/smth'
            })).toEqual('<a class="button2 button2_disabled_yes button2_theme_normal button2_view_classic i-bem" ' +
                    'role="button" href="/path/to/smth" aria-disabled="true" data-bem="{&quot;button2&quot;:{}}">' +
                        '<span class="button2__text">text</span>' +
                    '</a>');
        });

        it('shouldn\'t use name and value', function() {
            expect(execView('Button2', {
                content: 'text',
                name: 'foo',
                value: 'bar',
                url: '/path/to/smth'
            })).toEqual('<a class="button2 button2_theme_normal button2_view_classic i-bem" ' +
                    'role="button" href="/path/to/smth" data-bem="{&quot;button2&quot;:{}}">' +
                        '<span class="button2__text">text</span>' +
                    '</a>');
        });

        it('should use attrs', function() {
            expect(execView('Button2', {
                content: 'text',
                attrs: { id: 'quack' },
                url: '/path/to/smth'
            })).toEqual('<a class="button2 button2_theme_normal button2_view_classic i-bem" ' +
                    'id="quack" role="button" href="/path/to/smth" data-bem="{&quot;button2&quot;:{}}">' +
                        '<span class="button2__text">text</span>' +
                    '</a>');
        });
    });
});
