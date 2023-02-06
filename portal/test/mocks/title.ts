export const SimpleTitle = {
    "type": "div-title-block",
    "text": "<font color=\"#000000\">Фильмы</font>",
    "text_style": "title_m",
};

export const TitleWithPadding = {
    "type": "div-title-block",
    "text": "<font color=\"#000000\">Фильмы</font>",
    "text_style": "title_m",
    "padding_modifier": {
        "size": "xs",
        "position": "left"
    }
};

export const TitleWithAction = {
    "type": "div-title-block",
    "text": "<font color=\"#000000\">Фильмы</font>",
    "text_style": "title_m",
    "action": {
        "url": "yellowskin://?background_color=%23282a3a&buttons_color=%23ffffff&omnibox_color=%23191b24&status_bar_theme=dark&text_color=%23ffffff&url=https%3A%2F%2Fyandex.ru%2Fefir%3Ffrom%3Dappsearch%26stream_active%3Dcategory%26stream_category%3Dfilm%26from_block%3Dfilm_carousel_appsearch",
        "log_id": "title"
    }
};

export const TitleWithMenu = {
    "type": "div-title-block",
    "text": "<font color=\"#000000\">Фильмы</font>",
    "menu_items": [
        {
            "text": "Настройки ленты",
            "url": "opensettings://?screen=feed"
        },
        {
            "text": "Скрыть карточку",
            "url": "hidecard://?topic_card_ids=stream_film_card&undo_snackbar_text=%D0%92%D1%8B%20%D1%81%D0%BA%D1%80%D1%8B%D0%BB%D0%B8%20%D0%BA%D0%B0%D1%80%D1%82%D0%BE%D1%87%D0%BA%D1%83"
        }
    ],
    "menu_color": "#808080",
    "text_style": "title_m",
};
