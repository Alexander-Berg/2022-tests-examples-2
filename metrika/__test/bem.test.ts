import { bem } from '../bem';

const blockName = 'test-block';
const elemName = 'test-elem';
const mixName = 'test-mix';
const elemCls = `${blockName}__${elemName}`;
const cls = bem(blockName);

describe('bem css class builder', () => {

    it('should return block class', function () {
        expect(cls()).toBe(blockName);
    });

    it('should return elem class for compact arg format', function () {
        expect(cls(elemName)).toBe(elemCls);
    });

    it('should return elem class for full arg format', function () {
        expect(cls({ elem: elemName })).toBe(elemCls);
    });

    it('should return bloc mods classes', function () {
        const classes = cls({ mods: { color: 'red', disabled: true } }).split(' ').sort();
        expect(classes).toEqual([blockName, `${blockName}_color_red`, `${blockName}_disabled`]);
    });

    it('should ignore undefined, false and empty mods value', function () {
        expect(cls({
            mods: { color: '', disabled: false, undef: undefined }
        })).toBe(blockName);
    });

    it('should return elem with mods classes', function () {
        expect(cls({
            elem: elemName,
            mods: { color: 'red' }
        })).toBe(`${elemCls} ${elemCls}_color_red`);
    });

    it('should return block with mixin classes', function () {
        expect(cls({
            mix: mixName
        })).toBe(`${blockName} ${mixName}`);
    });

    it('should return elem with mixin and mods classes', function () {
        const classes = cls({
            elem: elemName,
            mods: { color: 'red' },
            mix: mixName
        }).split(' ').sort();

        expect(classes).toEqual([elemCls, `${elemCls}_color_red`, mixName]);
    });
});
