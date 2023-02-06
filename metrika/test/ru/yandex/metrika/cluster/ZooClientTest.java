package ru.yandex.metrika.cluster;

import org.apache.curator.framework.CuratorFramework;
import org.apache.curator.framework.imps.CuratorFrameworkState;
import org.apache.curator.test.TestingServer;
import org.apache.logging.log4j.Level;
import org.junit.After;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.dbclients.zookeeper.ZooClient;
import ru.yandex.metrika.util.app.ZooSettingsImpl;
import ru.yandex.metrika.util.log.Log4jSetup;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertSame;

public class ZooClientTest {

    private ZooClient target;
    TestingServer server;

    @Before
    public void setUp() throws Exception {
        Log4jSetup.basicSetup(Level.INFO);
        server = new TestingServer(2181);
        server.start();
        target = new ZooClient();
        ZooSettingsImpl settings = new ZooSettingsImpl("/ru/yandex/metrika-DEV", "localhost:2181");
        target.setSettings(settings);
        target.afterPropertiesSet();
    }

    @Test
    @Ignore
    public void testNumChildren2() throws Exception {
        int i = 42; //target.numChildren2("/ru/yandex/metrika-DEV");
        assertEquals(i, 29447);
    }

    @Test
    @Ignore
    public void testNumChildren() throws Exception {
        int i = target.numChildren("/ru/yandex/metrika-DEV");
        assertEquals(i, 29447);
    }

    @Test
    public void testRefreshClient() {
        CuratorFramework oldClient = this.target.getClient();
        target.refreshClient((client, newState) -> { });
        assertSame("Старый клиент остановлен", oldClient.getState(), CuratorFrameworkState.STOPPED);
        assertSame("Новый клиент готов", target.getClient().getState(), CuratorFrameworkState.STARTED);
    }

    @After
    public void after() throws Exception {
        server.stop();
        target.destroy();
    }

}
