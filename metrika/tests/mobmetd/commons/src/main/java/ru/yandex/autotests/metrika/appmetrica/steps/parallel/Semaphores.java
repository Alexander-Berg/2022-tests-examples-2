package ru.yandex.autotests.metrika.appmetrica.steps.parallel;

import java.util.List;

/**
 * Делаем общий минимальный интерфейс для семафоров
 */
public interface Semaphores {

    /**
     * Занять указанные семафоры.
     */
    void acquire(List<Integer> semaphoreIds) throws InterruptedException;

    /**
     * Освободить указанные семафоры.
     */
    void release(List<Integer> semaphoreIds);

}
