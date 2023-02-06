package ru.yandex.autotests.metrika.appmetrica.steps.parallel;

import com.hazelcast.core.HazelcastInstance;
import org.apache.log4j.LogManager;
import org.apache.log4j.Logger;
import ru.yandex.qatools.hazelcast.HazelcastClient;

/**
 * Точка входа для работы с кластером Hazelcast
 */
final class HazelcastFactory {

    private static final Logger log = LogManager.getLogger(HazelcastFactory.class);

    private static HazelcastInstance instance;

    static synchronized HazelcastInstance hazelcastInstance() {
        if (instance == null) {
            log.debug("Create singleton hazelcast client");

            instance = HazelcastClient.newHazelcastClient();

            Runtime.getRuntime().addShutdownHook(new Thread(() -> {
                try {
                    log.debug("Shutting down singleton hazelcast instance");
                    instance.shutdown();
                } catch (Throwable e) {
                    log.error("Exception in singleton hazelcast shutdown", e);
                }
            }));
        }

        return instance;
    }
}
