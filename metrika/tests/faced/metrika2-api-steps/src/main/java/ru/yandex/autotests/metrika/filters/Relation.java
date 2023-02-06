package ru.yandex.autotests.metrika.filters;

/**
 * Created by konkov on 08.05.2015.
 */
public class Relation extends UnaryOperator {

    private final static String EXISTS = "EXISTS";
    private final static String ALL = "ALL";
    private final static String NONE = "NONE";
    public static final String EXTENDED_OPERATOR_TEMPLATE = "%s %s WITH";

    private Relation(String operator, Expression argument) {
        super(operator, argument);
    }

    private Relation(String attribute, String operator, Expression argument) {
        super(getExtendedOperator(attribute, operator), argument);
    }

    private static String getExtendedOperator(String attribute, String operator) {
        return String.format(EXTENDED_OPERATOR_TEMPLATE, operator, attribute);
    }

    public static Expression exists(Expression expression) {
        return new Relation(EXISTS, expression);
    }

    public static Expression exists(String attribute, Expression expression) {
        return new Relation(attribute, EXISTS, expression);
    }

    public static Expression all(Expression expression) {
        return new Relation(ALL, expression);
    }

    public static Expression all(String attribute, Expression expression) {
        return new Relation(attribute, ALL, expression);
    }

    public static Expression none(Expression expression) {
        return new Relation(NONE, expression);
    }

    public static Expression none(String attribute, Expression expression) {
        return new Relation(attribute, NONE, expression);
    }
}
