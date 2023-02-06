import {assert} from 'chai'

import {
    Action,
    Card, ContainerBlock,
    DivData, GalleryBlock,
    GradientBackground,
    ImageBackground, ImageBlock, ImageElement,
    NumericSize, PredefinedSize,
    SolidBackground,
    TabsBlock,
    TitleBlock
} from '../../src';

import {SimpleCard, SimpleSportCard} from '../mocks/index';

describe('Div card test', () => {
    it('should create simple title', () => {
        let data: DivData = {
            states: [
                {
                    state_id: 1,
                    blocks: []
                }
            ], background: [
                new GradientBackground({
                    start_color: '#ccc',
                    end_color: '#333'
                }),
                new ImageBackground({
                    image_url: 'ya.ru',

                })
            ],
            url: "ya.ru",
            width: new NumericSize({value: 100})
        };

        let card: Card = new Card({
            id: 'sport',
            type: 'div',
            data: data,
            menu: {
                menu_list: [
                    {action: 'ya.ru', text: 'text'}
                ], button_color: '#000'
            },
            topic: "sport_div"

        });

        assert.deepEqual(card.div(), SimpleCard);
    });

    it('should create simple sport card', () => {

        let title: TitleBlock = new TitleBlock({
            menu_color: "#000000",
            menu_items: [
                {
                    url: 'opensettings://?screen=feed',
                    text: "Настройки ленты"
                },
                {
                    url: "hidecard://?topic_card_ids=sport_card&undo_snackbar_text=%D0%92%D1%8B%20%D1%81%D0%BA%D1%80%D1%8B%D0%BB%D0%B8%20%D0%BA%D0%B0%D1%80%D1%82%D0%BE%D1%87%D0%BA%D1%83",
                    text: "Скрыть карточку"
                }
            ],
            text: "<font color=\"#000000\">Спорт</font>",
            text_style: 'title_m'
        });

        let gallery: GalleryBlock = new GalleryBlock({
            items: [
                new ContainerBlock({
                    height: new NumericSize({value: 240}),
                    frame: {style: "shadow"},
                    width: new NumericSize({value: 244}),
                    direction: "vertical",
                    alignment_vertical: "top",
                    background: [
                        new GradientBackground({start_color: "#ffffff", end_color: '#eef2f6'})
                    ],
                    children: [
                        new ImageBlock({
                            image: new ImageElement({
                                ratio: 2,
                                image_url: "https://avatars.mds.yandex.net/get-ynews/138655/1b242f132c7ea1233b2927d3c1af2d6a/563x304"
                            })
                        })
                    ]
                })
            ],
            padding_bottom: new NumericSize({value: 1}),
            padding_top: new NumericSize({value: 2}),
            padding_between_items: new NumericSize({value: 0}),
            tail: {

                text: "Другие новости спорта",
                text_style: "text_m",
                icon: {
                    fill_color: "#eef2f6",
                    icon_color: "#000000",
                    border_color: "#00ffffff"
                },
                action: {
                    url: "yellowskin://?background_color=%234b9645&buttons_color=%23ffffff&omnibox_color=%23288736&status_bar_theme=dark&text_color=%23ffffff&url=https%3A%2F%2Fyandex.ru%2Fsport%3Fsource%3Dyandex_portal%26utm_source%3Dyandex_portal%26lat%3D55.73%26lng%3D37.59%26appsearch_header%3D1",
                    log_id: "sport_tail"
                },

            }
        });

        let tabs: TabsBlock = new TabsBlock({
            has_delimiter: 0,
            inactive_tab_color: "#CC000000",
            items: [
                {
                    title: {
                        action: {
                            url: "yellowskin://?background_color=%23fefefe&buttons_color=%2391989b&omnibox_color=%23f0f0f0&status_bar_theme=light&text_color=%23000000&url=https%3A%2F%2Fyandex.ru%2Fsport%3Ffrom%3Dhome%26utm_campaign%3D%26utm_content%3Dall_posts%26utm_medium%3Dpromoblock%26utm_source%3Dappsearch%26appsearch_header%3D1",
                            log_id: "sport_all"
                        },
                        text: "ВСЕ"
                    },
                    content: new ContainerBlock({
                        height: new NumericSize({value: 260}),
                        width: new PredefinedSize({value: "match_parent"}),
                        frame: {
                            style: "shadow"
                        },
                        children: [gallery],
                        direction: "vertical",
                        alignment_vertical: "top"
                    })
                }
            ],

        });

        let data: DivData = {
            states: [
                {
                    state_id: 1,
                    blocks: [title, tabs]
                }
            ], background: [
                new SolidBackground({
                    color: '#ffffff'
                })
            ]
        };
        let card: Card = new Card({
            id: 'sport',
            type: 'div',
            data: data,
            ttl: 1,
            ttv: 1,
            utime: 1,
            topic: "sport_card"
        })

        assert.deepEqual(card.div(), SimpleSportCard);
    });

});