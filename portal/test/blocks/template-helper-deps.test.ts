import {ContainerBlock, TemplateBlock, TextBlock} from '../../src';
import {templatesDepsMap} from '../../src/template-helper-deps';

describe('template deps', () => {
    it('should find templates deps', () => {
        const templates = {
            template1: new TemplateBlock('home:block', {
                items: [
                    new TemplateBlock('template2'),
                    new TemplateBlock('template5')
                ]
            }),
            template2: new ContainerBlock({
                items: [
                    new TemplateBlock('template3')
                ]
            }),
            template3: new ContainerBlock({
                items: [
                    new TemplateBlock('home:test'),
                    new ContainerBlock({
                        items: [
                            new TemplateBlock('template4')
                        ]
                    })
                ]
            }),
            template4: new TextBlock({
                text: 'test'
            }),
            template5: new TextBlock({
                text: 'test'
            })
        };

        const depsMap = templatesDepsMap(templates);

        expect(new Set(depsMap.template1)).toEqual(new Set(['template1', 'template2', 'template3', 'template4', 'template5']));
        expect(new Set(depsMap.template2)).toEqual(new Set(['template2', 'template3', 'template4']));
        expect(new Set(depsMap.template3)).toEqual(new Set(['template3', 'template4']));
        expect(new Set(depsMap.template4)).toEqual(new Set(['template4']));
    });

    it('should find common templates dependencies', () => {
        const templatesCommon = {
            commonTemplate1: new ContainerBlock({
                items: [
                    new TemplateBlock('commonTemplate2')
                ]
            }),
            commonTemplate2: new TemplateBlock('commonTemplate3'),
            commonTemplate3: new TextBlock({text: 'text'}),
            commonTemplate4: new TextBlock({text: 'text'})
        };

        const templates = {
            template: new TemplateBlock('commonTemplate1')
        };

        const commonDeps = templatesDepsMap(templatesCommon);
        const depsMap = templatesDepsMap(templates, commonDeps);
        expect(new Set(depsMap.template)).toEqual(new Set(['template', 'commonTemplate1', 'commonTemplate2', 'commonTemplate3']));
    });
});
