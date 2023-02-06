package ru.yandex.metrika.zkqueue.core;

import java.util.Optional;

import com.google.common.collect.ImmutableList;
import org.apache.curator.framework.CuratorFramework;
import org.apache.curator.test.TestingServer;
import org.junit.After;
import org.junit.Before;

import ru.yandex.metrika.zkqueue.api.ConsumeTimes;
import ru.yandex.metrika.zkqueue.api.UnitOfWork;
import ru.yandex.metrika.zkqueue.api.redelivery.ConsumingPolicy;
import ru.yandex.metrika.zkqueue.core.curator.CuratorManager;
import ru.yandex.metrika.zkqueue.core.curator.ZkOptions;
import ru.yandex.metrika.zkqueue.test.Troublemaker;

import static ru.yandex.metrika.zkqueue.test.ZkTesting.connectionTimeout;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.destination1;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.destination2;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.retryPolicy;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.sessionTimeout;
import static ru.yandex.metrika.zkqueue.test.ZkTesting.take;

/**
 * Base class for tests.
 * Uses several queues with local ZK instance.
 * Defines helpful operations.
 */
abstract class BaseCoreTest {

    /**
     * ZK server running on random port in localhost
     */
    TestingServer server;

    /**
     * Underlying curator clients
     */
    CuratorFramework curator1;

    /**
     * Queue instances
     */
    ZkQueue queue;

    ZkQueue queue1;

    ZkQueue queue2;

    @Before
    public void setup() throws Exception {
        server = new TestingServer();
        server.start();

        queue1 = new ZkQueue(new CuratorManager(new ZkOptions(
                server.getConnectString(), sessionTimeout(), connectionTimeout(), retryPolicy())));
        queue1.createIfNeeded(ImmutableList.of(destination1(), destination2()));
        curator1 = queue1.currentCurator();

        queue2 = new ZkQueue(new CuratorManager(new ZkOptions(
                server.getConnectString(), sessionTimeout(), connectionTimeout(), retryPolicy())));
        queue2.createIfNeeded(ImmutableList.of(destination1(), destination2()));

        // Shortcuts for tests where only one client need to be used
        queue = queue1;
    }

    protected void put1(String destination, String payload) throws Exception {
        try (UnitOfWork tx = queue1.newTransaction()) {
            tx.put(destination, payload);
            tx.commit();
        }
    }

    Optional<String> take1() throws Exception {
        return take1(destination1(), new ConsumeTimes(5));
    }

    private Optional<String> take1(String destination, ConsumingPolicy consumingPolicy) throws Exception {
        return take(queue1, destination, consumingPolicy);
    }

    Optional<String> take2() throws Exception {
        return take2(destination1(), new ConsumeTimes(5));
    }

    private Optional<String> take2(String destination, ConsumingPolicy consumingPolicy) throws Exception {
        return take(queue2, destination, consumingPolicy);
    }

    /**
     * Expire the session and wait until expiration is visible
     */
    void expireSession1() {
        Troublemaker.expireCuratorSession(curator1);
    }

    void disconnectClient1() {
        Troublemaker.disconnectClient(curator1);
    }

    void killServer1() {
        Troublemaker.stopServer(server);
    }

    @After
    public void teardown() {
        // Queue closing will close underlying curator instances
        try {
            queue1.close();
            queue2.close();
            server.stop();
        } catch (Exception e) {
            // Just ignore
        }
    }

}
