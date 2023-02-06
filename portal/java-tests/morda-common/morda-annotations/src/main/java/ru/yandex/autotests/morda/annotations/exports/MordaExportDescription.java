package ru.yandex.autotests.morda.annotations.exports;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 16/08/15
 */
@Target({ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
public @interface MordaExportDescription {
    String name();
    Class<?> clazz();
    boolean needApprove() default true;
}
