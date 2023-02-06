package ru.yandex.autotests.metrika.utils;


import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * @author zgmnkv
 */
@Target({ElementType.ANNOTATION_TYPE, ElementType.FIELD})
@Retention(RetentionPolicy.RUNTIME)
public @interface CsvField {

    /**
     * Name of column
     * @return name of column
     */
    String value();

    /**
     * Order of column in CSV file
     * @return order of column
     */
    int order() default 0;
}
