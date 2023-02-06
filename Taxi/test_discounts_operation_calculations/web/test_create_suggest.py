# pylint: disable=too-many-lines
import pytest

CONTROL_SHARE = 10
TEST_SHARE = (100 - CONTROL_SHARE) / 100

EXPECTED_DISCOUNT = {
    'id': 1,
    'multidraft_params': {
        'charts': [
            {
                'algorithm_id': 'kt',
                'plot': {
                    'data': [
                        [50, 0.0],
                        [100, 0.0],
                        [150, 0.0],
                        [200, 0.0],
                        [250, 0.0],
                        [300, 0.0],
                        [350, 0.0],
                        [400, 0.0],
                        [450, 0.0],
                        [500, 0.0],
                        [550, 0.0],
                        [600, 0.0],
                        [650, 0.0],
                    ],
                    'label': 'control',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
            {
                'algorithm_id': 'kt',
                'plot': {
                    'data': [
                        [50, 0.0],
                        [100, 0.0],
                        [150, 0.0],
                        [200, 0.0],
                        [250, 0.0],
                        [300, 0.0],
                        [350, 0.0],
                        [400, 0.0],
                        [450, 0.0],
                        [500, 0.0],
                        [550, 0.0],
                        [600, 0.0],
                        [650, 0.0],
                    ],
                    'label': 'metrika_active_Hconv',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
            {
                'algorithm_id': 'kt',
                'plot': {
                    'data': [
                        [50, 30.0],
                        [100, 30.0],
                        [150, 30.0],
                        [200, 24.0],
                        [250, 15.0],
                        [300, 9.0],
                        [350, 6.0],
                        [400, 3.0],
                        [450, 0.0],
                        [500, 0.0],
                        [550, 0.0],
                        [600, 0.0],
                        [650, 0.0],
                    ],
                    'label': 'metrika_active_Lconv',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
            {
                'algorithm_id': 'kt',
                'plot': {
                    'data': [
                        [50, 30.0],
                        [100, 30.0],
                        [150, 18.0],
                        [200, 3.0],
                        [250, 0.0],
                        [300, 0.0],
                        [350, 0.0],
                        [400, 0.0],
                        [450, 0.0],
                        [500, 0.0],
                        [550, 0.0],
                        [600, 0.0],
                        [650, 0.0],
                    ],
                    'label': 'metrika_active_Mconv',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
            {
                'algorithm_id': 'kt',
                'plot': {
                    'data': [
                        [50, 0.0],
                        [100, 0.0],
                        [150, 0.0],
                        [200, 0.0],
                        [250, 0.0],
                        [300, 0.0],
                        [350, 0.0],
                        [400, 0.0],
                        [450, 0.0],
                        [500, 0.0],
                        [550, 0.0],
                        [600, 0.0],
                        [650, 0.0],
                    ],
                    'label': 'metrika_notactive_Hconv',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
            {
                'algorithm_id': 'kt',
                'plot': {
                    'data': [
                        [50, 30.0],
                        [100, 30.0],
                        [150, 30.0],
                        [200, 27.0],
                        [250, 18.0],
                        [300, 12.0],
                        [350, 9.0],
                        [400, 6.0],
                        [450, 3.0],
                        [500, 0.0],
                        [550, 0.0],
                        [600, 0.0],
                        [650, 0.0],
                    ],
                    'label': 'metrika_notactive_Lconv',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
            {
                'algorithm_id': 'kt',
                'plot': {
                    'data': [
                        [50, 30.0],
                        [100, 30.0],
                        [150, 21.0],
                        [200, 9.0],
                        [250, 0.0],
                        [300, 0.0],
                        [350, 0.0],
                        [400, 0.0],
                        [450, 0.0],
                        [500, 0.0],
                        [550, 0.0],
                        [600, 0.0],
                        [650, 0.0],
                    ],
                    'label': 'metrika_notactive_Mconv',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
            {
                'algorithm_id': 'kt',
                'plot': {
                    'data': [
                        [50, 30.0],
                        [100, 21.0],
                        [150, 0.0],
                        [200, 0.0],
                        [250, 0.0],
                        [300, 0.0],
                        [350, 0.0],
                        [400, 0.0],
                        [450, 0.0],
                        [500, 0.0],
                        [550, 0.0],
                        [600, 0.0],
                        [650, 0.0],
                    ],
                    'label': 'random',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
        ],
        'discount_meta': {
            'kt': {
                'budget_spent': 499222323.0189901,
                'cur_cpeo': 16838.30949883128,
                'fallback_discount': 0,
                'fixed_discounts': [
                    {'discount_value': 0, 'segment': 'control'},
                ],
                'segments_meta': {
                    'control': {
                        'avg_discount': 0.0,
                        'budget': 0.0,
                        'max_discount_percent': 0.0,
                        'max_price_with_discount': 0,
                    },
                    'metrika_active_Hconv': {
                        'avg_discount': 0.0,
                        'budget': 0.0,
                        'max_discount_percent': 0.0,
                        'max_price_with_discount': 0,
                    },
                    'metrika_active_Lconv': {
                        'avg_discount': 13.223370983287424,
                        'budget': 32850296.619525,
                        'max_discount_percent': 30.0,
                        'max_price_with_discount': 400,
                    },
                    'metrika_active_Mconv': {
                        'avg_discount': 5.3790530170035025,
                        'budget': 158872765.29655498,
                        'max_discount_percent': 30.0,
                        'max_price_with_discount': 200,
                    },
                    'metrika_notactive_Hconv': {
                        'avg_discount': 0.0,
                        'budget': 0.0,
                        'max_discount_percent': 0.0,
                        'max_price_with_discount': 0,
                    },
                    'metrika_notactive_Lconv': {
                        'avg_discount': 14.248549220105048,
                        'budget': 169781811.42195004,
                        'max_discount_percent': 30.0,
                        'max_price_with_discount': 450,
                    },
                    'metrika_notactive_Mconv': {
                        'avg_discount': 5.774510242066734,
                        'budget': 128161870.19856,
                        'max_discount_percent': 30.0,
                        'max_price_with_discount': 200,
                    },
                    'random': {
                        'avg_discount': 2.4644409001851995,
                        'budget': 9555579.4824,
                        'max_discount_percent': 30.0,
                        'max_price_with_discount': 100,
                    },
                },
                'with_push': False,
            },
        },
    },
    'warnings': [
        {
            'code': 'LowBudget::Error',
            'level': 'ERROR',
            'message': (
                'Сегмент metrika_active_Lconv имеет слишком низкую '
                'скидку! Увеличьте бюджет!'
            ),
        },
        {
            'code': 'LowBudget::Error',
            'level': 'ERROR',
            'message': (
                'Сегмент metrika_active_Mconv имеет слишком низкую '
                'скидку! Увеличьте бюджет!'
            ),
        },
        {
            'code': 'LowBudget::Error',
            'level': 'ERROR',
            'message': (
                'Сегмент metrika_notactive_Mconv имеет слишком '
                'низкую скидку! Увеличьте бюджет!'
            ),
        },
        {
            'code': 'LowBudget::Error',
            'level': 'ERROR',
            'message': (
                'Сегмент random имеет слишком низкую скидку! '
                'Увеличьте бюджет!'
            ),
        },
        {
            'code': 'LowBudget::Error',
            'level': 'ERROR',
            'message': (
                'Сегмент metrika_active_Hconv не имеет скидок! '
                'Увеличьте бюджет!'
            ),
        },
        {
            'code': 'LowBudget::Error',
            'level': 'ERROR',
            'message': (
                'Сегмент metrika_notactive_Hconv не имеет скидок! '
                'Увеличьте бюджет!'
            ),
        },
    ],
}
EXPECTED_DISCOUNT_WITH_PUSH = {
    'id': 1,
    'multidraft_params': {
        'charts': [
            {
                'algorithm_id': 'ktfallback',
                'plot': {
                    'data': [[75, 0], [285, 0], [295, 0]],
                    'label': 'control',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
            {
                'algorithm_id': 'ktfallback',
                'plot': {
                    'data': [[75, 6], [285, 6], [295, 0]],
                    'label': 'metrika_active_Hconv',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
            {
                'algorithm_id': 'kt',
                'plot': {
                    'data': [
                        [75, 6.0],
                        [125, 6.0],
                        [175, 6.0],
                        [225, 6.0],
                        [275, 6.0],
                        [285, 0],
                    ],
                    'label': 'metrika_active_Hconv',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
        ],
        'discount_meta': {
            'kt': {
                'budget_spent': 447880.78648709995,
                'cur_cpeo': 0,
                'fallback_discount': 6,
                'fixed_discounts': [
                    {'discount_value': 0, 'segment': 'control'},
                ],
                'segments_meta': {
                    'metrika_active_Hconv': {
                        'avg_discount': 0.029999999999999995,
                        'budget': 447880.78648709995,
                        'max_discount_percent': 6.0,
                        'max_price_with_discount': 275,
                    },
                },
                'with_push': True,
            },
            'ktfallback': {
                'budget_spent': 0,
                'cur_cpeo': 0,
                'fallback_discount': 6,
                'fixed_discounts': [],
                'segments_meta': {},
                'with_push': True,
            },
        },
    },
    'warnings': [
        {
            'code': 'LowBudget::Error',
            'level': 'ERROR',
            'message': (
                'Сегмент metrika_active_Lconv не имеет скидок! '
                'Увеличьте бюджет!'
            ),
        },
        {
            'code': 'LowBudget::Error',
            'level': 'ERROR',
            'message': (
                'Сегмент metrika_active_Mconv не имеет скидок! '
                'Увеличьте бюджет!'
            ),
        },
        {
            'code': 'LowBudget::Error',
            'level': 'ERROR',
            'message': (
                'Сегмент metrika_notactive_Hconv не имеет скидок! '
                'Увеличьте бюджет!'
            ),
        },
        {
            'code': 'LowBudget::Error',
            'level': 'ERROR',
            'message': (
                'Сегмент metrika_notactive_Lconv не имеет скидок! '
                'Увеличьте бюджет!'
            ),
        },
        {
            'code': 'LowBudget::Error',
            'level': 'ERROR',
            'message': (
                'Сегмент metrika_notactive_Mconv не имеет скидок! '
                'Увеличьте бюджет!'
            ),
        },
        {
            'code': 'LowBudget::Error',
            'level': 'ERROR',
            'message': 'Сегмент random не имеет скидок! Увеличьте бюджет!',
        },
    ],
}

EXPECTED_DISCOUNT_SMALL_BUDGET = {
    'id': 1,
    'multidraft_params': {
        'charts': [
            {
                'algorithm_id': 'kt',
                'plot': {
                    'data': [
                        [50, 0.0],
                        [100, 0.0],
                        [150, 0.0],
                        [200, 0.0],
                        [250, 0.0],
                        [300, 0.0],
                        [350, 0.0],
                        [400, 0.0],
                        [450, 0.0],
                        [500, 0.0],
                        [550, 0.0],
                        [600, 0.0],
                        [650, 0.0],
                    ],
                    'label': 'control',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
            {
                'algorithm_id': 'kt',
                'plot': {
                    'data': [
                        [50, 0.0],
                        [100, 0.0],
                        [150, 0.0],
                        [200, 0.0],
                        [250, 0.0],
                        [300, 0.0],
                        [350, 0.0],
                        [400, 0.0],
                        [450, 0.0],
                        [500, 0.0],
                        [550, 0.0],
                        [600, 0.0],
                        [650, 0.0],
                    ],
                    'label': 'metrika_active_Hconv',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
            {
                'algorithm_id': 'kt',
                'plot': {
                    'data': [
                        [50, 0.0],
                        [100, 0.0],
                        [150, 0.0],
                        [200, 0.0],
                        [250, 0.0],
                        [300, 0.0],
                        [350, 0.0],
                        [400, 0.0],
                        [450, 0.0],
                        [500, 0.0],
                        [550, 0.0],
                        [600, 0.0],
                        [650, 0.0],
                    ],
                    'label': 'metrika_active_Lconv',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
            {
                'algorithm_id': 'kt',
                'plot': {
                    'data': [
                        [50, 0.0],
                        [100, 0.0],
                        [150, 0.0],
                        [200, 0.0],
                        [250, 0.0],
                        [300, 0.0],
                        [350, 0.0],
                        [400, 0.0],
                        [450, 0.0],
                        [500, 0.0],
                        [550, 0.0],
                        [600, 0.0],
                        [650, 0.0],
                    ],
                    'label': 'metrika_active_Mconv',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
            {
                'algorithm_id': 'kt',
                'plot': {
                    'data': [
                        [50, 0.0],
                        [100, 0.0],
                        [150, 0.0],
                        [200, 0.0],
                        [250, 0.0],
                        [300, 0.0],
                        [350, 0.0],
                        [400, 0.0],
                        [450, 0.0],
                        [500, 0.0],
                        [550, 0.0],
                        [600, 0.0],
                        [650, 0.0],
                    ],
                    'label': 'metrika_notactive_Hconv',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
            {
                'algorithm_id': 'kt',
                'plot': {
                    'data': [
                        [50, 0.0],
                        [100, 0.0],
                        [150, 0.0],
                        [200, 0.0],
                        [250, 0.0],
                        [300, 0.0],
                        [350, 0.0],
                        [400, 0.0],
                        [450, 0.0],
                        [500, 0.0],
                        [550, 0.0],
                        [600, 0.0],
                        [650, 0.0],
                    ],
                    'label': 'metrika_notactive_Lconv',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
            {
                'algorithm_id': 'kt',
                'plot': {
                    'data': [
                        [50, 0.0],
                        [100, 0.0],
                        [150, 0.0],
                        [200, 0.0],
                        [250, 0.0],
                        [300, 0.0],
                        [350, 0.0],
                        [400, 0.0],
                        [450, 0.0],
                        [500, 0.0],
                        [550, 0.0],
                        [600, 0.0],
                        [650, 0.0],
                    ],
                    'label': 'metrika_notactive_Mconv',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
            {
                'algorithm_id': 'kt',
                'plot': {
                    'data': [
                        [50, 0.0],
                        [100, 0.0],
                        [150, 0.0],
                        [200, 0.0],
                        [250, 0.0],
                        [300, 0.0],
                        [350, 0.0],
                        [400, 0.0],
                        [450, 0.0],
                        [500, 0.0],
                        [550, 0.0],
                        [600, 0.0],
                        [650, 0.0],
                    ],
                    'label': 'random',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
        ],
        'discount_meta': {
            'kt': {
                'budget_spent': 0.0,
                'cur_cpeo': 2369.213593047498,
                'fallback_discount': 0,
                'fixed_discounts': [
                    {'discount_value': 0, 'segment': 'control'},
                ],
                'segments_meta': {
                    'control': {
                        'avg_discount': 0.0,
                        'budget': 0.0,
                        'max_discount_percent': 0.0,
                        'max_price_with_discount': 0,
                    },
                    'metrika_active_Hconv': {
                        'avg_discount': 0.0,
                        'budget': 0.0,
                        'max_discount_percent': 0.0,
                        'max_price_with_discount': 0,
                    },
                    'metrika_active_Lconv': {
                        'avg_discount': 0.0,
                        'budget': 0.0,
                        'max_discount_percent': 0.0,
                        'max_price_with_discount': 0,
                    },
                    'metrika_active_Mconv': {
                        'avg_discount': 0.0,
                        'budget': 0.0,
                        'max_discount_percent': 0.0,
                        'max_price_with_discount': 0,
                    },
                    'metrika_notactive_Hconv': {
                        'avg_discount': 0.0,
                        'budget': 0.0,
                        'max_discount_percent': 0.0,
                        'max_price_with_discount': 0,
                    },
                    'metrika_notactive_Lconv': {
                        'avg_discount': 0.0,
                        'budget': 0.0,
                        'max_discount_percent': 0.0,
                        'max_price_with_discount': 0,
                    },
                    'metrika_notactive_Mconv': {
                        'avg_discount': 0.0,
                        'budget': 0.0,
                        'max_discount_percent': 0.0,
                        'max_price_with_discount': 0,
                    },
                    'random': {
                        'avg_discount': 0.0,
                        'budget': 0.0,
                        'max_discount_percent': 0.0,
                        'max_price_with_discount': 0,
                    },
                },
                'with_push': False,
            },
        },
    },
    'warnings': [
        {
            'code': 'LowBudget::Error',
            'level': 'ERROR',
            'message': (
                'Сегмент metrika_active_Hconv не имеет скидок! '
                'Увеличьте бюджет!'
            ),
        },
        {
            'code': 'LowBudget::Error',
            'level': 'ERROR',
            'message': (
                'Сегмент metrika_active_Lconv не имеет скидок! '
                'Увеличьте бюджет!'
            ),
        },
        {
            'code': 'LowBudget::Error',
            'level': 'ERROR',
            'message': (
                'Сегмент metrika_active_Mconv не имеет скидок! '
                'Увеличьте бюджет!'
            ),
        },
        {
            'code': 'LowBudget::Error',
            'level': 'ERROR',
            'message': (
                'Сегмент metrika_notactive_Hconv не имеет скидок! '
                'Увеличьте бюджет!'
            ),
        },
        {
            'code': 'LowBudget::Error',
            'level': 'ERROR',
            'message': (
                'Сегмент metrika_notactive_Lconv не имеет скидок! '
                'Увеличьте бюджет!'
            ),
        },
        {
            'code': 'LowBudget::Error',
            'level': 'ERROR',
            'message': (
                'Сегмент metrika_notactive_Mconv не имеет скидок! '
                'Увеличьте бюджет!'
            ),
        },
        {
            'code': 'LowBudget::Error',
            'level': 'ERROR',
            'message': 'Сегмент random не имеет скидок! Увеличьте бюджет!',
        },
    ],
}

EXPECTED_DISCOUNT_EXCEEDED_BUDGET = {
    'id': 1,
    'multidraft_params': {
        'charts': [
            {
                'algorithm_id': 'kt',
                'plot': {
                    'data': [
                        [50, 0.0],
                        [100, 0.0],
                        [150, 0.0],
                        [200, 0.0],
                        [250, 0.0],
                        [300, 0.0],
                        [350, 0.0],
                        [400, 0.0],
                        [450, 0.0],
                        [500, 0.0],
                        [550, 0.0],
                        [600, 0.0],
                        [650, 0.0],
                    ],
                    'label': 'control',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
            {
                'algorithm_id': 'kt',
                'plot': {
                    'data': [
                        [50, 30.0],
                        [100, 30.0],
                        [150, 30.0],
                        [200, 30.0],
                        [250, 30.0],
                        [300, 30.0],
                        [350, 30.0],
                        [400, 30.0],
                        [450, 30.0],
                        [500, 30.0],
                        [550, 30.0],
                        [600, 30.0],
                        [650, 30.0],
                        [652.5, 0],
                    ],
                    'label': 'metrika_active_Hconv',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
            {
                'algorithm_id': 'kt',
                'plot': {
                    'data': [
                        [50, 30.0],
                        [100, 30.0],
                        [150, 30.0],
                        [200, 30.0],
                        [250, 30.0],
                        [300, 30.0],
                        [350, 30.0],
                        [400, 30.0],
                        [450, 30.0],
                        [500, 30.0],
                        [550, 30.0],
                        [600, 30.0],
                        [650, 30.0],
                        [652.5, 0],
                    ],
                    'label': 'metrika_active_Lconv',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
            {
                'algorithm_id': 'kt',
                'plot': {
                    'data': [
                        [50, 30.0],
                        [100, 30.0],
                        [150, 30.0],
                        [200, 30.0],
                        [250, 30.0],
                        [300, 30.0],
                        [350, 30.0],
                        [400, 30.0],
                        [450, 30.0],
                        [500, 30.0],
                        [550, 30.0],
                        [600, 30.0],
                        [650, 30.0],
                        [652.5, 0],
                    ],
                    'label': 'metrika_active_Mconv',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
            {
                'algorithm_id': 'kt',
                'plot': {
                    'data': [
                        [50, 30.0],
                        [100, 30.0],
                        [150, 30.0],
                        [200, 30.0],
                        [250, 30.0],
                        [300, 30.0],
                        [350, 30.0],
                        [400, 30.0],
                        [450, 30.0],
                        [500, 30.0],
                        [550, 30.0],
                        [600, 30.0],
                        [650, 30.0],
                        [652.5, 0],
                    ],
                    'label': 'metrika_notactive_Hconv',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
            {
                'algorithm_id': 'kt',
                'plot': {
                    'data': [
                        [50, 30.0],
                        [100, 30.0],
                        [150, 30.0],
                        [200, 30.0],
                        [250, 30.0],
                        [300, 30.0],
                        [350, 30.0],
                        [400, 30.0],
                        [450, 30.0],
                        [500, 30.0],
                        [550, 30.0],
                        [600, 30.0],
                        [650, 30.0],
                        [652.5, 0],
                    ],
                    'label': 'metrika_notactive_Lconv',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
            {
                'algorithm_id': 'kt',
                'plot': {
                    'data': [
                        [50, 30.0],
                        [100, 30.0],
                        [150, 30.0],
                        [200, 30.0],
                        [250, 30.0],
                        [300, 30.0],
                        [350, 30.0],
                        [400, 30.0],
                        [450, 30.0],
                        [500, 30.0],
                        [550, 30.0],
                        [600, 30.0],
                        [650, 30.0],
                        [652.5, 0],
                    ],
                    'label': 'metrika_notactive_Mconv',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
            {
                'algorithm_id': 'kt',
                'plot': {
                    'data': [
                        [50, 30.0],
                        [100, 30.0],
                        [150, 30.0],
                        [200, 30.0],
                        [250, 30.0],
                        [300, 30.0],
                        [350, 30.0],
                        [400, 30.0],
                        [450, 30.0],
                        [500, 30.0],
                        [550, 30.0],
                        [600, 30.0],
                        [650, 30.0],
                        [652.5, 0],
                    ],
                    'label': 'random',
                    'x_label': 'Цена поездки',
                    'y_label': 'Скидка',
                },
            },
        ],
        'discount_meta': {
            'kt': {
                'budget_spent': 1047732343.5448613,
                'cur_cpeo': 8382.36942675159,
                'fallback_discount': 0,
                'fixed_discounts': [
                    {'discount_value': 0, 'segment': 'control'},
                ],
                'segments_meta': {
                    'control': {
                        'avg_discount': 0.0,
                        'budget': 0.0,
                        'max_discount_percent': 0.0,
                        'max_price_with_discount': 0,
                    },
                    'metrika_active_Hconv': {
                        'avg_discount': 7.994749891836805,
                        'budget': 82885049.24355,
                        'max_discount_percent': 30.0,
                        'max_price_with_discount': 650,
                    },
                    'metrika_active_Lconv': {
                        'avg_discount': 15.93921399884707,
                        'budget': 41305384.35,
                        'max_discount_percent': 30.0,
                        'max_price_with_discount': 650,
                    },
                    'metrika_active_Mconv': {
                        'avg_discount': 11.262818031107642,
                        'budget': 352139645.8001701,
                        'max_discount_percent': 30.0,
                        'max_price_with_discount': 650,
                    },
                    'metrika_notactive_Hconv': {
                        'avg_discount': 8.865852551536088,
                        'budget': 18283725.0,
                        'max_discount_percent': 30.0,
                        'max_price_with_discount': 650,
                    },
                    'metrika_notactive_Lconv': {
                        'avg_discount': 16.90108610124194,
                        'budget': 211008690.322875,
                        'max_discount_percent': 30.0,
                        'max_price_with_discount': 650,
                    },
                    'metrika_notactive_Mconv': {
                        'avg_discount': 12.4574758609052,
                        'budget': 297025212.1082651,
                        'max_discount_percent': 30.0,
                        'max_price_with_discount': 650,
                    },
                    'random': {
                        'avg_discount': 10.986177665441385,
                        'budget': 45084636.72,
                        'max_discount_percent': 30.0,
                        'max_price_with_discount': 650,
                    },
                },
                'with_push': False,
            },
        },
    },
    'warnings': [],
}


@pytest.mark.pgsql(
    'discounts_operation_calculations', files=['fill_pg_segment_stats.sql'],
)
@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_ALGORITHMS_CONFIGS={
        'kt': {
            'name': 'algorithm1',
            'metric_name': 'test_metric_name',
            'algorithm_type': 'katusha',
            'control_share': CONTROL_SHARE,
        },
    },
)
@pytest.mark.skip(reason='this handle is not supported anymore')
async def test_create_suggest(web_app_client, pgsql):
    response = await web_app_client.post(
        '/v1/suggests',
        json={
            'discounts_city': 'test_city',
            'budget': 500000000,
            'smooth_threshold': 10,
            'calculations': [
                {
                    'algorithm_id': 'kt',
                    'plot': [
                        {
                            'x_label': 'x',
                            'y_label': 'y',
                            'data': [[1, 2], [3, 4]],
                        },
                    ],
                    'fixed_discounts': [
                        {'segment': 'control', 'discount_value': 0},
                    ],
                },
            ],
        },
    )
    assert response.status == 200
    content = await response.json()

    assert content == EXPECTED_DISCOUNT

    cursor = pgsql['discounts_operation_calculations'].cursor()

    # test segment_stats_hist filling
    cursor.execute(
        'SELECT algorithm_id, trips, extra_trips, price_to, price_from, gmv,'
        'new_gmv, discount, city, segment, metric, weekly_budget, suggest_id,'
        'is_uploaded_to_yt, date_from, date_to '
        'FROM discounts_operation_calculations.segment_stats_hist ',
        'ORDER BY segment DESC',
    )
    segment_stats_hist = list(cursor)

    assert len(segment_stats_hist) == 104
    assert segment_stats_hist[:2] == [
        (
            'kt',
            pytest.approx(1099.0),
            pytest.approx(0.0),
            pytest.approx(75),
            pytest.approx(50),
            pytest.approx(359975.0),
            pytest.approx(1799875.0),
            pytest.approx(0.0),
            'test_city',
            'control',
            pytest.approx(0.0),
            pytest.approx(0.0),
            1,
            False,
            None,
            None,
        ),
        (
            'kt',
            pytest.approx(3257.5),
            pytest.approx(0.0),
            pytest.approx(125),
            pytest.approx(100),
            pytest.approx(2227482.5),
            pytest.approx(11137412.5),
            pytest.approx(0.0),
            'test_city',
            'control',
            pytest.approx(0.0),
            pytest.approx(0.0),
            1,
            False,
            None,
            None,
        ),
    ]

    cursor.close()


@pytest.mark.pgsql(
    'discounts_operation_calculations', files=['fill_pg_segment_stats.sql'],
)
@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_ALGORITHMS_CONFIGS={
        'kt': {
            'name': 'algorithm1',
            'metric_name': 'test_metric_name',
            'algorithm_type': 'katusha',
            'control_share': CONTROL_SHARE,
        },
    },
)
@pytest.mark.skip(reason='this handle is not supported anymore')
async def test_create_suggest_smooth_threshold(web_app_client, pgsql):
    response = await web_app_client.post(
        '/v1/suggests',
        json={
            'discounts_city': 'test_city',
            'budget': 2000000,
            'smooth_threshold': 2.5,
            'calculations': [
                {
                    'algorithm_id': 'kt',
                    'plot': [
                        {
                            'x_label': 'x',
                            'y_label': 'y',
                            'data': [[1, 2], [3, 4]],
                        },
                    ],
                    'fixed_discounts': [
                        {'segment': 'control', 'discount_value': 0},
                    ],
                },
            ],
        },
    )
    assert response.status == 200
    content = await response.json()

    assert content['multidraft_params']['charts'][1] == {
        'algorithm_id': 'kt',
        'plot': {
            'data': [
                [50, 0.0],
                [100, 0.0],
                [150, 0.0],
                [200, 0.0],
                [250, 0.0],
                [300, 0.0],
                [350, 0.0],
                [400, 0.0],
                [450, 0.0],
                [500, 0.0],
                [550, 0.0],
                [600, 0.0],
                [650, 0.0],
            ],
            'label': 'metrika_active_Hconv',
            'x_label': 'Цена поездки',
            'y_label': 'Скидка',
        },
    }

    response = await web_app_client.post(
        '/v1/suggests',
        json={
            'discounts_city': 'test_city',
            'budget': 2000000,
            'calculations': [
                {
                    'algorithm_id': 'kt',
                    'plot': [
                        {
                            'x_label': 'x',
                            'y_label': 'y',
                            'data': [[1, 2], [3, 4]],
                        },
                    ],
                    'fixed_discounts': [
                        {'segment': 'control', 'discount_value': 0},
                    ],
                },
            ],
        },
    )
    # smooth_threshold should be specified
    assert response.status == 400


@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=[
        'fill_pg_segment_stats.sql',
        'fill_pg_push_segment_stats.sql',
        'fill_pg_flat_segment_stats.sql',
    ],
)
@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_ALGORITHMS_CONFIGS={
        'kt': {
            'name': 'algorithm1',
            'metric_name': 'test_metric_name',
            'algorithm_type': 'katusha',
            'control_share': CONTROL_SHARE,
        },
    },
)
@pytest.mark.skip(reason='this handle is not supported anymore')
async def test_create_suggest_with_push(web_app_client, pgsql):
    response = await web_app_client.post(
        '/v1/suggests',
        json={
            'discounts_city': 'test_city',
            'budget': 500000,
            'smooth_threshold': 10,
            'calculations': [
                {
                    'algorithm_id': 'kt',
                    'plot': [
                        {
                            'x_label': 'x',
                            'y_label': 'y',
                            'data': [[1, 2], [3, 4]],
                        },
                    ],
                    'fixed_discounts': [
                        {'segment': 'control', 'discount_value': 0},
                    ],
                    'with_push': True,
                    'fallback_discount': 6,
                },
            ],
        },
    )
    assert response.status == 200
    content = await response.json()

    assert content == EXPECTED_DISCOUNT_WITH_PUSH

    cursor = pgsql['discounts_operation_calculations'].cursor()

    # test inserting new suggest
    cursor.execute(
        """SELECT id, algorithm_ids, author, discounts_city, budget, with_push
    FROM discounts_operation_calculations.suggests""",
    )
    result = list(cursor)
    assert result == [(1, ['kt'], None, 'test_city', 500000.0, True)]
    cursor.close()


@pytest.mark.pgsql(
    'discounts_operation_calculations', files=['fill_pg_segment_stats.sql'],
)
@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_ALGORITHMS_CONFIGS={
        'kt': {
            'name': 'algorithm1',
            'metric_name': 'test_metric_name',
            'algorithm_type': 'katusha',
            'control_share': CONTROL_SHARE,
        },
    },
)
@pytest.mark.skip(reason='this handle is not supported anymore')
async def test_create_suggest_exceeded_budget(web_app_client, pgsql):
    response = await web_app_client.post(
        '/v1/suggests',
        json={
            'discounts_city': 'test_city',
            'budget': 2000000000,
            'smooth_threshold': 2.5,
            'calculations': [
                {
                    'algorithm_id': 'kt',
                    'plot': [
                        {
                            'x_label': 'x',
                            'y_label': 'y',
                            'data': [[1, 2], [3, 4]],
                        },
                    ],
                    'fixed_discounts': [
                        {'segment': 'control', 'discount_value': 0},
                    ],
                },
            ],
        },
    )

    assert response.status == 200
    content = await response.json()
    assert content == EXPECTED_DISCOUNT_EXCEEDED_BUDGET


@pytest.mark.pgsql(
    'discounts_operation_calculations', files=['fill_pg_segment_stats.sql'],
)
@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_ALGORITHMS_CONFIGS={
        'kt': {
            'name': 'algorithm1',
            'metric_name': 'test_metric_name',
            'algorithm_type': 'katusha',
            'control_share': CONTROL_SHARE,
        },
    },
)
@pytest.mark.skip(reason='this handle is not supported anymore')
async def test_create_suggest_small_budget(web_app_client, pgsql):
    response = await web_app_client.post(
        '/v1/suggests',
        json={
            'discounts_city': 'test_city',
            'budget': 2000,
            'smooth_threshold': 2.5,
            'calculations': [
                {
                    'algorithm_id': 'kt',
                    'plot': [
                        {
                            'x_label': 'x',
                            'y_label': 'y',
                            'data': [[1, 2], [3, 4]],
                        },
                    ],
                    'fixed_discounts': [
                        {'segment': 'control', 'discount_value': 0},
                    ],
                },
            ],
        },
    )

    assert response.status == 200
    content = await response.json()

    assert content == EXPECTED_DISCOUNT_SMALL_BUDGET
