package ru.yandex.metrika.cdp.core.tests.medium.steps;


import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeoutException;

import org.awaitility.core.ConditionTimeoutException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Component;

import ru.yandex.kikimr.persqueue.consumer.SyncConsumer;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.ConsumerReadResponse;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.data.MessageBatch;
import ru.yandex.metrika.cdp.dao.ClientsDao;
import ru.yandex.metrika.cdp.dao.OrdersDao;
import ru.yandex.metrika.cdp.dto.core.Client;
import ru.yandex.metrika.cdp.dto.core.ClientKey;
import ru.yandex.metrika.cdp.dto.core.ClientUpdate;
import ru.yandex.metrika.cdp.dto.core.Order;
import ru.yandex.metrika.cdp.dto.core.OrderKey;
import ru.yandex.metrika.cdp.dto.core.OrderUpdate;
import ru.yandex.metrika.cdp.processing.dto.matching.CdpClientIdChange;
import ru.yandex.metrika.cdp.processing.proto.CdpClientIdChangeProtoSerializer;
import ru.yandex.metrika.cdp.proto.ClientKeyProtoSerializer;
import ru.yandex.metrika.cdp.proto.OrderKeyProtoSerializer;
import ru.yandex.metrika.dbclients.ydb.async.QueryExecutionContext;
import ru.yandex.metrika.lb.serialization.proto.ProtoSerializer;
import ru.yandex.metrika.lb.waitable.WaitingLogbrokerWriter;
import ru.yandex.qatools.allure.annotations.Step;

import static java.util.concurrent.TimeUnit.MILLISECONDS;
import static java.util.stream.Collectors.toList;
import static org.awaitility.Awaitility.await;

@Component
public class DataSteps {

    @Autowired
    private WaitingLogbrokerWriter<OrderUpdate> orderUpdatesDownstream;

    @Autowired
    private WaitingLogbrokerWriter<ClientUpdate> clientUpdatesDownstream;

    @Autowired
    private OrdersDao ordersDao;

    @Autowired
    private ClientsDao clientsDao;

    @Autowired
    @Qualifier("orderUpdatesSyncConsumer")
    private SyncConsumer orderKeysSyncConsumer;

    @Autowired
    private OrderKeyProtoSerializer orderKeyProtoSerializer;

    @Autowired
    @Qualifier("clientUpdatesSyncConsumer")
    private SyncConsumer clientKeysSyncConsumer;

    @Autowired
    private ClientKeyProtoSerializer clientKeyProtoSerializer;

    @Autowired
    @Qualifier("cdpClientIdChangesConsumer")
    private SyncConsumer cdpClientIdChangesConsumer;

    @Autowired
    private CdpClientIdChangeProtoSerializer cdpClientIdChangeProtoSerializer;

    @Autowired
    @Qualifier("changedEmailsAndPhonesConsumer")
    private SyncConsumer changedEmailsAndPhonesConsumer;


    @Step("Подать апдейты клиентов на вход демону")
    public void writeClientUpdates(List<ClientUpdate> clientUpdates) {
        clientUpdatesDownstream.writeBatchAsync(clientUpdates).join();
    }

    @Step("Подать апдейты заказов на вход демону")
    public void writeOrderUpdates(List<OrderUpdate> orderUpdates) {
        orderUpdatesDownstream.writeBatchAsync(orderUpdates).join();
    }

    @Step("Подождать пока апдейты клиентов обработаются демоном")
    public void waitClientUpdatesProcessing() throws InterruptedException {
        clientUpdatesDownstream.waitProcessing();
    }

    @Step("Подождать пока апдейты заказов обработаются демоном")
    public void waitOrderUpdatesProcessing() throws InterruptedException {
        orderUpdatesDownstream.waitProcessing();
    }

    @Step("Подать апдейты клиентов на вход демону и подождать их процессинга")
    public void writeClientUpdatesAndWaitProcessing(List<ClientUpdate> clientUpdates) throws InterruptedException {
        writeClientUpdates(clientUpdates);
        waitClientUpdatesProcessing();
    }

    @Step("Подать апдейты заказов на вход демону и подождать их процессинга")
    public void writeOrderUpdatesAndWaitProcessing(List<OrderUpdate> orderUpdates) throws InterruptedException {
        writeOrderUpdates(orderUpdates);
        waitOrderUpdatesProcessing();
    }

    @Step("Прочитать клиентов из YDB")
    public List<Client> readClientsFromYdb(List<ClientKey> clientKeys) {
        return clientsDao.get(clientKeys);
    }

    @Step("Записать клиенток в YDB")
    public void writeInitialStateOfClientsYdb(List<Client> clients) {
        clientsDao.save(clients);
    }

    @Step("Прочитать заказы из YDB")
    public List<Order> readOrdersFromYdb(List<OrderKey> orderKeys) {
        return ordersDao.getAsync(orderKeys, QueryExecutionContext.read()).join();
    }

    @Step("Записать заказы в YDB")
    public void writeInitialStateOfOrdersYdb(List<Order> orders) {
        ordersDao.saveAsync(orders, QueryExecutionContext.write()).join();
    }

    @Step("Прочитать ключи изменившихся заказов из выходного топика")
    public List<OrderKey> readOutputOrderKeysFromLB() {
        return readResultFromLogbroker(orderKeysSyncConsumer, orderKeyProtoSerializer);
    }

    @Step("Прочитать cdpClientIdChange из выходного топика")
    public List<CdpClientIdChange> readOutputClientIdChangeFromLB() {
        return readResultFromLogbroker(cdpClientIdChangesConsumer, cdpClientIdChangeProtoSerializer);
    }

    @Step("Прочитать ключи изменившихся клиентов из выходного топика")
    public List<ClientKey> readOutputClientKeysFromLB() {
        return readResultFromLogbroker(clientKeysSyncConsumer, clientKeyProtoSerializer);
    }

    @Step("Прочитать ключи клиентов в которых изменились емейлы и телефоны")
    public List<ClientKey> readOutputChangedEmailsAndPhonesClientKeysFromLB() {
        return readResultFromLogbroker(changedEmailsAndPhonesConsumer, clientKeyProtoSerializer);
    }

    @Step("Очистить топик для изменившихся емейлов")
    public void clearChangedEmailsAndPhonesClientKeysTopic() {
        clearLogbroker(changedEmailsAndPhonesConsumer);
    }

    @Step("Очистить выходной топик с ключами клиентов")
    public void clearClientKeysTopic() {
        clearLogbroker(clientKeysSyncConsumer);
    }

    @Step("Очистить топик с изменениям cdpClientId")
    public void clearClientIdChangeTopic() {
        clearLogbroker(cdpClientIdChangesConsumer);
    }

    @Step("Очистить выходной топик с ключами заказов")
    public void clearOrderKeysTopic() {
        clearLogbroker(orderKeysSyncConsumer);
    }


    private <T> List<T> readResultFromLogbroker(SyncConsumer syncConsumer, ProtoSerializer<T> serializer) {
        List<MessageBatch> messageBatches = new ArrayList<>();
        boolean isAnyRead = true;
        while (isAnyRead) {
            try {
                await().atMost(3000, MILLISECONDS)
                        .pollInterval(100, MILLISECONDS)
                        .ignoreException(InterruptedException.class)
                        .until(() -> {
                            ConsumerReadResponse read = syncConsumer.read();
                            if (read != null && read.getBatches() != null && read.getBatches().size() > 0) {
                                messageBatches.addAll(read.getBatches());
                                syncConsumer.commit(read.getCookie());
                                Thread.sleep(1000);
                                return true;
                            }
                            return false;
                        });
            } catch (ConditionTimeoutException e) {
                isAnyRead = false;
            }
        }

        return messageBatches.stream()
                .flatMap(messageBatch -> messageBatch.getMessageData().stream())
                .map(messageData -> serializer.deserialize(messageData.getRawData()))
                .collect(toList());
    }

    private void clearLogbroker(SyncConsumer consumer) {
        boolean isAnyRead = true;
        while (isAnyRead) {
            try {
                ConsumerReadResponse read = consumer.read();
                if (read != null && read.getBatches() != null && read.getBatches().size() > 0) {
                    consumer.commit(read.getCookie());
                } else {
                    isAnyRead = false;
                }
            } catch (InterruptedException | TimeoutException ignored) {
            }
        }
    }
}
