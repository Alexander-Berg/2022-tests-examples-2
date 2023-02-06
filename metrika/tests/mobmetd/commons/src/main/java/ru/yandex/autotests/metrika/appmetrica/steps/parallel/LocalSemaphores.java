package ru.yandex.autotests.metrika.appmetrica.steps.parallel;

import ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties;

import java.util.List;
import java.util.concurrent.Semaphore;

/**
 * Если тесты запускаются из IDEA, используем локальный семафор
 */
final class LocalSemaphores extends AbstractSemaphores<Semaphore> {

    public LocalSemaphores(List<Integer> allSemaphoreIds) {
        init(allSemaphoreIds);
    }

    @Override
    public void acquire(Integer semaphoreId) throws InterruptedException {
        get(semaphoreId).acquire();
    }

    @Override
    public void release(Integer semaphoreId) {
        get(semaphoreId).release();
    }

    @Override
    protected Semaphore initSemaphore(Integer semaphoreId) {
        return new Semaphore(AppMetricaApiProperties.apiProperties().getReportSemaphorePermits());
    }

}
