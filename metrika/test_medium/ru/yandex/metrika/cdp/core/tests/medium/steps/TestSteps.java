package ru.yandex.metrika.cdp.core.tests.medium.steps;


import java.util.List;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import ru.yandex.metrika.cdp.dto.core.ClientKey;
import ru.yandex.metrika.cdp.dto.core.ClientUpdate;
import ru.yandex.metrika.cdp.dto.core.OrderKey;
import ru.yandex.metrika.cdp.dto.core.OrderUpdate;
import ru.yandex.metrika.cdp.processing.dto.matching.CdpClientIdChange;
import ru.yandex.qatools.allure.annotations.Step;

import static org.assertj.core.api.Assertions.assertThat;

@Component
public class TestSteps {

    @Autowired
    private DataSteps dataSteps;

    @Step("Подать апдейты клиентов на вход демону и проверить YDB")
    public void writeClientUpdatesAndCheckYdb(List<ClientUpdate> clientUpdates) throws InterruptedException {
        dataSteps.writeClientUpdatesAndWaitProcessing(clientUpdates);

        List<ClientKey> keys = clientUpdates.stream().map(update -> update.getClient().getKey()).collect(Collectors.toList());
        var clientsFromYdb = dataSteps.readClientsFromYdb(keys);

        var expected = clientUpdates.stream().map(ClientUpdate::getClient).collect(Collectors.toList());

        assertThat(clientsFromYdb).containsExactlyInAnyOrderElementsOf(expected);
    }

    @Step("Подать апдейты заказов на вход демону и проверить YDB")
    public void writeOrderUpdatesAndCheckYdb(List<OrderUpdate> orderUpdates) throws InterruptedException {
        dataSteps.writeOrderUpdatesAndWaitProcessing(orderUpdates);

        List<OrderKey> keys = orderUpdates.stream().map(update -> update.getOrder().getKey()).collect(Collectors.toList());
        var ordersFromYdb = dataSteps.readOrdersFromYdb(keys);

        var expected = orderUpdates.stream().map(OrderUpdate::getOrder).collect(Collectors.toList());

        assertThat(ordersFromYdb).containsExactlyInAnyOrderElementsOf(expected);
    }

    @Step("Подать апдейты клиентов на вход демону и проверить ключи в выходном топике")
    public void writeClientUpdatesAndCheckTopicWithChangedClients(List<ClientUpdate> clientUpdates) throws InterruptedException {
        dataSteps.writeClientUpdatesAndWaitProcessing(clientUpdates);

        var clientKeys = dataSteps.readOutputClientKeysFromLB();

        var expected = clientUpdates.stream().map(clientUpdate -> clientUpdate.getClient().getKey()).collect(Collectors.toList());

        assertThat(clientKeys).containsExactlyElementsOf(expected);
    }

    @Step("Подать апдейты заказов на вход демону и проверить ключи в выходном топике")
    public void writeOrderUpdatesAndCheckTopicWithChangedOrders(List<OrderUpdate> orderUpdates) throws InterruptedException {
        dataSteps.writeOrderUpdatesAndWaitProcessing(orderUpdates);

        var orderKeys = dataSteps.readOutputOrderKeysFromLB();

        var expected = orderUpdates.stream().map(orderUpdate -> orderUpdate.getOrder().getKey()).collect(Collectors.toList());

        assertThat(orderKeys).containsExactlyElementsOf(expected);
    }

    @Step("Подать апдейты клиентов на вход демону и проверить топик с изменившимися емейлами и телефонами")
    public void writeClientUpdatesAndCheckTopicWithChangedEmailsAndPhones(List<ClientUpdate> clientUpdates, List<ClientKey> expected) throws InterruptedException {
        dataSteps.writeClientUpdatesAndWaitProcessing(clientUpdates);

        var clientKeys = dataSteps.readOutputChangedEmailsAndPhonesClientKeysFromLB();

        assertThat(clientKeys).containsExactlyElementsOf(expected);
    }

    @Step("Подать апдейты  клиентов на вход демону и проверить топик с изменившимися clientId")
    public void writeClientUpdatesAndCheckTopicWithChangedClientId(List<ClientUpdate> clientUpdates, List<CdpClientIdChange> expected) throws InterruptedException {
        dataSteps.writeClientUpdatesAndWaitProcessing(clientUpdates);

        var cdpClientIdChanges = dataSteps.readOutputClientIdChangeFromLB();

        assertThat(cdpClientIdChanges).containsExactlyInAnyOrderElementsOf(expected);
    }

    @Step("Подать апдейты заказов на вход демону и проверить топик с изменившимися клиентами")
    public void writeOrderUpdatesAndCheckTopicWithChangedClients(List<OrderUpdate> orderUpdates) throws InterruptedException {
        dataSteps.writeOrderUpdatesAndWaitProcessing(orderUpdates);

        var clientKeys = dataSteps.readOutputClientKeysFromLB();

        var expected = orderUpdates.stream()
                .map(orderUpdate ->
                        new ClientKey(orderUpdate.getOrder().getCdpUid(), orderUpdate.getOrder().getCounterId()))
                .collect(Collectors.toList());

        assertThat(clientKeys).containsExactlyElementsOf(expected);
    }

}
