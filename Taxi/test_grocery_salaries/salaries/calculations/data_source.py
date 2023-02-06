# pylint: disable=W0212
import pandas as pd

from grocery_salaries.salaries.calculations.data_source import (
    AdjustmentsDataSource,
)


def test_exclude_technical_adjustments():
    adjustments = pd.DataFrame(
        columns=['salary_adjustment_amt', 'reason_id', 'comment_text'],
        data=[
            (100.0, 498, 'Компенсация'),
            (100.0, 333, 'за прохождение осмотра'),  # обычная корректировка
            # Технические корректировки (должны быть исключены):
            (232.0, 696, 'Пропуск запланированного слота/Уход раньше'),
            (666.0, 809, 'Соцвыплаты НЕТО для отчёта по CPO'),
            (300.0, 333, 'Вознаграждение доставщика.'),
        ],
    )

    filtered_adjustments = (
        AdjustmentsDataSource._exclude_technical_adjustments(adjustments)
    )

    expected_result = pd.DataFrame(
        columns=['salary_adjustment_amt', 'reason_id', 'comment_text'],
        data=[
            (100.0, 498, 'Компенсация'),
            (100.0, 333, 'за прохождение осмотра'),
        ],
    )

    pd.testing.assert_frame_equal(filtered_adjustments, expected_result)
