import {
    rewriteTemplateVersions,
    ContainerBlock,
    getTemplateHash,
    TemplateBlock,
    TextBlock,
    thelperVersion,
    thelperWithMemo
} from '../../src';

describe('template helper version', () => {
    it('should add versions', () => {
        const templatesV1 = {
            template1: new TextBlock({
                text: 'text1'
            })
        };

        const templatesV2 = {
            template1: new TextBlock({
                text: 'text2'
            })
        };

        const version1 = thelperVersion(templatesV1);
        const version2 = thelperVersion(templatesV2);

        const {used: usedV1, thelper: thelperV1} = thelperWithMemo<typeof templatesV1>({
            customName: version1
        });

        const {used: usedV2, thelper: thelperV2} = thelperWithMemo<typeof templatesV1>({
            customName: version2
        });

        const block1 = thelperV1.template1({});
        const block2 = thelperV2.template1({});

        expect(block1.type).toMatch('template1/');
        expect(block1.type).toMatch('template1/');
        expect([...usedV1]).toEqual([...usedV2]);
        expect(block1.type).not.toEqual(block2.type);
    });

    it('should rewrite templates', () => {
        let templates = {
            template1: new TextBlock({
                text: 'text1'
            }),
            template2: new ContainerBlock({
                items: [
                    new TemplateBlock('template3'),
                ]
            }),
            template3: new ContainerBlock({
                items: [
                    new TemplateBlock('template4'),
                    new TemplateBlock('template1')
                ]
            }),
            template4: new TemplateBlock('home:block')
        };

        templates = rewriteTemplateVersions(templates).templates;

        expect(templates.template2.items[0].type).toEqual(`template3/${getTemplateHash(templates.template3)}`);
        expect(templates.template3.items[0].type).toEqual(`template4/${getTemplateHash(templates.template4)}`);
    });

    it('should work with common templates', () => {
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

        const {resolvedNames: commonNames, templates: templatesCommonPatched} = rewriteTemplateVersions(templatesCommon);

        let templates = {
            template: new TemplateBlock('commonTemplate1')
        };
        templates = rewriteTemplateVersions(templates, commonNames).templates;

        expect(templates.template.type).toEqual(`commonTemplate1/${getTemplateHash(templatesCommonPatched.commonTemplate1)}`);
    });
});
