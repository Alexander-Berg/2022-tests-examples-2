package ru.yandex.metrika.cdp.core.tests.medium.ydb;

import java.time.Instant;
import java.util.List;
import java.util.stream.Collectors;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.metrika.cdp.core.spring.CdpCoreTestConfig;
import ru.yandex.metrika.cdp.core.tests.medium.AbstractCdpCoreTest;
import ru.yandex.metrika.cdp.dto.core.OrderUpdate;

import static org.assertj.core.api.Assertions.assertThat;


@RunWith(SpringRunner.class)
@ContextConfiguration(classes = CdpCoreTestConfig.class)
public class OrderUpdatesYdbTest extends AbstractCdpCoreTest {

    @Test
    public void correctlyProcessSingleOrderUpdateAndWriteToYdb() throws InterruptedException {
        var orderUpdates = List.of(ORDER_SAVE);

        testSteps.writeOrderUpdatesAndCheckYdb(orderUpdates);
    }

    @Test
    public void correctlyUpdatesSingleOrderUpdateAndWriteToYdb() throws InterruptedException {
        dataSteps.writeOrderUpdatesAndWaitProcessing(List.of(ORDER_SAVE));

        var orderUpdates = List.of(ORDER_UPDATE);

        testSteps.writeOrderUpdatesAndCheckYdb(orderUpdates);
    }

    @Test
    public void correctlySaveLastUploading() throws InterruptedException {
        var orderUpdates = List.of(ORDER_SAVE);

        dataSteps.writeOrderUpdatesAndWaitProcessing(orderUpdates);

        var orderKeys = orderUpdates.stream().map(orderUpdate -> orderUpdate.getOrder().getKey()).collect(Collectors.toList());

        var ordersFromYdb = dataSteps.readOrdersFromYdb(orderKeys);

        var expected = orderUpdates.stream().map(OrderUpdate::getUploadingId).collect(Collectors.toList()).get(0);

        assertThat(ordersFromYdb).hasSize(1);
        assertThat(ordersFromYdb.get(0).getLastUploadings()).containsExactly(expected);
    }

    @Test
    public void correctlyUpdatesLastUploading() throws InterruptedException {
        dataSteps.writeOrderUpdatesAndWaitProcessing(List.of(ORDER_SAVE));

        var orderUpdates = List.of(ORDER_UPDATE);

        dataSteps.writeOrderUpdatesAndWaitProcessing(orderUpdates);

        var orderKeys = orderUpdates.stream().map(orderUpdate -> orderUpdate.getOrder().getKey()).collect(Collectors.toList());

        var ordersFromYdb = dataSteps.readOrdersFromYdb(orderKeys);

        assertThat(ordersFromYdb).hasSize(1);
        assertThat(ordersFromYdb.get(0).getLastUploadings()).hasSize(2);
        assertThat(ordersFromYdb.get(0).getLastUploadings()).containsExactly(ORDER_SAVE.getUploadingId(), ORDER_UPDATE.getUploadingId());
    }

    @Test
    public void correctlySavesSystemLastUploading() throws InterruptedException {
        var orderUpdates = List.of(ORDER_SAVE);

        var someTimestampBeforeUploading = Instant.now();

        dataSteps.writeOrderUpdatesAndWaitProcessing(orderUpdates);

        var orderKeys = orderUpdates.stream().map(orderUpdate -> orderUpdate.getOrder().getKey()).collect(Collectors.toList());

        var ordersFromYdb = dataSteps.readOrdersFromYdb(orderKeys);

        assertThat(ordersFromYdb).hasSize(1);

        assertThat(ordersFromYdb.get(0).getSystemLastUpdate()).isAfter(someTimestampBeforeUploading);
    }

    @Test
    public void correctlyUpdatesSystemLastUploading() throws InterruptedException {
        dataSteps.writeOrderUpdatesAndWaitProcessing(List.of(ORDER_SAVE));

        var someTimestempAfterSaveAndBeforeUpdate = Instant.now();
        var orderUpdates = List.of(ORDER_UPDATE);

        dataSteps.writeOrderUpdatesAndWaitProcessing(orderUpdates);

        var orderKeys = orderUpdates.stream().map(orderUpdate -> orderUpdate.getOrder().getKey()).collect(Collectors.toList());

        var clientsFromYdb = dataSteps.readOrdersFromYdb(orderKeys);

        assertThat(clientsFromYdb).hasSize(1);
        assertThat(clientsFromYdb.get(0).getSystemLastUpdate()).isAfterOrEqualTo(someTimestempAfterSaveAndBeforeUpdate);
    }
}
