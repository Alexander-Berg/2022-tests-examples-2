import {
    ContainerBlock,
    Template,
    TextBlock,
    templateHelper,
    ImageBlock,
    GalleryBlock,
    ImageBackground,
    GradientBackground,
    SolidBackground,
    TemplateBlock,
    FixedSize,
    expression
} from '../../src';

describe('templateHelper', () => {
    it('should create TemplateBlock with parameters', () => {
        const templates = {
            template1: new ContainerBlock({
                paddings: new Template('vPaddings'),
                items: [
                    new TextBlock({
                        text: 'text',
                        max_lines: new Template('vMaxlines'),
                        paddings: {
                            left: new Template('leftP'),
                            right: 5
                        }
                    }),
                    new TextBlock({
                        text: new Template('vText1')
                    }),
                    new TextBlock({
                        text: new Template('vText2')
                    }),
                    new ImageBlock({
                        image_url: expression('@{image}'),
                        margins: {
                            left: expression('@{left}')
                        }
                    })
                ]
            }),
            template2: new GalleryBlock({
                items: [
                    new TextBlock({
                        text: 'string',
                        action: new Template('action1')
                    }),
                    new ContainerBlock({
                        items: [
                            new TextBlock({
                                text: new Template('text2'),
                                action: {log_id: 'test', url: 'test'}
                            })
                        ]
                    })
                ]
            }),
            template3: new ContainerBlock({
                items: [
                    new ImageBlock({
                        height: new FixedSize({value: 50}),
                        width: new FixedSize({value: 50}),
                        image_url: 'imageSrc'
                    })
                ],
                background: [
                    new SolidBackground({color: '#0000000d'}),
                    new ImageBackground({
                        image_url: new Template('img'),
                        scale: new Template('imgScale')
                    }),
                    new GradientBackground({
                        angle: new Template('gAngle'),
                        colors: [
                            '#99000000',
                            '#66000000',
                            '#33000000',
                            '#00000000'
                        ]
                    })
                ]
            }),
            template4: new TemplateBlock('template3', {
                items: [
                    new TemplateBlock('template1', {
                        vPaddings: {}
                    }),
                    new TemplateBlock('template2')
                ]
            }),
            template6: new ContainerBlock({
                items: [
                    new TemplateBlock('template5')
                ]
            }),
            template5: new ImageBlock({
                image_url: new Template('imgUrl')
            })
        };
        const helper = templateHelper(templates);
        const block = helper.template1({
            vText1: 'test',
            vText2: 'test',
            vMaxlines: 2,
            vPaddings: {left: 4},
            leftP: 4,
        });
        expect(block).toMatchSnapshot();

        const block2 = helper.template2({
            action1: {log_id: 'action', url: 'url'},
            text2: 'text2'
        });
        expect(block2).toMatchSnapshot();

        const block3 = helper.template3({
            gAngle: 90,
            img: 'img',
            imgScale: 'fill'
        });
        expect(block3).toMatchSnapshot();

        const block4 = helper.template4({
            gAngle: 90,
            img: 'img',
            imgScale: 'fill',
            vText1: '1',
            vText2: '2',
            text2: '2',
            action1: {log_id: 'action', url: 'url'},
            vMaxlines: 1,
            leftP: 1,
        });
        expect(block4).toMatchSnapshot();

        helper.template6({
            imgUrl: 'imgUrl'
        });
    });
});
