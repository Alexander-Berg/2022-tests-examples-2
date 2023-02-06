from tqdm import tqdm_notebook

from taxi_pyml.eats.support import types


def test(model, dataset, device):
    return [
        model.apply(
            types.Request(
                **{
                    'feedback': types.Feedback(
                        **{
                            'comment': text,
                            'predefined_comments': predef_comments,
                            'is_required': is_feedback_required,
                            'rating': mark,
                        },
                    ),
                    'app_type': 'superapp',
                    'delay_time': 15,
                    'is_order_feedback': True,
                    'is_lavka': False,
                    'user_grade': 'neutral',
                    'order_nr': '20191009-239942',
                    'user_id': 'sjdfksjfsk',
                    'delivery_at': '2019-10-09T08:02:23+03:00',
                    'delivered_at': '2019-10-09T08:15:45+03:00',
                },
            ),
            device,
        )
        for (
            text,
            predef_comments,
            is_feedback_required,
            mark,
        ) in tqdm_notebook(zip(*dataset))
    ]
