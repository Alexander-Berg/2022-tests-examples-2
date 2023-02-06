package ru.yandex.autotests.metrika.appmetrica.steps.parallel;

import com.hazelcast.core.HazelcastInstance;
import com.hazelcast.core.ISemaphore;
import ru.yandex.autotests.metrika.appmetrica.properties.AppMetricaApiProperties;

import java.util.List;

/**
 * Адаптер распределенного семафора, через который будут идти запуски в акве
 */
public final class HazelcastSemaphores extends AbstractSemaphores<ISemaphore> {

    private final HazelcastInstance hazelcast;

    HazelcastSemaphores(HazelcastInstance hazelcast, List<Integer> semaphoreIds) {
        this.hazelcast = hazelcast;
        init(semaphoreIds);
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
    protected ISemaphore initSemaphore(Integer semaphoreId) {
        final String name = AppMetricaApiProperties.apiProperties().getReportSemaphoreName();
        final int permits = AppMetricaApiProperties.apiProperties().getReportSemaphorePermits();

        final ISemaphore semaphore = hazelcast.getSemaphore(String.format("%s-%s:%s", name, semaphoreId, permits));
        semaphore.init(permits);
        return semaphore;
    }

}
