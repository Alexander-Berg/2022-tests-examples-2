from typing import Any
from typing import Dict
from typing import List

BUTTON_TITLES = {'ru': 'Русский текст', 'en': 'English text'}


def create_response_story(
        story_id: str, locale: str, media_count: int = 2,
) -> Dict[str, Any]:

    return {
        'name': story_id + '_name',
        'media': [
            {
                'content': f'md3_content_{i}.{locale}',
                'show_button': True,
                'type': 'video',
            }
            for i in range(media_count)
        ],
        'button_title': BUTTON_TITLES[locale],
        'button_link': 'button_link' + story_id + locale,
        'teaser_image': 'teaser_image' + story_id + locale,
    }


def create_db_story(
        story_id: str, locales: List[str], media_count: int = 2,
) -> Dict[str, Any]:
    return dict(
        {
            'id': story_id,
            'updated': '2019-07-23T11:46:47.439Z',
            'name': story_id + '_name',
            'created': '2019-07-23T11:46:41.702Z',
            'button_title_key': 'promo_story.default.button_title',
            'languages': [
                {
                    'locale': locale,
                    'media': [
                        {
                            'content': f'md3_content_{i}.{locale}',
                            'type': 'video',
                            'show_button': True,
                        }
                        for i in range(media_count)
                    ],
                    'button_link': 'button_link' + story_id + locale,
                    'teaser_image': 'teaser_image' + story_id + locale,
                }
                for locale in locales
            ],
            'active': False,
        },
    )
