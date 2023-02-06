package ru.yandex.autotests.metrika.filters;

import ru.yandex.autotests.metrika.data.report.v1.enums.ReportFilterType;

/**
 * Created by konkov on 08.10.2014.
 *
 * Интерфейс выражения фильтра
 */
public interface Expression {
    /**
     * @return строковое представление выражения фильтра
     */
    String build(ReportFilterType type);

    Expression and(Expression expression);

    Expression or(Expression expression);

    default String build() {
        return build(ReportFilterType.METRIKA);
    }
}
