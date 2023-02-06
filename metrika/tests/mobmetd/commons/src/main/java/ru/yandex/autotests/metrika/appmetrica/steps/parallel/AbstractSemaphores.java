package ru.yandex.autotests.metrika.appmetrica.steps.parallel;

import com.google.common.base.Preconditions;

import java.util.List;
import java.util.Map;

import static java.util.function.Function.identity;
import static java.util.stream.Collectors.toMap;

/**
 * Абстрактная реализация семафоров, требующая предварительного вызова init.
 */
public abstract class AbstractSemaphores<T> implements Semaphores {

    /**
     * Объекты семафоров по id
     */
    private Map<Integer, T> semaphores;

    /**
     * Получить заранее подготовленный объект семафора по id
     */
    protected T get(Integer semaphoreId) {
        return semaphores.get(semaphoreId);
    }

    /**
     * Подготавливает объекты семафоров для заранее известного набора их id.
     * Последующие вызовы {@link #acquire} и {@link #release} допускаются только с инициализированными семафорами.
     */
    protected void init(List<Integer> allSemaphoreIds) {
        Preconditions.checkState(semaphores == null, "Semaphores were already initialized.");
        semaphores = allSemaphoreIds
                .stream()
                .collect(toMap(identity(), this::initSemaphore));
    }

    @Override
    public void acquire(List<Integer> semaphoreIds) throws InterruptedException {
        for (Integer semaphoreId : semaphoreIds) {
            acquire(semaphoreId);
        }
    }

    @Override
    public void release(List<Integer> semaphoreIds) {
        semaphoreIds.forEach(this::release);
    }

    /**
     * Подготовить объект семафора.
     */
    protected abstract T initSemaphore(Integer semaphoreId);

    /**
     * Занять указанный семафор.
     */
    protected abstract void acquire(Integer semaphoreId) throws InterruptedException;

    /**
     * Освободить указанный семафор.
     */
    protected abstract void release(Integer semaphoreId);

}
