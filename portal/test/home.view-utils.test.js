describe('home.view-utils', function() {
    describe('htmlFilter', function() {
        it('не изменяет пустую строку', function() {
            home.htmlFilter('').should.equal('');
        });

        it('не изменяет текст', function() {
            home.htmlFilter('text').should.equal('text');
        });

        it('преобразует спецсимволы', function() {
            home.htmlFilter('<div>').should.equal('&lt;div&gt;');
            home.htmlFilter('<div data-url="yandex/?text=123&abc">')
                .should.equal('&lt;div data-url=&quot;yandex/?text=123&amp;abc&quot;&gt;');
        });
    });

    describe('getBEMParams', function() {
        it('энкодит параметры для data-bem', function () {
            home.getBEMParams({
                button: {
                    timeout: 123
                }
            }).should.equal('{&quot;button&quot;:{&quot;timeout&quot;:123}}');

            home.getBEMParams({
                button: {
                    tooltip: 'Д\'Артаньян, а не Д"Артаньян!'
                }
            }).should.equal('{&quot;button&quot;:{&quot;tooltip&quot;:&quot;Д\'Артаньян, а не Д\\&quot;Артаньян!&quot;}}');
        });
    });

    describe('getBEMClassname', function() {
        it('возвращает нужный набор классов', function () {
            home.getBEMClassname('', {}).should.equal('');
            home.getBEMClassname('button', {}).should.equal('button');
            home.getBEMClassname('button', {}).should.equal('button');
            home.getBEMClassname('button', {
                mix: 'suggest2-form__button'
            }).should.equal('button suggest2-form__button');
            home.getBEMClassname('button', {
                mods: {
                    theme: 'action'
                }
            }).should.equal('button button_theme_action');
            home.getBEMClassname('button', {
                mods: {
                    theme: 'action',
                    size: 'l'
                }
            }).should.equal('button button_theme_action button_size_l');
            home.getBEMClassname('button', {
                mods: {
                    theme: '',
                    size: 'l'
                }
            }).should.equal('button button_size_l');
            home.getBEMClassname('button', {
                mods: {
                    step: 0
                }
            }).should.equal('button button_step_0');
            home.getBEMClassname('button', {
                mix: 'geo-button',
                mods: {
                    step: 0
                }
            }).should.equal('button geo-button button_step_0');
            home.getBEMClassname('button', {
                mix: {block: 'geo-button'}
            }).should.equal('button geo-button');
            home.getBEMClassname('button', {
                mix: {block: 'geo-button', elem: 'text'}
            }).should.equal('button geo-button__text');
            home.getBEMClassname('button', {
                mix: {elem: 'text'}
            }).should.equal('button button__text');
            home.getBEMClassname('button', {
                mix: [
                    {block: 'geo-button', elem: 'text'},
                    {block: 'another-button', elem: 'title'},
                    {block: 'geo-form'},
                    {elem: 'icon'}
                ]
            }).should.equal('button geo-button__text another-button__title geo-form button__icon');
            home.getBEMClassname('button', {
                mix: [
                    {
                        block: 'block-1',
                        mods: {
                            theme: 'normal'
                        }
                    },
                    {
                        block: 'block-2',
                        elem: 'elem-2',
                        mods: {
                            type: 'submit'
                        }
                    }
                ]
            }).should.equal('button block-1 block-1_theme_normal block-2__elem-2');
            home.getBEMClassname('button', {
                mix: [
                    {
                        block: 'block-1',
                        elem: 'elem-1',
                        elemMods: {
                            type: 'one'
                        }
                    },
                    {
                        block: 'block-2',
                        elem: 'elem-2',
                        mods: {
                            mod: 'val' // по методологии если есть элемент, модификаторы блока игнорируются
                        },
                        elemMods: {
                            type: 'two'
                        }
                    }
                ]
            }).should.equal('button block-1__elem-1 block-1__elem-1_type_one block-2__elem-2 block-2__elem-2_type_two');
            home.getBEMClassname('button', {
                mix: [
                    {block: 'block-1'},
                    'block-2'
                ]
            }).should.equal('button block-1 block-2');
        });
    });

    describe('getAttributes', function() {
        it('возвращает атрибуты', function () {
            home.getAttributes().should.equal('');
            home.getAttributes({}).should.equal('');
            home.getAttributes({
                role: 'dialog'
            }).should.equal(' role="dialog"');
            home.getAttributes({
                role: 'dialog',
                tabindex: 0
            }).should.equal(' role="dialog" tabindex="0"');
            home.getAttributes({
                tabindex: 1,
                disabled: ''
            }).should.equal(' tabindex="1"');
            home.getAttributes({
                autofocus: home.emptyAttr
            }).should.equal(' autofocus');
        });
    });
});

