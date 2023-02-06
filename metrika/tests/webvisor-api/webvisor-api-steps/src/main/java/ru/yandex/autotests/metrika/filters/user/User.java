package ru.yandex.autotests.metrika.filters.user;

import ru.yandex.autotests.metrika.data.report.v1.enums.ReportFilterType;
import ru.yandex.autotests.metrika.filters.Expression;

import static ru.yandex.autotests.metrika.filters.Node.left;

/**
 * Created by konkov on 18.06.2015.
 */
public class User implements Expression {
    private final String startDate;
    private final String endDate;
    private final ConditionSequence conditions;

    private User(String startDate, String endDate, ConditionSequence conditions) {
        this.startDate = startDate;
        this.endDate = endDate;
        this.conditions = conditions;
    }

    public static User user(String startDate, String endDate) {
        return new User(startDate, endDate, null);
    }

    public static User user(String startDate, String endDate, ConditionSequence conditions) {
        return new User(startDate, endDate, conditions);
    }

    public static Condition cond(String namespace, Expression filter) {
        return new Condition(namespace, filter);
    }

    @Override
    public String build(ReportFilterType type) {
        return conditions != null
                ? String.format("USER_PATTERN(%s, %s, %s)", startDate, endDate, conditions.build())
                : String.format("USER_PATTERN(%s, %s)", startDate, endDate);
    }

    @Override
    public String toString() {
        return build();
    }

    @Override
    public Expression and(Expression expression) {
        return left(this).and(expression);
    }

    @Override
    public Expression or(Expression expression) {
        return left(this).or(expression);
    }
}
