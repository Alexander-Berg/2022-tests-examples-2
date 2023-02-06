package ru.yandex.metrika.cdp.chwriter.tests.medium.steps;


import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import gnu.trove.set.TLongSet;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import ru.yandex.metrika.cdp.chwriter.data.ClientChRow;
import ru.yandex.metrika.cdp.chwriter.data.OrderChRow;
import ru.yandex.metrika.cdp.chwriter.processor.OrderAggregatesDaoYdb;
import ru.yandex.metrika.cdp.chwriter.tests.medium.CdpChWriterTestStateHolder;
import ru.yandex.metrika.cdp.dao.ClientsDao;
import ru.yandex.metrika.cdp.dao.OrdersDao;
import ru.yandex.metrika.cdp.dao.SchemaDao;
import ru.yandex.metrika.cdp.dto.core.Client;
import ru.yandex.metrika.cdp.dto.core.ClientKey;
import ru.yandex.metrika.cdp.dto.core.Order;
import ru.yandex.metrika.cdp.dto.core.OrderKey;
import ru.yandex.metrika.cdp.dto.schema.OrderStatus;
import ru.yandex.metrika.cdp.processing.dao.ClientIdMatchingDao;
import ru.yandex.metrika.cdp.processing.dao.ClientVersionsDao;
import ru.yandex.metrika.cdp.processing.dao.CryptaIdMatchingDao;
import ru.yandex.metrika.cdp.processing.dao.GluedYuidMatchingDao;
import ru.yandex.metrika.cdp.processing.dao.OrderVersionsDao;
import ru.yandex.metrika.cdp.processing.dto.export.ClientVersion;
import ru.yandex.metrika.cdp.processing.dto.export.OrderVersion;
import ru.yandex.metrika.dbclients.ydb.async.QueryExecutionContext;
import ru.yandex.qatools.allure.annotations.Step;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

@Component
public class TestSteps {

    @Autowired
    private DataSteps dataSteps;

    @Autowired
    private OrdersDao ordersDao;

    @Autowired
    private ClientsDao clientsDao;

    @Autowired
    private ClientVersionsDao clientVersionsDao;

    @Autowired
    private OrderVersionsDao orderVersionsDao;

    @Autowired
    private ClientIdMatchingDao clientIdMatchingDao;

    @Autowired
    private OrderAggregatesDaoYdb orderAggregatesDao;

    @Autowired
    private CryptaIdMatchingDao cryptaIdMatchingDao;

    @Autowired
    private GluedYuidMatchingDao gluedYuidMatchingDao;

    @Autowired
    private SchemaDao schemaDao;


    @Step("Подать заказы на вход демону и проверить версии в YDB")
    public void writeOrdersAndCheckYdb(CdpChWriterTestStateHolder testData) {
        dataSteps.writeOrderKeys(testData.getOrderKeys());

        var newVersions = dataSteps.readOrderVersionsFromYdb(testData.getOrderKeys());

        var expected = new ArrayList<>(testData.getOrderVersions().values());

        assertTrue("не все версии обновлены корректно",
                expected.stream().allMatch(oldVersion ->
                        newVersions.stream()
                                .filter(newVersion -> oldVersion.getKey().equals(newVersion.getKey()))
                                .allMatch(newVersion -> newVersion.getVersion() == oldVersion.getVersion())
                )
        );
    }

    @Step("Подать клиентов на вход демону и проверить версии в YDB")
    public void writeClientsAndCheckYdb(CdpChWriterTestStateHolder testData) {
        dataSteps.writeClientKeys(testData.getClientKeys());

        var newVersions = dataSteps.readClientVersionsFromYdb(testData.getClientKeys());

        var expected = new ArrayList<>(testData.getClientVersions().values());

        assertTrue("не все версии обновлены корректно",
                expected.stream().allMatch(oldVersion ->
                        newVersions.stream()
                                .filter(newVersion -> oldVersion.getKey().equals(newVersion.getKey()))
                                .allMatch(newVersion -> newVersion.getVersion() == oldVersion.getVersion())
                )
        );
    }

    @Step("Подать заказы на вход демону и проверить кликхаус")
    public void writeOrdersAndCheckClickhouse(CdpChWriterTestStateHolder testData) throws InterruptedException {
        dataSteps.writeOrderKeys(testData.getOrderKeys());

        dataSteps.waitOrdersProcessing();

        testData.incrementAllOrderVersions();
        var expected = new ArrayList<>(testData.getOrderChRows().values());

        var ordersFromCH = dataSteps.readAllOrdersFromCH();

        assertEquals("количество строк в кликхаусе не совпадает", expected.size(), ordersFromCH.size());

        assertEquals("данные в кликхаусе не соответствуют ожиданиям", new HashSet<>(expected), new HashSet<>(ordersFromCH));
    }

    @Step("Подать клиентов на вход демону и проверить кликхаус")
    public void writeClientsAndCheckClickhouse(CdpChWriterTestStateHolder testData) throws InterruptedException {
        dataSteps.writeClientKeys(testData.getClientKeys());

        dataSteps.waitClientsProcessing();

        testData.incrementAllClientVersions();
        var expected = new ArrayList<>(testData.getClientChRows().values());

        var clientsFromCH = dataSteps.readAllClientsFromCH();

        assertEquals("количество строк в кликхаусе не совпадает", expected.size(), clientsFromCH.size());

        assertEquals("данные в кликхаусе не соответствуют ожиданиям", expected, clientsFromCH);
    }

    @Step("Подать клиентов на вход демону и проверить что версии в Ydb и кликхаусе совпадают")
    public void writeClientsAndCheckVersionsInClickhouse(CdpChWriterTestStateHolder testData) throws InterruptedException {
        dataSteps.writeClientKeys(testData.getClientKeys());

        dataSteps.waitClientsProcessing();

        var expected = dataSteps.readClientVersionsFromYdb(testData.getClientKeys()).stream().collect(Collectors.toMap(ClientVersion::getKey, ClientVersion::getVersion));

        var clientsFromCH = dataSteps.readAllClientsFromCH().stream().collect(Collectors.toMap(ClientChRow::getClientKey, ClientChRow::getVersion));

        assertEquals("количество строк в кликхаусе не совпадает", expected.size(), clientsFromCH.size());

        assertEquals("версии в кликхаусе и Ydb не совпадают", expected, clientsFromCH);
    }

    @Step("Подать заказы на вход демону и проверить что версии в Ydb и кликхаусе совпадают")
    public void writeOrdersAndCheckVersionsInClickhouse(CdpChWriterTestStateHolder testData) throws InterruptedException {
        dataSteps.writeOrderKeys(testData.getOrderKeys());

        dataSteps.waitOrdersProcessing();

        var expected = dataSteps.readOrderVersionsFromYdb(testData.getOrderKeys()).stream().collect(Collectors.toMap(OrderVersion::getKey, OrderVersion::getVersion));

        var ordersFromCH = dataSteps.readAllOrdersFromCH().stream().collect(Collectors.toMap(OrderChRow::getOrderKey, OrderChRow::getOrderVersion));

        assertEquals("количество строк в кликхаусе не совпадает", expected.size(), ordersFromCH.size());

        assertEquals("версии в кликхаусе и Ydb не совпадают", expected, ordersFromCH);
    }

    @Step("Инициализация таблички с версиями клиентов")
    public List<ClientVersion> prepareClientVersionsTable(List<ClientKey> clientKeys) {
        if (clientKeys.isEmpty()) return List.of();
        return clientVersionsDao.incrementAndGetVersionsAsync(clientKeys).join();
    }

    @Step("Инициализация таблички с версиями клиентов")
    public List<OrderVersion> prepareOrderVersionsTable(List<OrderKey> orderKeys) {
        if (orderKeys.isEmpty()) return List.of();
        return orderVersionsDao.incrementAndGetVersionsAsync(orderKeys).join();
    }

    @Step("Инициализация таблички с заказами")
    public void prepareOrdersTable(List<Order> orders) {
        if (orders.isEmpty()) return;
        ordersDao.saveAsync(orders, QueryExecutionContext.write()).join();
    }

    @Step("Прочитать табличку с заказами")
    public List<Order> getOrdersTableData(List<OrderKey> orderKeys) {
        if(orderKeys.isEmpty()) return List.of();
        return ordersDao.getAsync(orderKeys, QueryExecutionContext.write()).join();
    }

    @Step("Инициализация таблички с клиентами")
    public void prepareClientsTable(List<Client> clients) {
        if (clients.isEmpty()) return;
        clientsDao.save(clients);
    }

    @Step("Прочитать табличку с клиентами")
    public List<Client> getClientsTableData(List<ClientKey> clientKeys) {
        if (clientKeys.isEmpty()) return List.of();
        return clientsDao.get(clientKeys);
    }

    @Step("Инициализация таблички с clientUserId")
    public void prepareClientUserIdTable(Map<ClientKey, TLongSet> clientUserIds) {
        if (clientUserIds.isEmpty()) return;

        clientIdMatchingDao.saveUserIdChanges(clientUserIds, Map.of(), QueryExecutionContext.write()).join();
    }

    @Step("Инициализация таблички с clientCryptaId")
    public void prepareClientCryptaIdTable(Map<ClientKey, TLongSet> cryptaIds) {
        if (cryptaIds.isEmpty()) return;
        cryptaIdMatchingDao.saveCryptaIdsAsync(cryptaIds).join();
    }

    @Step("Инициализация таблички с clientGluedYuid")
    public void prepareClientGluedYuidTable(Map<ClientKey, TLongSet> gluedYuids) {
        if (gluedYuids.isEmpty()) return;
        gluedYuidMatchingDao.saveGluedYuidsAsync(gluedYuids).join();
    }

    @Step("Инициализация таблички с orderStatuses")
    public void prepareOrderStatusesTable(Map<Integer, List<OrderStatus>> orderStatuses) {
        if (orderStatuses.isEmpty()) return;
        orderStatuses.forEach((counterId, statuses) -> schemaDao.saveOrderStatuses(counterId, statuses));
    }
}
