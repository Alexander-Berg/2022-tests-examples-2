package ru.yandex.autotests.metrika.hazelcast;

import com.hazelcast.core.HazelcastInstance;
import org.apache.log4j.LogManager;
import org.apache.log4j.Logger;
import ru.yandex.qatools.hazelcast.HazelcastClient;

/**
 * Created by konkov on 27.02.2017.
 */
public final class HazelcastFactory {
    private static final Logger log = LogManager.getLogger(HazelcastFactory.class);

    private static HazelcastInstance instance;

    private HazelcastFactory() {
    }

    public static synchronized HazelcastInstance getInstance() {
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
