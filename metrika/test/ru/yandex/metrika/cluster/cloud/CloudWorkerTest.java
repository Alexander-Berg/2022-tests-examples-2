package ru.yandex.metrika.cluster.cloud;

import org.apache.curator.test.TestingServer;
import org.apache.logging.log4j.Level;
import org.junit.After;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.cluster.cloud.CloudWorker.State;
import ru.yandex.metrika.dbclients.zookeeper.ZooClient;
import ru.yandex.metrika.util.app.ZooSettingsImpl;
import ru.yandex.metrika.util.log.Log4jSetup;

import static java.util.concurrent.TimeUnit.MILLISECONDS;
import static org.awaitility.Awaitility.await;
import static org.junit.Assert.assertSame;

@Ignore
public class CloudWorkerTest {
    private CloudWorker cloudWorker;
    private TestingServer server;
    private ZooClient zooClient;

    @Before
    public void before() throws Exception {
        Log4jSetup.basicSetup(Level.INFO);
        String pathToListOfFreeDaemons = "/path/to/free/daemons";
        String daemonName = "visor3d";
        String balancerCommandsPath = "/path/to/balancer-daemons";
        server = new TestingServer(2181);
        server.start();

        zooClient = new ZooClient();
        zooClient.setSettings(new ZooSettingsImpl("/ru/yandex/metrika-DEV", "localhost:2181"));
        zooClient.afterPropertiesSet();
        zooClient.create(pathToListOfFreeDaemons, new byte[]{});
        zooClient.create(balancerCommandsPath, new byte[]{});

        MultiQueueProperties queuesProperties = new MultiQueueProperties();
        queuesProperties.setQueueDigits(3);
        queuesProperties.setQueuePrefix("layer");

        StickingLayerSelector layerSelector = new StickingLayerSelector();
        layerSelector.setZooClient(zooClient);
        layerSelector.setQueuesProperties(queuesProperties);
        layerSelector.setPathToListOfFreeDaemons(pathToListOfFreeDaemons);
        layerSelector.setBalancerCommandsPath(balancerCommandsPath);
        layerSelector.setDaemonName(daemonName);
        layerSelector.afterPropertiesSet();

        cloudWorker = new CloudWorker();
        cloudWorker.setLayerSelector(layerSelector);
        cloudWorker.setZooClient(zooClient);
        cloudWorker.handleContextRefresh(null);
        await().atMost(500, MILLISECONDS).pollInterval(100, MILLISECONDS).until(() -> cloudWorker.getState() == State.STARTED);
    }

    @Test
    public void test() throws Exception {
        server.stop();
        await().atMost(500, MILLISECONDS).pollInterval(100, MILLISECONDS).until(() -> cloudWorker.getState() == State.CLOSED);
        server.restart();
        await().atMost(2000, MILLISECONDS).pollInterval(100, MILLISECONDS).untilAsserted(() -> {
            assertSame("CloudWorker successfully restarted", cloudWorker.getState(), State.STARTED);
        });
    }

    @After
    public void after() throws Exception {
        cloudWorker.close();
        zooClient.destroy();
        server.stop();
    }
}
