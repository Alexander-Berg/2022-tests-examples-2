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
public class OrderKeyLogbrokerTest extends AbstractCdpCoreTest {

    @Before
    public void cleanTopics() {
        dataSteps.clearOrderKeysTopic();
    }

    @Test
    public void correctlyWritesOrderKeyToDownstream() throws InterruptedException {
        var orderUpdates = List.of(ORDER_SAVE);

        testSteps.writeOrderUpdatesAndCheckTopicWithChangedOrders(orderUpdates);
    }

    @Test
    public void correctlyWritesOrderKeyToDownstreamAfterUpdate() throws InterruptedException {
        var orderUpdates = List.of(ORDER_SAVE, ORDER_UPDATE);

        testSteps.writeOrderUpdatesAndCheckTopicWithChangedOrders(orderUpdates);
    }


}
