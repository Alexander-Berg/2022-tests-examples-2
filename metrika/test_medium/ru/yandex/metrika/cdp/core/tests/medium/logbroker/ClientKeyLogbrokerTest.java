package ru.yandex.metrika.cdp.core.tests.medium.logbroker;

import java.util.List;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.metrika.cdp.core.spring.CdpCoreTestConfig;
import ru.yandex.metrika.cdp.core.tests.medium.AbstractCdpCoreTest;


@RunWith(SpringRunner.class)
@ContextConfiguration(classes = CdpCoreTestConfig.class)
public class ClientKeyLogbrokerTest extends AbstractCdpCoreTest {

    @Before
    public void cleanTopics() {
        dataSteps.clearClientKeysTopic();
    }

    @Test
    public void correctlyWritesClientKeyToDownstreamAfterSave() throws InterruptedException {
        var clientUpdates = List.of(CLIENT_SAVE);

        testSteps.writeClientUpdatesAndCheckTopicWithChangedClients(clientUpdates);
    }

    @Test
    public void correctlyWritesClientKeyToDownstreamAfterUpdate() throws InterruptedException {
        var clientUpdates = List.of(CLIENT_SAVE, CLIENT_UPDATE);

        testSteps.writeClientUpdatesAndCheckTopicWithChangedClients(clientUpdates);
    }

    @Test
    public void correctlyWritesClientKeyAfterOrderSave() throws InterruptedException {
        var orderUpdates = List.of(ORDER_SAVE);

        testSteps.writeOrderUpdatesAndCheckTopicWithChangedClients(orderUpdates);
    }

    @Test
    public void correctlyWritesClientKeyAfterOrderUpdate() throws InterruptedException {
        var orderUpdates = List.of(ORDER_SAVE, ORDER_UPDATE);

        testSteps.writeOrderUpdatesAndCheckTopicWithChangedClients(orderUpdates);
    }
}
