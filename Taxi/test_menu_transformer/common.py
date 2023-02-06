from menu_transformer.content import filters
from menu_transformer.content import transformers


class MenuTransformerFiltersTest:
    filters = {
        'punctuation_filter': filters.PunctuationFilter(),
        'html_tags_filter': filters.HtmlTagsFilter(),
        'uppercase_filter': filters.UppercaseFilter(),
        'capitalize_first_letter_filter': (
            filters.CapitalizeFirstLetterFilter()
        ),
        'capitalize_first_letter_by_sentence_filter': (
            filters.CapitalizeFirstLetterBySentenceFilter()
        ),
        'replacement_filter': filters.ReplacementFilter(
            **{
                'arguments': {
                    '/\\s+Б\\.\\sЮ\\.\\s+/ui': ' Б.Ю. ',
                    '/\\s+Нежныйс\\s+/ui': ' Нежный с ',
                    '/\\s+вяз(\\.)?\\s+/ui': ' вязкий ',
                },
            },
        ),
    }


class MenuTransformersTest:
    transformers = {
        'basic_category_name_transformer': (
            transformers.CategoryNameTransformer(
                **{
                    'arguments': [
                        'html_tags_filter',
                        'capitalize_first_letter_filter',
                    ],
                    'menu_transformer': MenuTransformerFiltersTest,
                },
            )
        ),
    }
