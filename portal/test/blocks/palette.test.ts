import {
    ContainerBlock,
    FixedSize,
    SolidBackground,
    TextBlock,
    createPaletteTools,
    withOpacity
} from '../../src';

describe('Palette', () => {
    const paletteTools = createPaletteTools({
        a: {
            b: {
                dark: '#000000',
                light: '#ffffff'
            }
        },
        c: {
            dark: '#ababab',
            light: '#dedede'
        }
    }, 'prefix');

    it('should create palette', () => {
        expect(paletteTools.palette).toEqual({
            dark: [
                {
                    name: 'prefix.c',
                    color: '#ababab'
                },
                {
                    name: 'prefix.a.b',
                    color: '#000000'
                }
            ],
            light: [
                {
                    name: 'prefix.c',
                    color: '#dedede'
                },
                {
                    name: 'prefix.a.b',
                    color: '#ffffff'
                }
            ]
        });

    });

    it('should provide semantic namespace', () => {
        expect(paletteTools.getColorNamespace({isPaletteSupported: true}).a.b).toEqual('@{prefix.a.b}');
    });

    it('should provide fallback namespace', () => {
        expect(paletteTools.getColorNamespace({isPaletteSupported: false}).a.b).toEqual('#ffffff');
    });

    it('should compute opacity with #RRGGBB colors', () => {
        expect(withOpacity('#000000', 1)).toEqual('#ff000000');
        expect(withOpacity('#ffffff', 0.5)).toEqual('#80ffffff');
        expect(withOpacity('#000000', 0)).toEqual('#00000000');
    });

    it('should compute opacity with #RGB colors', () => {
        expect(withOpacity('#000', 1)).toEqual('#f000');
        expect(withOpacity('#fff', 0.5)).toEqual('#8fff');
        expect(withOpacity('#000', 0)).toEqual('#0000');
    });

    it('should replace current opacity', () => {
        expect(withOpacity('#12ffffff', 0.5)).toEqual('#80ffffff');
        expect(withOpacity('#4fff', 0.5)).toEqual('#8fff');
    });

    it('should throw error on unsupported color/opacity format', () => {
        expect(() => withOpacity('#00001', 1)).toThrowError();
        expect(() => withOpacity('#000', 1.1)).toThrowError();
    });

    it('should rewrite colors in Templates', () => {
        const colors = paletteTools.getColorNamespace({isPaletteSupported: true});
        const templates = {
            testBlock: new ContainerBlock({
                height: new FixedSize({value: 34}),
                background: [
                    new SolidBackground({
                        color: colors.a.b
                    })
                ],
                items: [
                    new TextBlock({
                        text: 'test',
                        text_color: colors.c
                    })
                ]
            })
        };

        expect(paletteTools.rewriteTemplateColors(templates)).toMatchSnapshot();
    });
});
