package ru.yandex.autotests.metrika.appmetrica.steps.parallel;

public interface SemaphoreProvider<T> {

    T createSemaphore(Integer semaphoreId);

}
