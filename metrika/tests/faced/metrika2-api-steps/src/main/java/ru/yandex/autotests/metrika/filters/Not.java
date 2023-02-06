package ru.yandex.autotests.metrika.filters;

/**
 * Created by konkov on 11.06.2015.
 */
public class Not extends UnaryOperator {
    private final static String NOT = "NOT";

    protected Not(String operator, Expression argument) {
        super(operator, argument);
    }

    public static Expression not(Expression expression) {
        return new Not(NOT, expression);
    }
}
