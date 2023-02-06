package ru.yandex.metrika.zkqueue.framework.listener;

import java.util.Optional;

import com.google.common.collect.ImmutableList;
import org.apache.curator.framework.CuratorFramework;
import org.apache.curator.test.TestingServer;
import org.junit.After;
import org.junit.Before;

import ru.yandex.metrika.zkqueue.api.ConsumeTimes;
import ru.yandex.metrika.zkqueue.api.UnitOfWork;
import ru.yandex.metrika.zkqueue.api.redelivery.ConsumingPolicy;
import ru.yandex.metrika.zkqueue.core.ZkQueue;
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
 * Base class for framework tests.
 */
public abstract class BaseFrameworkTest {

    /**
     * ZK server running on random port in localhost
     */
    protected TestingServer server;

    /**
     * Underlying curator clients
     */
    private CuratorFramework curator1;

    /**
     * Queue instances
     */
    protected ZkQueue queue;

    protected ZkQueue queue1;

    @Before
    public void setup() throws Exception {
        server = new TestingServer();
        server.start();

        queue1 = new ZkQueue(new CuratorManager(new ZkOptions(
                server.getConnectString(), sessionTimeout(), connectionTimeout(), retryPolicy())));
        queue1.createIfNeeded(ImmutableList.of(destination1(), destination2()));
        curator1 = queue1.currentCurator();

        // Shortcuts for tests where only one client need to be used
        queue = queue1;
    }

    protected void put1(String destination, String payload) throws Exception {
        try (UnitOfWork tx = queue1.newTransaction()) {
            tx.put(destination, payload);
            tx.commit();
        }
    }

    protected Optional<String> take1(String destination) throws Exception {
        return take1(destination, new ConsumeTimes(5));
    }

    private Optional<String> take1(String destination, ConsumingPolicy consumingPolicy) throws Exception {
        return take(queue1, destination, consumingPolicy);
    }

    /**
     * Expire the session and wait until expiration is visible
     */
    protected void expireSession1() {
        Troublemaker.expireCuratorSession(curator1);
    }

    protected void disconnectClient1() {
        Troublemaker.disconnectClient(curator1);
    }

    protected void restartServer1() {
        Troublemaker.restartServer(server);
    }

    @After
    public void teardown() {
        // Queue closing will close underlying curator instances
        try {
            queue1.close();
            server.stop();
        } catch (Exception e) {
            // Just ignore
        }
    }

}
