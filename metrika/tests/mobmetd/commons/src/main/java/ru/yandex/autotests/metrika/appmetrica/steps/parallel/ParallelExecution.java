package ru.yandex.autotests.metrika.appmetrica.steps.parallel;

import java.lang.annotation.Retention;
import java.lang.annotation.Target;

import static java.lang.annotation.ElementType.METHOD;
import static java.lang.annotation.RetentionPolicy.RUNTIME;

/**
 * Поскольку степы запускаются на продовом КХ, мы хотим для каждого степа контролировать возможность его параллельного запуска.
 * <p>
 * Аннотация {@link ParallelExecution} обязательна потому что автор степа
 * должен задуматься о возможности запускать его параллельно.
 * <p>
 * Золотое правило: если степ под капотом ходит в КХ, то запускать его параллельно нельзя.
 */
@Target(METHOD)
@Retention(RUNTIME)
public @interface ParallelExecution {

    Permission value();

    enum Permission {
        /**
         * Разрешаем бесконечный параллелизм (на самом деле тот, который прописан в акве)
         */
        ALLOW,

        /**
         * Одновременно может работать только один экземпляр степа. Плата за использование продакшен КХ.
         * Контролируется конфигом {@code api.report-semaphore-permits}
         */
        RESTRICT;
    }
}
