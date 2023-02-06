package ru.yandex.autotests.metrika.filters;

import org.apache.commons.lang3.StringUtils;
import ru.yandex.autotests.metrika.data.report.v1.enums.ReportFilterType;

import static ru.yandex.autotests.metrika.filters.Node.left;

/**
 * Created by konkov on 11.06.2015.
 */
public abstract class UnaryOperator implements Expression {

    private final Expression argument;
    private final String operator;

    protected UnaryOperator(String operator, Expression argument) {
        this.argument = argument;
        this.operator = operator;
    }

    public Expression and(Expression expression) {
        return left(this).and(expression);
    }

    public Expression or(Expression expression) {
        return left(this).or(expression);
    }

    @Override
    public String toString() {
        return build();
    }

    @Override
    public String build(ReportFilterType type) {
        return argument != null
                ? operator + "(" + argument.build() + ")"
                : StringUtils.EMPTY;
    }
}
