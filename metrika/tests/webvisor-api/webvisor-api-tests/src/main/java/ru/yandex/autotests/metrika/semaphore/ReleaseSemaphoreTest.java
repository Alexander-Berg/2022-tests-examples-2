package ru.yandex.autotests.metrika.semaphore;

import com.hazelcast.core.HazelcastInstance;
import com.hazelcast.core.ISemaphore;
import org.apache.log4j.LogManager;
import org.apache.log4j.Logger;
import org.junit.Test;
import ru.yandex.autotests.metrika.hazelcast.HazelcastFactory;
import ru.yandex.autotests.metrika.properties.MetrikaApiProperties;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

@Features("Семафор")
@Stories({"Семафор"})
@Title("Освобождение семафора")
public class ReleaseSemaphoreTest {

    private static final Logger log = LogManager.getLogger(ReleaseSemaphoreTest.class);

    private static final HazelcastInstance HAZELCAST_INSTANCE = HazelcastFactory.getInstance();

    @Test
    public void release() {
        String semaphoreName = String.format("%s:%s", MetrikaApiProperties.getInstance().getApiSemaphoreNamePrefix(),
                MetrikaApiProperties.getInstance().getApiSemaphorePermits());
        int permits = MetrikaApiProperties.getInstance().getApiSemaphorePermits();

        log.info(String.format("Semaphore name: '%s', permits: %s", semaphoreName, permits));

        
        log.info("Create semaphore object");
        ISemaphore semaphore = HAZELCAST_INSTANCE.getSemaphore(semaphoreName);
        log.info("Initialize semaphore");
        semaphore.init(permits);
        log.info(String.format("Available permits: %s", semaphore.availablePermits()));

        log.info(String.format("Try to release %s permits", permits));

        semaphore.release(permits);
        log.info(String.format("Available permits: %s", semaphore.availablePermits()));
    }
}
