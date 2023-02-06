import { loadBemDecl, loadBemDeps, bemEntityName, mergeBemDependency } from './bem-dependency';
import mockFs from 'mock-fs';
import { expect } from 'chai';

describe('bemdecl', () => {
    afterEach(mockFs.restore);

    it('should load bemDecl', () => {
        mockFs({
            'test.bemdecl.js': `
                exports.blocks = [
                    'xapp',
                    {name: 'i-jquery', elems: ['tap']},
                    { name: 'body', mods: { type: 'yaru-mini' } },
                    { block: 'yandex-logo', mods: { lang: ['ru', 'en'] } },
                    { block: 'header3', elem: 'textarea', mod: 'inline', val: true }
                ];
            `,
        });
        expect(loadBemDecl('test.bemdecl.js')).to.include.deep.members([
            { block: 'xapp' },
            { block: 'i-jquery' },
            { block: 'i-jquery', elem: 'tap' },
            { block: 'yandex-logo' },
            { block: 'yandex-logo', mod: 'lang', val: 'ru' },
            { block: 'yandex-logo', mod: 'lang', val: 'en' },
            { block: 'header3', elem: 'textarea', mod: 'inline', val: true },
        ]);
        mockFs.restore();
    });
});

describe('bemdeps', () => {
    afterEach(mockFs.restore);
    it('should load bemdeps', () => {
        mockFs({
            'i-mini-service-worker.deps.js': "({mustDeps: [{name: 'i-mini-util', elems: ['ready']}]})",
            'dialog.deps.js': "({shouldDeps: ['i-mini-channel'], mustDeps: ['i-mini-bem']})",
            'checkbox.deps.js':
                "({shouldDeps: [{elems: ['box', 'control', 'tick', 'label'], mods: {'checked': 'yes', 'size': 's', 'theme': 'normal'}}]})",
            'stream.deps.js': "({ shouldDeps: [{mod: 'stat', val: 'yes', mustDeps: [{mod: 'touch', val: 'yes'}]}]})",
        });

        expect(loadBemDeps('i-mini-service-worker.deps.js').mustDeps).to.have.deep.members([
            { block: 'i-mini-util' },
            { block: 'i-mini-util', elem: 'ready' },
        ]);

        expect(loadBemDeps('dialog.deps.js').shouldDeps).to.have.deep.members([{ block: 'i-mini-channel' }]);

        expect(loadBemDeps('checkbox.deps.js').shouldDeps).to.include.deep.members([
            { block: 'checkbox', elem: 'box' },
            { block: 'checkbox', mod: 'checked', val: 'yes' },
        ]);
    });

    it('should return dependency name', () => {
        expect(bemEntityName({ block: 'block' })).to.deep.equal('block');
        expect(bemEntityName({ block: 'block', mod: 'mod' })).to.deep.equal('block_mod');
        expect(bemEntityName({ block: 'block', mod: 'mod', val: 'val' })).to.deep.equal('block_mod_val');
        expect(bemEntityName({ block: 'block', elem: 'elem' })).to.deep.equal('block__elem');
        expect(bemEntityName({ block: 'block', elem: 'elem', mod: 'mod' })).to.deep.equal('block__elem_mod');
        expect(bemEntityName({ block: 'block', elem: 'elem', mod: 'mod', val: 'val' })).to.deep.equal(
            'block__elem_mod_val'
        );
    });

    it('should merge bem deps', () => {
        let bemDep1 = {
            shouldDeps: [{ block: 'dep1-block1', test: true }, { block: 'remove-me2', elem: 'elem', mod: 'mod' }],
            mustDeps: [],
            noDeps: [{ block: 'remove-me1', elem: 'elem', mod: 'mod' }],
        };
        let bemDep2 = {
            shouldDeps: [{ block: 'dep2-block2' }, { block: 'dep1-block1', test: false }, { block: 'remove-me1', elem: 'elem', mod: 'mod' }],
            noDeps: [{ block: 'remove-me2', elem: 'elem', mod: 'mod' }],
        };
        expect(mergeBemDependency(bemDep1, bemDep2).shouldDeps).to.have.deep.members([
            { block: 'dep1-block1', test: true },
            { block: 'dep2-block2' },
        ]);
        expect(mergeBemDependency(bemDep1, bemDep2). noDeps).to.have.deep.members([
            { block: 'remove-me1', elem: 'elem', mod: 'mod' },
            { block: 'remove-me2', elem: 'elem', mod: 'mod' }
        ]);
    });
});
