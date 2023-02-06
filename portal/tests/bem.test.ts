import { getBEMClassname, getBEMParams } from '../bem';

describe('bem', () => {
    describe('getBEMParams', function() {
        test('энкодит параметры для data-bem', function() {
            expect(getBEMParams({
                button: {
                    timeout: 123
                }
            })).toEqual('{&quot;button&quot;:{&quot;timeout&quot;:123}}');

            expect(getBEMParams({
                button: {
                    tooltip: 'Д\'Артаньян, а не Д"Артаньян!'
                }
            })).toEqual('{&quot;button&quot;:{&quot;tooltip&quot;:&quot;Д\'Артаньян, а не Д\\&quot;Артаньян!&quot;}}');
        });
    });

    describe('getBEMClassname', function() {
        test('возвращает нужный набор классов', function() {
            expect(getBEMClassname('', {})).toEqual('');
            expect(getBEMClassname('button', {})).toEqual('button');
            expect(getBEMClassname('button', {})).toEqual('button');
            expect(getBEMClassname('button', {
                mix: 'suggest2-form__button'
            })).toEqual('button suggest2-form__button');
            expect(getBEMClassname('button', {
                mods: {
                    theme: 'action'
                }
            })).toEqual('button button_theme_action');
            expect(getBEMClassname('button', {
                mods: {
                    theme: 'action',
                    size: 'l'
                }
            })).toEqual('button button_theme_action button_size_l');
            expect(getBEMClassname('button', {
                mods: {
                    theme: '',
                    size: 'l'
                }
            })).toEqual('button button_size_l');
            expect(getBEMClassname('button', {
                mods: {
                    step: 0
                }
            })).toEqual('button button_step_0');
            expect(getBEMClassname('button', {
                mix: 'geo-button',
                mods: {
                    step: 0
                }
            })).toEqual('button geo-button button_step_0');
            expect(getBEMClassname('button', {
                mix: { block: 'geo-button' }
            })).toEqual('button geo-button');
            expect(getBEMClassname('button', {
                mix: { block: 'geo-button', elem: 'text' }
            })).toEqual('button geo-button__text');
            expect(getBEMClassname('button', {
                mix: { elem: 'text' }
            })).toEqual('button button__text');
            expect(getBEMClassname('button', {
                mix: [
                    { block: 'geo-button', elem: 'text' },
                    { block: 'another-button', elem: 'title' },
                    { block: 'geo-form' },
                    { elem: 'icon' }
                ]
            })).toEqual('button geo-button__text another-button__title geo-form button__icon');
            expect(getBEMClassname('button', {
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
            })).toEqual('button block-1 block-1_theme_normal block-2__elem-2');
            expect(getBEMClassname('button', {
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
            })).toEqual('button block-1__elem-1 block-1__elem-1_type_one block-2__elem-2 block-2__elem-2_type_two');
            expect(getBEMClassname('button', {
                mix: [
                    { block: 'block-1' },
                    'block-2'
                ]
            })).toEqual('button block-1 block-2');
        });
    });
});
