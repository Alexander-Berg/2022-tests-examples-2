import {ContainerBlock, copyTemplates, Template, TemplateBlock, TextBlock} from '../../src';

describe('helper functions', () => {
    it('should copy templates', () => {
        const templates = {
            template1: new ContainerBlock({
                items: [
                    new TextBlock({
                        paddings: {
                            right: 4,
                            left: new Template('leftPad')
                        },
                        text: 'test string'
                    })
                ]
            }),
            template2: new TemplateBlock('template1', {
                margins: {left: 7}
            })
        };

        const copy = copyTemplates(templates);
        expect(JSON.stringify(copy)).toEqual(JSON.stringify(templates));
    });
});
