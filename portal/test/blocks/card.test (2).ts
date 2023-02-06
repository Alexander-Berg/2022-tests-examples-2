import {
    ContainerBlock,
    IDivData,
    FixedSize,
    GalleryBlock,
    GradientBackground,
    ImageBlock,
    MatchParentSize,
    SolidBackground,
    TabsBlock,
    TemplateBlock,
    TextBlock,
    WrapContentSize,
    ImageBackground,
    Templates,
    Template,
    TemplateCard,
    GifBlock,
    GridBlock,
    SeparatorBlock,
    DivStateBlock
} from '../../src';

describe('Div card test', (): void => {
    const textBlock = new TextBlock({
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
    });

    type NewBlocks =
        | 'title_text'
        | 'title_text'
        | 'title_menu'
        | 'footer'
        | 'poi_card'
        | 'star'
        | 'star_full'
        | 'star_half'
        | 'star_empty'
        | 'poi_gallery_item'
        | 'gallery_tail_light'
        | 'star_half'
        | 'star_empty'
        | 'poi_gallery_item'
        | 'gallery_tail_light'
        | 'znatoki_card'
        | 'znatoki_question';

    const commonTemplate = new Templates([
        {
            type: 'title_text',
            block: textBlock
        },
        {
            type: 'title_menu',
            block: new ImageBlock({
                width: new FixedSize({value: 44}),
                height: new FixedSize({value: 44}),
                image_url: 'https://i.imgur.com/qNJQKU8.png'
            })
        }
    ]);

    const templates: Templates<NewBlocks> = new Templates<NewBlocks>([
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
        },
        {
            type: 'poi_card',
            block: new ContainerBlock({
                orientation: 'vertical',
                background: [
                    new SolidBackground({
                        color: '#FFFFFF'
                    })
                ],
                items: [
                    new ContainerBlock({
                        orientation: 'horizontal',
                        items: new Template('title_items')
                    }),
                    new TabsBlock({
                        switch_tabs_by_content_swipe_enabled: 0,
                        title_paddings: {
                            left: 12,
                            right: 12,
                            bottom: 8
                        },
                        tab_title_style: {
                            font_weight: 'medium'
                        },
                        items: new Template('tab_items_link'),
                        dynamic_height: 1
                    }),
                    new TemplateBlock('footer')
                ]
            })
        },
        {
            type: 'star',
            block: new ImageBlock({
                width: new FixedSize({value: 14}),
                height: new FixedSize({value: 14}),
                image_url: new Template('image_url')
            })
        },
        {
            type: 'star_full',
            block: new TemplateBlock('star', {
                image_url:
                    'https://avatars.mds.yandex.net/get-bass/787408/poi_48x48_ee9550bc195fdc5d7c1d281ea5d8d776320345e0a67b0663c4fdde14e194393b.png/orig'
            })
        },
        {
            type: 'star_half',
            block: new TemplateBlock('star', {
                image_url:
                    'https://avatars.mds.yandex.net/get-bass/469429/poi_48x48_188933e7030027690ed55b5614b60fa77e0e4b50b86dde48d166714096ed0b0e.png/orig'
            })
        },
        {
            type: 'star_empty',
            block: new TemplateBlock('star', {
                image_url:
                    'https://avatars.mds.yandex.net/get-bass/397492/poi_48x48_4ce4cec5ea8f8336bc3792a4899c1e9958531fcf9f8aabc4dd319ddaf5deafa0.png/orig'
            })
        },
        {
            type: 'poi_gallery_item',
            block: new ContainerBlock({
                orientation: 'vertical',
                width: new FixedSize({value: 244}),
                height: new FixedSize({value: 240, unit: 'sp'}),
                border: {
                    corner_radius: 6
                },
                paddings: {
                    left: 12,
                    right: 12,
                    top: 16,
                    bottom: 14
                },
                background: [
                    new ImageBlock({
                        content_alignment_vertical: 'top',
                        image_url: new Template('background_url')
                    }),
                    new GradientBackground({
                        angle: 270,
                        colors: ['#00293445', '#293445']
                    })
                ],
                action: new Template('poi_gallery_item_action_link'),

                items: [
                    new TextBlock({
                        text: new Template('badge_text'),
                        font_size: 13,
                        text_color: '#fff',
                        line_height: 16,
                        width: new WrapContentSize(),
                        max_lines: 1,
                        alignment_horizontal: 'right',
                        background: [new SolidBackground({color: '#3A4F71'})],
                        border: {
                            corner_radius: 4
                        },
                        paddings: {
                            bottom: 4,
                            top: 4,
                            left: 6,
                            right: 6
                        }
                    }),
                    new TextBlock({
                        text: new Template('place_category'),
                        font_size: 11,
                        text_color: '#FFFFFF',
                        line_height: 12,
                        max_lines: 6,
                        letter_spacing: 0.75,
                        text_alignment_vertical: 'bottom',
                        height: new MatchParentSize({weight: 1}),
                        paddings: {
                            top: 8
                        }
                    }),
                    new TextBlock({
                        text: new Template('place_title'),
                        font_size: 16,
                        text_color: '#FFFFFF',
                        line_height: 20,
                        max_lines: 6,
                        paddings: {
                            top: 8
                        }
                    }),
                    new TextBlock({
                        text: new Template('address'),
                        font_size: 13,
                        text_color: '#99FFFFFF',
                        line_height: 16,
                        max_lines: 6,
                        paddings: {
                            top: 8
                        }
                    }),
                    new ContainerBlock({
                        items: new Template('poi_stars'),
                        orientation: 'horizontal',
                        content_alignment_vertical: 'center',
                        paddings: {
                            top: 8
                        }
                    }),
                    new ContainerBlock({
                        orientation: 'horizontal',
                        content_alignment_vertical: 'center',
                        paddings: {
                            top: 11
                        },
                        items: [
                            new TextBlock({
                                text: new Template('time'),
                                font_size: 11,
                                text_color: '#99FFFFFF',
                                line_height: 12,
                                max_lines: 1,
                                letter_spacing: 0.75,
                                width: new MatchParentSize({weight: 1})
                            }),
                            new ImageBlock({
                                image_url: 'http://imgur.com/7y1xr5j.png',
                                width: new FixedSize({value: 16}),
                                height: new FixedSize({value: 16})
                            }),
                            new TextBlock({
                                text: new Template('distance'),
                                font_size: 13,
                                text_color: '#99FFFFFF',
                                max_lines: 1,
                                width: new WrapContentSize()
                            })
                        ]
                    })
                ]
            })
        },
        {
            type: 'gallery_tail_light',
            block: new ContainerBlock({
                width: new FixedSize({value: 104}),
                height: new MatchParentSize({weight: 0}),
                action: new Template('gallery_tail_action_link'),
                content_alignment_horizontal: 'center',
                content_alignment_vertical: 'center',
                items: [
                    new ImageBlock({
                        width: new FixedSize({value: 40}),
                        height: new FixedSize({value: 40}),
                        border: {
                            corner_radius: 20,
                            stroke: {
                                color: '#DCDEE0'
                            }
                        },
                        background: [new SolidBackground({color: '#ffffff'})],
                        placeholder_color: '#00ffffff',
                        image_url: 'https://i.imgur.com/CPmGi24.png'
                    }),
                    new TextBlock({
                        text: new Template('tail_text_link'),
                        font_size: 14,
                        text_color: '#6b7a80',
                        line_height: 16,
                        text_alignment_horizontal: 'center',
                        height: new WrapContentSize(),
                        paddings: {
                            left: 0,
                            right: 0,
                            top: 10,
                            bottom: 0
                        }
                    })
                ]
            })
        }
    ]);

    templates.add(commonTemplate);

    templates.update('footer', new TextBlock({
        text: new Template('footer_text'),
        font_size: 14,
        line_height: 16,
        text_color: '#999',
        margins: {
            left: 16,
            right: 16
        },
        paddings: {
            bottom: 12,
            top: 12
        },
        action: new Template('footer_action_link')
    }));

    const znatokiTemplates: Templates<NewBlocks> = new Templates<NewBlocks>([
        {
            type: 'znatoki_question',
            block: new TextBlock({
                text: new Template('question_title'),
                alignment_vertical: 'center',
                font_size: 16,
                line_height: 20,
                text_color: '#ffffff',
                height: new WrapContentSize(),
                paddings: {left: 12, right: 12, top: 8, bottom: 8},
                max_lines: 4,
                font_weight: 'bold'
            })

        },
        {
            type: 'znatoki_card',
            block: new ContainerBlock({
                orientation: 'vertical',
                height: new WrapContentSize(),
                width: new FixedSize({value: 272}),
                border: {corner_radius: 6, stroke: {color: '#DCDEE0', width: 1}},
                background: [new SolidBackground({color: '#ffffff'})],
                items: [
                    new ContainerBlock({
                        background: [
                            new SolidBackground({color: '#e9edf2'}),
                            new ImageBackground({image_url: new Template('question_cover_url')}),
                            new SolidBackground({color: '#80000000'})
                        ],
                        height: new FixedSize({value: 96, unit: 'sp'}),
                        width: new MatchParentSize({}),
                        content_alignment_vertical: 'center',
                        items: [new TemplateBlock('znatoki_question')]
                    }),
                    new ContainerBlock({
                        paddings: {left: 12, right: 12, top: 12, bottom: 12},
                        items: [
                            new ContainerBlock({
                                orientation: 'horizontal',
                                content_alignment_vertical: 'center',
                                paddings: {bottom: 4},
                                items: [
                                    new ImageBlock({
                                        image_url: new Template('author_avater_url'),
                                        width: new FixedSize({value: 32}),
                                        height: new FixedSize({value: 32}),
                                        border: {corner_radius: 16},
                                        alignment_vertical: 'center'
                                    }),
                                    new ContainerBlock({
                                        paddings: {left: 8, right: 8},
                                        items: [
                                            new TextBlock({
                                                text: new Template('author_name')
                                            })
                                        ]
                                    })
                                ]
                            }),
                            new TextBlock({
                                text: new Template('answer_text'),
                            }),
                            new ContainerBlock({
                                orientation: 'horizontal',
                                content_alignment_vertical: 'center',
                                items: [
                                    new ImageBlock({
                                        image_url: 'https://avatars.mds.yandex.net/get-znatoki/1649112/2a0000016c29fff42cb526006c69e437cd43/orig',
                                        width: new FixedSize({value: 16}),
                                        height: new FixedSize({value: 16}),
                                        alignment_vertical: 'center',
                                        placeholder_color: '#00ffffff',
                                        alpha: 0.24
                                    }),
                                    new TextBlock({
                                        text: new Template('answers_more')
                                    })
                                ]
                            })
                        ]
                    }),
                ]
            }),
        }
    ]);

    it('should create full card poi with template', (): void => {
        const divData: IDivData = {
            log_id: 'poi_card',
            states: [
                {
                    state_id: 1,
                    div: new TemplateBlock('poi_card', {
                        title_items: [
                            new TemplateBlock('title_text', {
                                text: 'Рядом с вами'
                            }),
                            new TemplateBlock('title_menu', {
                                action: {
                                    log_id: 'menu',
                                    menu_items: [
                                        {
                                            text: 'Настройки ленты',
                                            action: {
                                                url: 'http://ya.ru',
                                                log_id: 'settings'
                                            }
                                        },
                                        {
                                            text: 'Скрыть карточку',
                                            action: {
                                                url: 'http://ya.ru',
                                                log_id: 'hide'
                                            }
                                        }
                                    ]
                                }
                            })
                        ],
                        footer_text: 'ОТКРЫТЬ КАРТЫ',
                        tab_items_link: [
                            {
                                title: 'ПОПУЛЯРНОЕ',
                                div: new GalleryBlock({
                                    width: new MatchParentSize({weight: 40}),
                                    height: new FixedSize({value: 240, unit: 'sp'}),
                                    paddings: {
                                        left: 16,
                                        right: 16
                                    },
                                    items: [
                                        new TemplateBlock('poi_gallery_item', {
                                            badge_text: 'Лучшее',
                                            background_url:
                                                'https://avatars.mds.yandex.net/get-pdb/1340633/88a085e7-7254-43ff-805a-660b96f0e6ce/s1200?webp=false',
                                            place_category: 'РЕСТОРАН',
                                            place_title: 'Кулинарная лавка',
                                            address: 'улица Тимура Фрунзе, 11, корп. 8',
                                            time: 'ДО 23:00',
                                            distance: '150м',
                                            poi_stars: [
                                                {
                                                    type: 'star_full'
                                                },
                                                {
                                                    type: 'star_full'
                                                },
                                                {
                                                    type: 'star_full'
                                                },
                                                {
                                                    type: 'star_half'
                                                },
                                                {
                                                    type: 'star_empty'
                                                }
                                            ],
                                            poi_gallery_item_action_link: 'ya.ru'
                                        }),
                                        new TemplateBlock('poi_gallery_item', {
                                            badge_text: 'Лучшее',
                                            background_url:
                                                'https://avatars.mds.yandex.net/get-pdb/1340633/88a085e7-7254-43ff-805a-660b96f0e6ce/s1200?webp=false',
                                            place_category: 'КОНЦЕРТ',
                                            place_title: 'Black Label Society',
                                            address: 'чт 15 февраля',
                                            time: 'Главclub Green Concert',
                                            distance: '150м',
                                            poi_stars: [],
                                            poi_gallery_item_action_link: 'ya.ru'
                                        }),
                                        new TemplateBlock('gallery_tail_light', {
                                            tail_text_link: 'Ещё на картах',
                                            visibility_action: {
                                                log_id: 'a66',
                                                visibility_duration: 10000
                                            },
                                            gallery_tail_action_link: 'ya.ru'
                                        })
                                    ]
                                })
                            }
                        ],
                        footer_action_link: 'ya.ru'
                    })
                }
            ]
        };
        const card = new TemplateCard(templates, divData);
        expect(card).toMatchSnapshot();
    });


    it('should create part of znatoki card with style template', (): void => {
        const divData: IDivData = {
            log_id: 'znatoki_card',
            states: [
                {
                    state_id: 1,
                    div: new TemplateBlock('znatoki_card', {
                        author_name: 'name',
                        question_cover_url: 'ya.ru',
                        question_title: 'title',
                        author_avater_url: 'ya.ru',
                        answer_text: 'text',
                        answers_more: 'more'
                    })
                }
            ]
        };
        const card = new TemplateCard(znatokiTemplates, divData);
        expect(card).toMatchSnapshot();
    });

    it('should throw not found error', (): void => {
        const divData: IDivData = {
            log_id: 'poi_card',
            states: [
                {
                    state_id: 1,
                    div: new TemplateBlock('poi_card_demo', {
                        footer_text: 'ОТКРЫТЬ КАРТЫ'
                    })
                }
            ]
        };

        expect(() => new TemplateCard(templates, divData))
            .toThrowError('Template poi_card_demo not found');
    });

    it('should throw invalid property error', (): void => {
        const divData: IDivData = {
            log_id: 'poi_card',
            states: [
                {
                    state_id: 1,
                    div: new TemplateBlock('poi_card', {
                        footer_text_demo: 'ОТКРЫТЬ КАРТЫ',
                        title_items: [],
                        tab_items_link: 'ya.ru',
                        footer_text: '',
                        footer_action_link: 'p'
                    })
                }
            ]
        };
        expect(() => new TemplateCard(templates, divData))
            .toThrowError('Property footer_text_demo does not exist in template block poi_card');
    });

    it('should throw error if try to add an existing template to the current list', (): void => {
        expect(() => commonTemplate.add(new Templates([
            {
                type: 'title_text',
                block: textBlock
            }
        ])))
            .toThrowError('The template title_text is already exist. Templates:[title_text,title_menu]!');
    });

    it('should throw not implemented error', (): void => {
        const divData: IDivData = {
            log_id: 'poi_card',
            states: [
                {
                    state_id: 1,
                    div: new TemplateBlock('znatoki_card', {
                        //author_name: 'name',
                        question_cover_url: 'ya.ru',
                        question_title: 'title',
                        author_avater_url: 'ya.ru',
                        author_about: 'about',
                        answer_text: 'text',
                        answers_more: 'more',
                    })
                }
            ]
        };

        expect(() => new TemplateCard(znatokiTemplates, divData))
            .toThrowError('The properties author_name of template znatoki_card is not implemented!');
    });

    it('should throw not implemented error if the prop from child template is called from the base template', (): void => {
        const divData: IDivData = {
            log_id: 'poi_card',
            states: [
                {
                    state_id: 1,
                    div: new TemplateBlock('znatoki_card', {
                        author_name: 'name',
                        question_cover_url: 'ya.ru',
                        //question_title: 'title',
                        author_avater_url: 'ya.ru',
                        author_about: 'about',
                        answer_text: 'text',
                        answers_more: 'more',
                    })
                }
            ]
        };
        expect(() => new TemplateCard(znatokiTemplates, divData))
            .toThrowError('The properties question_title of template znatoki_card is not implemented!');
    });

    it('should create market card with templated nested props', (): void => {

        type TBlocks =
            | 'title_text'
            | 'market_card'
            | 'market_item'
            | 'market_card_container';


        const title = new TextBlock({
            text: new Template('text'),
            paddings: {
                left: 22,
                top: 14,
                right: 22,
                bottom: 4
            },
            font_size: 18,
            font_weight: 'bold',
            text_color: '#000000'
        });

        const templates: Templates<TBlocks> = new Templates<TBlocks>([
            {
                type: 'title_text',
                block: title
            },
            {
                type: 'market_card_container',
                block: new ContainerBlock({
                    alignment_vertical: new Template('align'),
                    orientation: 'vertical',
                    background: [
                        new SolidBackground({
                            color: new Template('bg_color')
                        })
                    ],
                    items: new Template('content'),
                })
            },
            {
                type: 'market_card',
                block: new TemplateBlock('market_card_container', {
                    align: 'center',
                    content: [
                        new ContainerBlock({
                            orientation: 'horizontal',
                            items: new Template('title_items'),
                        }),
                        new GalleryBlock({
                            items: new Template('cards')
                        })
                    ],
                })
            },
            {
                type: 'market_item',
                block: new ContainerBlock({
                    orientation: 'vertical',
                    width: new FixedSize({value: 148}),
                    height: new FixedSize({value: 222, unit: 'sp'}),
                    border: {
                        corner_radius: 6,
                        has_shadow: 1
                    },
                    margins: {
                        top: 10,
                        bottom: 15
                    },
                    action: new Template('action_link'),

                    items: [
                        new ImageBlock({
                            image_url: new Template('logo'),
                            width: new MatchParentSize(),
                            height: new FixedSize({value: 108}),
                            scale: 'fit',
                            margins: {
                                top: new Template('logo_margin_top'),
                                bottom: 6
                            }
                        }),
                        new TextBlock({
                            text: new Template('price'),
                            font_size: 14,
                            text_color: '#000000',
                            line_height: 18,
                            margins: {
                                top: 6,
                                left: 12
                            },
                            font_weight: 'medium',
                            ranges: [
                                {
                                    start: new Template('custom_range_start'),
                                    end: new Template('custom_range_end'),
                                    text_color: new Template('custom_range_color')
                                }
                            ]
                        }),
                        new TextBlock({
                            text: new Template('desc'),
                            font_size: 14,
                            text_color: '#000000',
                            line_height: 18,
                            max_lines: 2,
                            margins: {
                                top: 2,
                                left: 12,
                                right: 12
                            }
                        }),
                        new TextBlock({
                            text: new Template('host'),
                            font_size: 14,
                            text_color: '#000000',
                            alpha: 0.4,
                            line_height: 16,
                            max_lines: 1,
                            margins: {
                                top: 3,
                                left: 12,
                                right: 12
                            }
                        })
                    ]
                })
            }
        ]);

        const cards = [{
            url: 'ya.ru',
            title: 'Маркет',
            desc: 'Дрова',
            host: 'Село',
            logo: 'Дерево',
            price: '1 000 000$'
        }].map(({desc, url, logo, host, price}) => {
            return new TemplateBlock('market_item', {
                action_link: {
                    log_id: 'link',
                    url: url
                },
                price: price,
                desc: desc,
                host: host,
                logo: logo,
                logo_margin_top: 6,
                custom_range_start: 1,
                custom_range_end: 3,
                custom_range_color: 'red'
            })
        });

        const divData: IDivData = {
            log_id: 'market_card',
            states: [
                {
                    state_id: 1,
                    div: new TemplateBlock('market_card', {
                        bg_color: 'ya.ru',

                        title_items: [
                            new TemplateBlock('title_text', {
                                text: 'Маркет',
                                action: {
                                    log_id: 'market.title',
                                    url: 'https://m.market.yandex.ru?pp=110&clid=903&distr_type=7'
                                }
                            })
                        ],
                        cards: cards,
                        margins: {
                            bottom: 10
                        }
                    })
                }
            ]
        };

        const card = new TemplateCard(templates, divData);
        expect(card).toMatchSnapshot();
    });

    it('should hold id parameter', () => {
        const text = new TextBlock({id: 'text', text: 'test'});
        const gif = new GifBlock({id: 'gif', gif_url: 'test'});
        const img = new ImageBlock({id: 'image', image_url: 'test'});
        const container = new ContainerBlock({id: 'container', items: [text]});
        const gallery = new GalleryBlock({id: 'gallery', items: [container]});
        const grid = new GridBlock({id: 'grid', items: [text], column_count: 1});
        const sep = new SeparatorBlock({id: 'sep'});
        const state = new DivStateBlock({id: 'state', div_id: 'test', states: new Template('states')});
        const tabs = new TabsBlock({id: 'tabs', items: new Template('items')});
        const blocks = [
            text,
            gif,
            img,
            container,
            gallery,
            grid,
            sep,
            state,
            tabs
        ];

        expect(blocks.every(block => typeof block.id === 'string')).toBe(true);
    });
});
