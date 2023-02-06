import mockFs from 'mock-fs';
import { BemLevel } from './bem-level';
import { expect } from 'chai';
import { viewJsTemplates, viewHtmlTemplates } from './view-helpers';
const fs = {
    '/morda/tmpl/common/blocks': {
        'b-link': {
            'b-link.view.html': `
                <!--b-link__text-->
                <span class="b-link__text">[% content %]</span>
            
                <!--b-link__inner-->
                <span class="b-link__inner">[% content %]</span>
            
                <!--b-link-pseudoinner-->
                [% b-link %]
            `,
            'b-link.view.js': `views('b-link', function(data) {});`,
            'b-link.view.test.js': '',
        },
        checkbox: {
            __box: {},
            __label: {},
            __control: {
                'checkbox__control.ie7.css': '',
            },
            __tick: {
                'checkbox__tick.css': '',
                '_test-mod': {
                    'checkbox__tick_test-mod_val1.js': '',
                    'checkbox__tick_test-mod_val2.js': '',
                },
                '_test-mod2': {
                    'checkbox__tick_test-mod2.js': '',
                    'checkbox__tick_test-mod2.test.js': '',
                },
            },
            _checked: {},
            _size: {
                'checkbox_size_s.styl': '',
            },
            _theme: {
                'checkbox_theme_normal.ie7.css': '',
                'checkbox_theme_sticker.styl': '',
            },
            'checkbox.css': '',
            'checkbox.deps.js': `
                ({
                    shouldDeps:[
                        {elems: ['box', 'control', 'tick', 'label'], mods: {'checked': 'yes', 'size': 's', 'theme': 'normal'}}
                    ]
                })`,
            'checkbox.view.html': '',
            'checkbox.view.js': '',
        },
    },
};

describe('BemLevel', () => {
    beforeEach(() => {
        mockFs(fs);
    });
    afterEach(mockFs.restore);

    it('should resolve entities', () => {
        const bemLevel = new BemLevel('@common', '/morda/tmpl/common/blocks');
        expect(bemLevel.getEntity({ block: 'b-link' })).not.equal(undefined);
        expect(bemLevel.getEntity({ block: 'checkbox' })).not.equal(undefined);
        expect(bemLevel.getEntity({ block: 'checkbox', elem: 'control' })).equal(undefined);
        expect(bemLevel.getEntity({ block: 'checkbox', elem: 'tick', mod: 'test-mod', val: 'val1' })).not.equal(undefined);
        mockFs.restore();
    });

    it('should list files', () => {
        const bemLevel = new BemLevel('@common', '/morda/tmpl/common/blocks');

        expect(bemLevel.getEntity({ block: 'checkbox', elem: 'tick', mod: 'test-mod2' }).files()).to.deep.equal([
            '/morda/tmpl/common/blocks/checkbox/__tick/_test-mod2/checkbox__tick_test-mod2.js',
        ]);
        expect(
            bemLevel.getEntity({ block: 'checkbox', elem: 'tick', mod: 'test-mod', val: 'val1' }).files()
        ).to.deep.equal(['/morda/tmpl/common/blocks/checkbox/__tick/_test-mod/checkbox__tick_test-mod_val1.js']);
    });

    it('should list views', () => {
        expect(viewJsTemplates('/morda/tmpl/common/blocks/b-link/b-link.view.js')).to.deep.equal(['BLink']);
        expect(viewHtmlTemplates('/morda/tmpl/common/blocks/b-link/b-link.view.html'))
            .to.deep.equal(['BLink__text', 'BLink__inner', 'BLinkPseudoinner']);
    });

    it('should list entity dependencies', () => {
        const bemLevel = new BemLevel('@common', '/morda/tmpl/common/blocks');
        const entity = bemLevel.getEntity({ block: 'checkbox' });
        const deps = entity.deps();
        expect(deps.shouldDeps).to.have.deep.members([
            { block: 'checkbox', elem: 'box' },
            { block: 'checkbox', elem: 'control' },
            { block: 'checkbox', elem: 'tick' },
            { block: 'checkbox', elem: 'label' },
            { block: 'checkbox', mod: 'checked' },
            { block: 'checkbox', mod: 'checked', val: 'yes' },
            { block: 'checkbox', mod: 'size' },
            { block: 'checkbox', mod: 'size', val: 's' },
            { block: 'checkbox', mod: 'theme' },
            { block: 'checkbox', mod: 'theme', val: 'normal' },
        ]);
    });
});
