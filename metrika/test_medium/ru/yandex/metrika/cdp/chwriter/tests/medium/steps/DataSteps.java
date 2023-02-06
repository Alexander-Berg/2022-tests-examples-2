package ru.yandex.metrika.cdp.chwriter.tests.medium.steps;

import java.math.BigInteger;
import java.sql.Date;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Component;

import ru.yandex.metrika.cdp.chwriter.data.ClientChRow;
import ru.yandex.metrika.cdp.chwriter.data.OrderChRow;
import ru.yandex.metrika.cdp.dto.core.ClientKey;
import ru.yandex.metrika.cdp.dto.core.ClientType;
import ru.yandex.metrika.cdp.dto.core.EntityStatus;
import ru.yandex.metrika.cdp.dto.core.OrderKey;
import ru.yandex.metrika.cdp.processing.dao.ClientVersionsDao;
import ru.yandex.metrika.cdp.processing.dao.OrderVersionsDao;
import ru.yandex.metrika.cdp.processing.dto.export.ClientVersion;
import ru.yandex.metrika.cdp.processing.dto.export.OrderVersion;
import ru.yandex.metrika.dbclients.clickhouse.CHUtils;
import ru.yandex.metrika.dbclients.clickhouse.HttpTemplate;
import ru.yandex.metrika.dbclients.ydb.async.QueryExecutionContext;
import ru.yandex.metrika.lb.waitable.WaitingLogbrokerWriter;
import ru.yandex.qatools.allure.annotations.Step;

import static java.util.Optional.ofNullable;


@Component
public class DataSteps {

    @Autowired
    private HttpTemplate httpTemplate;

    @Autowired
    private WaitingLogbrokerWriter<OrderKey> orderKeysDownstream;
    @Autowired
    private WaitingLogbrokerWriter<ClientKey> clientKeysDownstream;


    @Autowired
    private OrderVersionsDao orderVersionsDao;
    @Autowired
    private ClientVersionsDao clientVersionsDao;

    private static final RowMapper<OrderChRow> ORDERS_ROW_MAPPER = (rs, i) -> {
        var orderChRow = new OrderChRow();
        orderChRow.setOrderKey(new OrderKey(
                rs.getLong("CDPUID"),
                rs.getInt("CounterID"),
                rs.getLong("OrderID")
        ));
        orderChRow.setCreateDateTime(rs.getTimestamp("CreateTime").toInstant());
        orderChRow.setOrderVersion(rs.getInt("OrderVersion"));
        orderChRow.setStatus(EntityStatus.valueOf(rs.getString("Status")));
        orderChRow.setUpdateDateTime(rs.getTimestamp("UpdateTime").toInstant());
        orderChRow.setFinishDateTime(rs.getTimestamp("FinishTime").toInstant());
        orderChRow.setRevenue(rs.getLong("Revenue"));
        orderChRow.setCost(rs.getLong("Cost"));
        orderChRow.setOrderStatus(rs.getString("OrderStatus"));
        orderChRow.setProductIds(Arrays.stream((String[]) rs.getArray("Products.ID").getArray()).collect(Collectors.toList()));
        orderChRow.setProductQuantities(CHUtils.splitCHArray(rs.getString("Products.Quantity")).mapToInt(Integer::parseUnsignedInt).boxed().collect(Collectors.toList()));
        orderChRow.setAttributeKeys(Arrays.stream((String[]) rs.getArray("Attributes.Key").getArray()).collect(Collectors.toList()));
        orderChRow.setAttributeValues(Arrays.stream((String[]) rs.getArray("Attributes.Value").getArray()).collect(Collectors.toList()));
        orderChRow.setPartitionId(rs.getByte("PartitionID"));
        orderChRow.setExternalOrderId(rs.getString("ExternalOrderID"));
        orderChRow.setLastUploadings(Arrays.stream((String[]) rs.getArray("LastUploadings").getArray()).map(UUID::fromString).collect(Collectors.toList()));
        orderChRow.setSystemLastUpdate(ofNullable(rs.getTimestamp("SystemLastUpdate")).map(Timestamp::toInstant).orElse(Instant.ofEpochSecond(0)));

        return orderChRow;
    };

    private static final RowMapper<ClientChRow> CLIENTS_ROW_MAPPER = (rs, i) -> {
        var clientChRow = new ClientChRow();

        clientChRow.setClientKey(new ClientKey(
                rs.getLong("CDPUID"),
                rs.getInt("CounterID")
        ));
        clientChRow.setVersion(rs.getInt("ClientVersion"));
        clientChRow.setUserIds(Arrays.stream((BigInteger[]) rs.getArray("UserIDs").getArray()).mapToLong(BigInteger::longValue).toArray());
        clientChRow.setClientIds(CHUtils.splitCHArray(rs.getString("ClientIDs")).mapToLong(Long::parseUnsignedLong).toArray());
        clientChRow.setCryptaIds(CHUtils.splitCHArray(rs.getString("CryptaIDs")).mapToLong(Long::parseLong).toArray());
        clientChRow.setGluedIds(CHUtils.splitCHArray(rs.getString("GluedYuids")).mapToLong(Long::parseLong).toArray());
        clientChRow.setCreateTime(ofNullable(rs.getTimestamp("CreateTime")).map(Timestamp::toInstant).orElse(null));
        clientChRow.setUpdateTime(ofNullable(rs.getTimestamp("UpdateTime")).map(Timestamp::toInstant).orElse(null));
        clientChRow.setExternalHardId(rs.getString("ExternalHardID"));
        clientChRow.setClientType(ClientType.valueOf(rs.getString("ClientType")));
        clientChRow.setStatus(EntityStatus.valueOf(rs.getString("Status")));
        clientChRow.setParentCdpUid(ofNullable(rs.getString("ParentCDPUID")).map(Long::parseUnsignedLong).orElse(0L));
        clientChRow.setName(rs.getString("Name"));
        clientChRow.setBirthDate(ofNullable(rs.getDate("BirthDate")).map(Date::toLocalDate).orElse(null));
        clientChRow.setEmails(Arrays.stream((String[]) rs.getArray("Emails").getArray()).collect(Collectors.toList()));
        clientChRow.setPhones(Arrays.stream((String[]) rs.getArray("Phones").getArray()).collect(Collectors.toList()));
        clientChRow.setAttributeKeys(Arrays.stream((String[]) rs.getArray("Attributes.Key").getArray()).collect(Collectors.toList()));
        clientChRow.setAttributeValues(Arrays.stream((String[]) rs.getArray("Attributes.Value").getArray()).collect(Collectors.toList()));
        clientChRow.setClientUserIds(Arrays.stream((String[]) rs.getArray("ClientUserIDs").getArray()).collect(Collectors.toList()));
        clientChRow.setSumRevenue(rs.getLong("OrdersSum"));
        clientChRow.setLtv(rs.getLong("LTV"));
        clientChRow.setFirstOrderCreateTime(rs.getTimestamp("FirstOrderCreateTime").toInstant());
        clientChRow.setLastOrderCreateTime(rs.getTimestamp("LastOrderCreateTime").toInstant());
        clientChRow.setFirstOrderFinishTime(ofNullable(rs.getTimestamp("FirstOrderFinishTime")).map(Timestamp::toInstant).orElse(Instant.ofEpochSecond(0)));
        clientChRow.setLastOrderFinishTime(ofNullable(rs.getTimestamp("LastOrderFinishTime")).map(Timestamp::toInstant).orElse(Instant.ofEpochSecond(0)));
        clientChRow.setCompletedOrders(rs.getInt("CompletedOrders"));
        clientChRow.setCreatedOrders(rs.getInt("CreatedOrders"));
        clientChRow.setPaidOrders(rs.getInt("PaidOrders"));
        clientChRow.setPartitionId(rs.getByte("PartitionID"));
        clientChRow.setEmailsMd5(Arrays.stream((String[]) rs.getArray("EmailsMd5").getArray()).collect(Collectors.toList()));
        clientChRow.setPhonesMd5(Arrays.stream((String[]) rs.getArray("PhonesMd5").getArray()).collect(Collectors.toList()));
        clientChRow.setLastUploadings(Arrays.stream((String[]) rs.getArray("LastUploadings").getArray()).map(UUID::fromString).collect(Collectors.toList()));
        clientChRow.setSystemLastUpdate(ofNullable(rs.getTimestamp("SystemLastUpdate")).map(Timestamp::toInstant).orElse(Instant.ofEpochSecond(0)));

        return clientChRow;
    };


    @Step("Запись тестовых заказов во входные топики")
    public void writeOrderKeys(List<OrderKey> orderKeys) {
        orderKeysDownstream.writeBatchAsync(orderKeys).join();
    }

    @Step("Запись тестовых клиентов во входные топики")
    public void writeClientKeys(List<ClientKey> clientKeys) {
        clientKeysDownstream.writeBatchAsync(clientKeys).join();
    }

    @Step("Подождать пока заказы обработаются демоном")
    public void waitOrdersProcessing() throws InterruptedException {
        orderKeysDownstream.waitProcessing();
    }

    @Step("Подождать пока клиенты обработаются демоном")
    public void waitClientsProcessing() throws InterruptedException {
        clientKeysDownstream.waitProcessing();
    }

    @Step("Прочитать версии заказов из YDB")
    public List<OrderVersion> readOrderVersionsFromYdb(List<OrderKey> orderKeys) {
        return orderVersionsDao.getVersionsAsync(orderKeys, QueryExecutionContext.read()).join();
    }

    @Step("Прочитать версии клиентов из YDB")
    public List<ClientVersion> readClientVersionsFromYdb(List<ClientKey> clientKeys) {
        return clientVersionsDao.getVersionsAsync(clientKeys).join();
    }

    @Step("Прочитать все заказы из ClickHouse")
    public List<OrderChRow> readAllOrdersFromCH() {
        String query = "select * from orders_d final;";

        return httpTemplate.query(query, ORDERS_ROW_MAPPER);
    }

    @Step("Прочитать всех клиентов из ClickHouse")
    public List<ClientChRow> readAllClientsFromCH() {
        String query = "select * from clients_d final;";

        return httpTemplate.query(query, CLIENTS_ROW_MAPPER);
    }

    @Step("Очистка таблицы с клиентами в кликхаусе")
    public void truncateClientsCHTable() {
        httpTemplate.update("TRUNCATE TABLE clients_d;");
    }

    @Step("Очистка таблицы с заказами в кликхаусе")
    public void truncateOrdersCHTable() {
        httpTemplate.update("TRUNCATE TABLE orders_d;");
    }

}
