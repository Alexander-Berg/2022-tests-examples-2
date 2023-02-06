import {
    ContainerBlock,
    FixedSize,
    IDivData,
    ImageBlock,
    TemplateBlock,
    TemplateCard,
    TextBlock
} from '../../src';
import {Template, Templates} from '../../src/template';

describe('Div templates test', (): void => {
    type NewBlocks = 'title_text' | 'title_menu' | 'footer';

    it('should create simple template', (): void => {
        const templates: Templates<NewBlocks> = new Templates<NewBlocks>([
            {
                type: 'title_text',
                block: new TextBlock({
                    text: new Template('title_text')
                })
            }
        ]);
        expect(templates.blocks).toMatchSnapshot();
    });

    it('should create template with title menu and footer', (): void => {
        const templates: Templates<NewBlocks> = new Templates<NewBlocks>([
            {
                type: 'title_text',
                block: new TextBlock({
                    text: new Template('text'),
                    paddings: {
                        left: 16,
                        top: 12,
                        right: 16
                    },
                    font_size: 18,
                    font_weight: 'medium',
                    line_height: 24,
                    text_color: '#CC000000'
                })
            },
            {
                type: 'title_menu',
                block: new ImageBlock({
                    width: new FixedSize({value: 44}),
                    height: new FixedSize({value: 44}),
                    image_url: 'https://i.imgur.com/qNJQKU8.png'
                })
            },
            {
                type: 'footer',
                block: new TextBlock({
                    text: new Template('footer_text'),
                    font_size: 12,
                    line_height: 16,
                    text_color: '#80000000',
                    margins: {
                        left: 16,
                        right: 16
                    },
                    paddings: {
                        bottom: 12,
                        top: 12
                    },
                    action: new Template('footer_action_link')
                })
            }
        ]);
        expect({templates: templates.blocks}).toMatchSnapshot();
    });

    it('should create card with template which has more than one base template block', (): void => {
        const templates = new Templates([
            {
                type: 'card',
                block: new TemplateBlock('A', {
                    alpha: new Template('opacity')
                })
            },
            {
                type: 'A',
                block: new TemplateBlock('B')
            },
            {
                type: 'B',
                block: new TemplateBlock('C',{
                    orientation: new Template('orient'),
                })
            },
            {
                type: 'C',
                block: new ContainerBlock({
                    items: new Template('content'),
                })
            }
        ]);

        const divData: IDivData = {
            log_id: 'id',
            states: [
                {
                    state_id: 1,
                    div: new TemplateBlock('card', {
                        opacity: 0.5,
                        orient: 'horizontal',
                        content: [new TextBlock({text: 'text'})],
                        margins: {
                            top:1
                        }
                    })
                }
            ]
        };
        new TemplateCard(templates, divData)
    });

    it('should create nested template and card with new property', (): void => {
        const templates = new Templates([
            {
                type: 'district2',
                block: new ContainerBlock({
                    items: [
                        new TemplateBlock('district2_foot_text', {
                            text: new Template('comments_cnt'),
                            my_end: new Template('my_first_end')
                        }),
                        new TemplateBlock('district2_foot_text', {
                            text: new Template('likes_cnt'),
                            my_end: 5
                        })
                    ],
                    column_span: 1
                })
            },
            {
                type: 'district2_foot_text',
                block: new TextBlock({
                    text: new Template('text'),
                    font_size: 13,
                    line_height: 16,
                    text_color: '#999',
                    width: {
                        type: 'wrap_content'
                    },
                    paddings: {
                        left: 5
                    },
                    alignment_horizontal: 'right',
                    ranges: [
                        {
                            start: 0,
                            end: new Template('my_end'),
                            text_color: '#333'
                        }
                    ]
                })
            }

        ]);


        const divData: IDivData = {
            log_id: 'id',
            states: [
                {
                    state_id: 1,
                    div: new TemplateBlock('district2', {
                        comments_cnt: 'some.comments.cnt',
                        likes_cnt: 'some.likes.cnt',
                        my_first_end: 5
                    })
                }
            ]
        };
        expect({templates: templates.blocks}).toMatchSnapshot();

        const card = new TemplateCard(templates, divData);
        expect(card).toMatchSnapshot();
    });
});
