package ru.yandex.autotests.mordacommonsteps.annotations;

import ru.yandex.autotests.utils.morda.url.Domain;

import java.lang.annotation.Retention;
import java.lang.annotation.Target;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27.05.13
 *
 * @DomainDependent(pattern = "http://www.yandex%s/", ru = Domain.KZ)
 * public static String href;
 */

@Retention(java.lang.annotation.RetentionPolicy.RUNTIME)
@Target({java.lang.annotation.ElementType.FIELD})
public @interface DomainDependent {
    String pattern();

    Domain ru() default Domain.RU;

    Domain ua() default Domain.UA;

    Domain by() default Domain.BY;

    Domain kz() default Domain.KZ;
}
