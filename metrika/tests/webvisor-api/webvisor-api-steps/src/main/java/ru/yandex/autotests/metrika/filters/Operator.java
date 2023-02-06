package ru.yandex.autotests.metrika.filters;

/**
 * Created by konkov on 08.10.2014.
 *
 * Перечисление всех поддерживаемых операторов в выражении фильтра
 */
public enum Operator {

    DEFINED("!n"),
    DEFINED_ALIAS(" DEFINED"),
    DEFINED_ALIAS2(" NOT UNDEFINED"),

    NOT_DEFINED("=n"),
    NOT_DEFINED_ALIAS(" UNDEFINED"),
    NOT_DEFINED_ALIAS2(" NOT DEFINED"),

    /**
     * ==	Равно
     */
    EQUAL("=="),
    EQUAL_ALIAS(" EQUALS "),

    /**
     * !=	Не равно
     */
    NOT_EQUAL("!="),
    NOT_EQUAL_ALIAS(" NOT EQUALS "),

    /**
     * >	Больше
     */
    GREATER(">"),

    /**
     * >=	Больше либо равно
     */
    GREATER_OR_EQUAL(">="),

    /**
     * <	Меньше
     */
    LESS("<"),

    /**
     * <=	Меньше либо равно
     */
    LESS_OR_EQUAL("<="),

    /**
     * =@	Является подстрокой
     */
    SUBSTRING("=@"),
    SUBSTRING_ALIAS(" CONTAINS "),
    SUBSTRING_ALIAS2(" INCLUDES "),

    /**
     * !@	Не является подстрокой
     */
    NOT_SUBSTRING("!@"),
    NOT_SUBSTRING_ALIAS(" NOT CONTAINS "),
    NOT_SUBSTRING_ALIAS2(" NOT INCLUDES "),

    /**
     * =~	Регулярное выражение
     */
    REGEX("=~"),
    REGEX_ALIAS(" MATCHES "),
    REGEX_ALIAS2(" REGEXP "),

    /**
     * !~	Не попадает под регулярное выражение
     */
    NOT_REGEX("!~"),
    NOT_REGEX_ALIAS(" NOT MATCHES "),
    NOT_REGEX_ALIAS2(" NOT REGEXP "),

    /**
     * =*	Равно, с возможностью поиска по *
     */
    EQUAL_STAR("=*"),
    EQUAL_STAR_ALIAS(" LIKE "),

    /**
     * !*	Не равно, с возможностью поиска по *
     */
    NOT_EQUAL_STAR("!*"),
    NOT_EQUAL_STAR_ALIAS(" NOT LIKE "),

    /**
     * =.   Входит в набор
     */
    IN("=."),
    IN_ALIAS(" IN "),

    /**
     * !.   Не входит в набор
     */
    NOT_IN("!."),
    NOT_IN_ALIAS(" NOT IN ");

    private final String value;

    Operator(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }
}
