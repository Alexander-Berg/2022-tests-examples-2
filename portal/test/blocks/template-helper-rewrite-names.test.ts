import {
    ContainerBlock,
    TemplateBlock,
    rewriteNames,
    TextBlock
} from '../../src';

describe('Rewrite templates', () => {
    it('should shoud preserve home:block', () => {
        const rename = (name: string) => `${name}/test`;
        let templates = {
            block1: new ContainerBlock({
                items: [
                    new TemplateBlock('block2'),
                    new TemplateBlock('block3')
                ]
            }),
            block2: new ContainerBlock({
                items: [
                    new TextBlock({
                        text: 'text1'
                    })
                ]
            }),
            block3: new TemplateBlock('block2'),
            block4: new TemplateBlock('home:block')
        };

        templates = rewriteNames(templates, rename).templates;
        expect(templates).toMatchSnapshot();
    });

    it('should validate template dependencies', () => {
        const templates = {
            template1: new TemplateBlock('a', {
                items: [
                    new TemplateBlock('template2'),
                    new TemplateBlock('b')
                ]
            }),
            template2: new TemplateBlock('home:block')
        };
        expect(() => rewriteNames(templates, x => x))
            .toThrowError(`template 'template1' unsolvable dependencies: 'a','b'`);
    });

    it('should catch cyclic dependecies', () => {
        const templates = {
            template1: new ContainerBlock({
                items: [
                    new TemplateBlock('template2'),
                ]
            }),
            template2: new ContainerBlock({
                items: [
                    new TemplateBlock('template3')
                ]
            }),
            template3: new ContainerBlock({
                items: [
                    new TemplateBlock('template1')
                ]
            })
        };
        expect(() => rewriteNames(templates, x => x))
            .toThrowError('cyclic depdendencies');
    });
});
