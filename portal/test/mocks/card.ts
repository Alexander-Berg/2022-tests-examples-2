export const SimpleCard = {
    id: 'sport',
    topic: "sport_div",
    type: 'div',
    menu: {
        menu_list: [
            {action: 'ya.ru', text: 'text'}
        ], button_color: '#000'
    },
    data: {
        background: [
            {
                type: 'div-gradient-background',
                start_color: '#ccc',
                end_color: '#333'
            },
            {
                type: 'div-image-background',
                image_url: 'ya.ru',
            }
        ],
        states: [
            {
                state_id: 1,
                blocks: []
            }
        ],
        url: "ya.ru",
        width: {
            type: 'numeric',
            value: 100
        }
    }
};

export const SimpleSportCard = {
    "data": {
        "states": [
            {
                "blocks": [
                    {
                        "menu_color": "#000000",
                        "menu_items": [
                            {
                                "url": "opensettings://?screen=feed",
                                "text": "Настройки ленты"
                            },
                            {
                                "url": "hidecard://?topic_card_ids=sport_card&undo_snackbar_text=%D0%92%D1%8B%20%D1%81%D0%BA%D1%80%D1%8B%D0%BB%D0%B8%20%D0%BA%D0%B0%D1%80%D1%82%D0%BE%D1%87%D0%BA%D1%83",
                                "text": "Скрыть карточку"
                            }
                        ],
                        "text_style": "title_m",
                        "type": "div-title-block",
                        "text": "<font color=\"#000000\">Спорт</font>"
                    },
                    {
                        "inactive_tab_color": "#CC000000",
                        "items": [
                            {
                                "title": {
                                    "action": {
                                        "url": "yellowskin://?background_color=%23fefefe&buttons_color=%2391989b&omnibox_color=%23f0f0f0&status_bar_theme=light&text_color=%23000000&url=https%3A%2F%2Fyandex.ru%2Fsport%3Ffrom%3Dhome%26utm_campaign%3D%26utm_content%3Dall_posts%26utm_medium%3Dpromoblock%26utm_source%3Dappsearch%26appsearch_header%3D1",
                                        "log_id": "sport_all"
                                    },
                                    "text": "ВСЕ"
                                },
                                "content": {
                                    "height": {
                                        "type": "numeric",
                                        "value": 260
                                    },
                                    "frame": {
                                        "style": "shadow"
                                    },
                                    "children": [
                                        {
                                            "padding_bottom": {
                                                "type": "numeric",
                                                "value": 1
                                            },
                                            "padding_top": {
                                                "type": "numeric",
                                                "value": 2
                                            },
                                            "tail": {
                                                "text_style": "text_m",
                                                "text": "Другие новости спорта",
                                                "icon": {
                                                    "fill_color": "#eef2f6",
                                                    "icon_color": "#000000",
                                                    "border_color": "#00ffffff"
                                                },
                                                "action": {
                                                    "url": "yellowskin://?background_color=%234b9645&buttons_color=%23ffffff&omnibox_color=%23288736&status_bar_theme=dark&text_color=%23ffffff&url=https%3A%2F%2Fyandex.ru%2Fsport%3Fsource%3Dyandex_portal%26utm_source%3Dyandex_portal%26lat%3D55.73%26lng%3D37.59%26appsearch_header%3D1",
                                                    "log_id": "sport_tail"
                                                }
                                            },
                                            "type": "div-gallery-block",
                                            "items": [
                                                {
                                                    "height": {
                                                        "type": "numeric",
                                                        "value": 240
                                                    },
                                                    "frame": {
                                                        "style": "shadow"
                                                    },
                                                    "children": [
                                                        {
                                                            "image": {
                                                                "ratio": 2,
                                                                "type": "div-image-element",
                                                                "image_url": "https://avatars.mds.yandex.net/get-ynews/138655/1b242f132c7ea1233b2927d3c1af2d6a/563x304"
                                                            },
                                                            "type": "div-image-block"
                                                        }
                                                    ],
                                                    "width": {
                                                        "type": "numeric",
                                                        "value": 244
                                                    },
                                                    "direction": "vertical",
                                                    "type": "div-container-block",
                                                    "alignment_vertical": "top",
                                                    "background": [
                                                        {
                                                            "start_color": "#ffffff",
                                                            "type": "div-gradient-background",
                                                            "end_color": "#eef2f6"
                                                        }
                                                    ]
                                                }
                                            ],
                                            "padding_between_items": {
                                                "type": "numeric",
                                                "value": 0
                                            }
                                        }
                                    ],
                                    "width": {
                                        "type": "predefined",
                                        "value": "match_parent"
                                    },
                                    "direction": "vertical",
                                    "type": "div-container-block",
                                    "alignment_vertical": "top"
                                }
                            }
                        ],
                        "type": "div-tabs-block",
                        "has_delimiter": 0
                    }
                ],
                "state_id": 1
            }
        ],
        "background": [
            {
                "color": "#ffffff",
                "type": "div-solid-background"
            }
        ]
    },
    "type": "div",
    "id": "sport",
    "topic": "sport_card",
    "ttl": 1,
    "ttv": 1,
    "utime": 1
};