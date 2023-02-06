export const SimpleContainer = {
    "type": "div-container-block",
    "children": [
        {
            "type": "div-title-block",
            "text": "text",
            "text_style": "title_s",
        }
    ],
    "width": {
        "value": 100,
        "type": "numeric",
        "unit": "dp"
    },
    "height": {
        "value": "match_parent",
        "type": "predefined"
    }
};

export const ContainerInContainer = {
    "type": "div-container-block",
    "children": [
        {
            "type": "div-title-block",
            "text": "text",
            "text_style": "title_s",
        },
        {
            "type": "div-container-block",
            "children": [
                {
                    "type": "div-title-block",
                    "text": "text",
                    "text_style": "title_s",
                }
            ],
            "width": {
                "value": 100,
                "type": "numeric",
                "unit": "dp"
            },
            "height": {
                "value": "match_parent",
                "type": "predefined"
            }
        },
        {
            "type": "div-title-block",
            "text": "text",
            "text_style": "title_s",
        }
    ],
    "width": {
        "value": 100,
        "type": "numeric",
        "unit": "sp"
    },
    "height": {
        "value": "wrap_content",
        "type": "predefined"
    },
    "alignment_horizontal": "center",
    "alignment_vertical": "top",
};

export const ContainerWithUniversal = {
    "type": "div-container-block",
    "children": [
        {
            "type": "div-universal-block",
            "text": "text",
            "text_max_lines": 1,
            "title": "title",
            "title_max_lines": 1,
            "text_style": "text_s",
            "title_style": "text_m_medium"
        }
    ],
    "width": {
        "value": 100,
        "type": "numeric",
        "unit": "sp"
    },
    "height": {
        "value": "match_viewport",
        "type": "predefined"
    },
    alignment_horizontal: "right",
    alignment_vertical: "bottom"
};

export const ContainerWithAllProperties = {
    "type": "div-container-block",
    "children": [
        {
            "type": "div-title-block",
            "text": "text",
            "text_style": "title_s",
        }
    ],
    "action": {
        "url": "ya.ru",
        "log_id": "id"
    },
    "alignment_vertical": "center",
    "alignment_horizontal": "right",
    "background": [
        {
            "type": "div-solid-background",
            "color": "#000"
        }
    ],
    "frame": {
        "color": "#000",
        "style": "shadow"
    },
    "width": {
        "value": 100,
        "type": "numeric"
    },
    "height": {
        "value": 100,
        "type": "numeric"
    },
    "padding_modifier": {
        position: "left",
        size: "match_parent"
    }
};
