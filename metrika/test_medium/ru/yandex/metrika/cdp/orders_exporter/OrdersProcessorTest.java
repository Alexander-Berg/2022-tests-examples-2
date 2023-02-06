package ru.yandex.metrika.cdp.orders_exporter;

import java.time.Duration;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.stream.Collectors;

import javax.annotation.Nullable;
import javax.annotation.ParametersAreNonnullByDefault;

import com.google.protobuf.Timestamp;
import com.yandex.ydb.table.query.Params;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringRunner;

import ru.yandex.kikimr.persqueue.LogbrokerClientAsyncFactory;
import ru.yandex.kikimr.persqueue.consumer.SyncConsumer;
import ru.yandex.kikimr.persqueue.consumer.sync.SyncConsumerConfig;
import ru.yandex.metrika.cdp.config.LogbrokerConfig;
import ru.yandex.metrika.cdp.dao.CdpCountersDao;
import ru.yandex.metrika.cdp.dao.OrdersDao;
import ru.yandex.metrika.cdp.dao.SchemaDao;
import ru.yandex.metrika.cdp.dto.CdpCounter;
import ru.yandex.metrika.cdp.dto.core.ClientType;
import ru.yandex.metrika.cdp.dto.core.EntityStatus;
import ru.yandex.metrika.cdp.dto.core.Order;
import ru.yandex.metrika.cdp.dto.core.OrderKey;
import ru.yandex.metrika.cdp.dto.schema.OrderStatus;
import ru.yandex.metrika.cdp.dto.schema.OrderStatusType;
import ru.yandex.metrika.cdp.orders_exporter.processing.UpdatedOrdersProcessor;
import ru.yandex.metrika.cdp.orders_exporter.proto.Export;
import ru.yandex.metrika.cdp.processing.dao.ClientIdMatchingDao;
import ru.yandex.metrika.cdp.processing.dao.CryptaIdMatchingDao;
import ru.yandex.metrika.cdp.processing.dao.GluedYuidMatchingDao;
import ru.yandex.metrika.cdp.processing.dao.OrderStateDao;
import ru.yandex.metrika.cdp.processing.dto.export.OrderState;
import ru.yandex.metrika.cdp.processing.ydb.ClientIdMatchingDaoYdb;
import ru.yandex.metrika.cdp.processing.ydb.CryptaIdMatchingDaoYdb;
import ru.yandex.metrika.cdp.processing.ydb.GluedYuidMatchingDaoYdb;
import ru.yandex.metrika.cdp.processing.ydb.OrderStateDaoYdb;
import ru.yandex.metrika.cdp.proto.ProtoSerializerUtil;
import ru.yandex.metrika.cdp.ydb.CdpCountersDaoYdb;
import ru.yandex.metrika.cdp.ydb.OrdersDaoYdb;
import ru.yandex.metrika.cdp.ydb.SchemaDaoYdb;
import ru.yandex.metrika.dbclients.YdbSetupUtil;
import ru.yandex.metrika.dbclients.config.YdbConfig;
import ru.yandex.metrika.dbclients.ydb.YdbTemplate;
import ru.yandex.metrika.dbclients.ydb.async.QueryExecutionContext;
import ru.yandex.metrika.dbclients.ydb.async.YdbTransactionManager;
import ru.yandex.metrika.lb.serialization.Serializer;
import ru.yandex.metrika.lb.serialization.proto.GenericProtoSerializer;
import ru.yandex.metrika.lb.serialization.proto.ProtoSerializer;
import ru.yandex.metrika.lb.write.LogbrokerWriter;
import ru.yandex.metrika.lb.write.LogbrokerWriterConfig;
import ru.yandex.metrika.lb.write.LogbrokerWriterFactory;
import ru.yandex.metrika.lb.write.ReinitializingLogbrokerWriter;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotEquals;
import static org.junit.Assert.assertNotNull;
import static ru.yandex.metrika.cdp.common.CdpIdUtil.buildCdpUid;
import static ru.yandex.metrika.cdp.common.CdpIdUtil.buildOrderId;
import static ru.yandex.metrika.cdp.common.FieldNames.OrderState.CDP_UID;
import static ru.yandex.metrika.cdp.common.FieldNames.OrderState.COUNTER_ID;
import static ru.yandex.metrika.cdp.common.FieldNames.OrderState.IN_PROGRESS_FIRST_TIME;
import static ru.yandex.metrika.cdp.common.FieldNames.OrderState.ORDER_ID;
import static ru.yandex.metrika.cdp.common.FieldNames.OrderState.PAID_FIRST_TIME;
import static ru.yandex.metrika.cdp.common.FieldNames.OrderState.VERSION;

@RunWith(SpringRunner.class)
@ContextConfiguration
@ParametersAreNonnullByDefault
public class OrdersProcessorTest {
    private static final int counterId = 42;

    @Autowired
    YdbTemplate ydbTemplate;

    @Autowired
    UpdatedOrdersProcessor updatedOrdersProcessor;

    @Autowired
    SchemaDaoYdb schemaDao;

    @Autowired
    OrderStateDaoYdb orderStateDaoYdb;

    @Autowired
    ClientIdMatchingDaoYdb clientIdMatchingDaoYdb;

    @Autowired
    OrdersDaoYdb ordersDaoYdb;

    @Autowired
    CdpCountersDaoYdb cdpCountersDaoYdb;

    @Autowired
    SyncConsumer syncConsumer;

    @BeforeClass
    public static void beforeClass() {
        YdbSetupUtil.setupYdbFolders("matching", "orders_export_meta", "system_data", "clients_data", "schema");
    }

    @Before
    public void init() {
        cleanYdb();
        createCounter();
        createOrderStatuses();
    }


    //Заказ со statusType IN_PROGRESS, которого нет в стейте (а после теста должен появиться)
    @Test
    public void testInProgressNew() {
        var inProgress = getOrder("1", "in_progress");
        testNew(inProgress);
    }


    //Заказ со statusType IN_PROGRESS, который есть в стейте с проставленным in_progress_first_time
    // (после теста не должно обновиться время в стейте)
    @Test
    public void testInProgressWithPreloadedState() {
        var inProgress = getOrder("1", "in_progress");

        var inProgressFirstTime = Instant.now().minus(1, ChronoUnit.DAYS);
        var oldState = new OrderState(inProgress.getKey(),
                1,
                inProgressFirstTime,
                null);
        testEqualityWithPreloadedState(inProgress, oldState, true);
    }


    //Заказ со statusType PAID, которого нет в стейте (а после теста должен появиться)
    @Test
    public void testPaidNew() {
        var paid = getOrder("2", "paid");
        testNew(paid);
    }


    //Заказ со statusType PAID, который есть в стейте c пустым paid_first_time (после теста должно заполниться paid_first_time)
    @Test
    public void testPaidEmptyPaidFirstTime() {
        var paid = getOrder("1", "paid");

        var oldState = new OrderState(paid.getKey(),
                1,
                Instant.now().minus(2, ChronoUnit.DAYS),
                null);

        testEqualityWithPreloadedState(paid, oldState, false);
    }


    //Заказ со statusType PAID, который есть в стейте c не пустым paid_first_time (после теста не должно обновиться время в стейте)
    @Test
    public void testPaidNotEmptyPaidFirstTime() {
        var paid = getOrder("1", "paid");

        var oldState = new OrderState(paid.getKey(),
                1,
                Instant.now().minus(2, ChronoUnit.DAYS),
                Instant.now().minus(1, ChronoUnit.DAYS));

        testEqualityWithPreloadedState(paid, oldState, true);

    }


    //Заказ без statusType но с FinishDateTime, которого нет в стейте (а после теста должен появиться)
    @Test
    public void testStatuslessWithFinishDate() {
        var statusless = getOrder("2", "some_unmapped_status");
        testNew(statusless);
    }


    //Заказ без statusType но с FinishDateTime, который есть в стейте c пустым paid_first_time
    //(после теста должно заполниться paid_first_time)
    @Test
    public void testStatuslessWithFinishDateEmptyPaidFirstTime() {
        var statusless = getOrder("1", "some_unmapped_status");

        var oldState = new OrderState(statusless.getKey(),
                1,
                Instant.now().minus(2, ChronoUnit.DAYS),
                null);

        testEqualityWithPreloadedState(statusless, oldState, false);
    }


    //Заказ без statusType но с FinishDateTime, который есть в стейте c не пустым paid_first_time
    //(после теста не должно обновиться время в стейте)
    @Test
    public void testStatuslessWithFinishDateFilledPaidFirstTime() {
        var statusless = getOrder("1", "some_unmapped_status");

        var oldState = new OrderState(statusless.getKey(),
                1,
                Instant.now().minus(2, ChronoUnit.DAYS),
                Instant.now().minus(1, ChronoUnit.DAYS));

        testEqualityWithPreloadedState(statusless, oldState, true);
    }

    //Заказ без statusType и без FinishDateTime (не должны экспортировать)
    @Test
    public void testStatuslessWithEmptyFinishDate() {
        cleanLb();
        var statusless = getOrder("2", "some_unmapped_status");
        statusless.setFinishDateTime(null);

        ordersDaoYdb.saveAsync(List.of(statusless), QueryExecutionContext.write()).join();
        //проверяем, что заказа нет в state
        var states = getOrderStateDataUntouched(ydbTemplate, orderStateDaoYdb.getTablePrefix(),
                statusless.getCounterId(), statusless.getOrderId(), statusless.getCdpUid());
        assertEquals(0, states.size());
        //обрабатываем
        updatedOrdersProcessor.process(List.of(statusless.getKey())).join();
        //проверяем, что заказа всё ещё нет в state
        states = getOrderStateDataUntouched(ydbTemplate, orderStateDaoYdb.getTablePrefix(),
                statusless.getCounterId(), statusless.getOrderId(), statusless.getCdpUid());
        assertEquals(0, states.size());

        //проверяем, что заказа нет в LB:
        var ordersFromLb = getOrdersFromLb(1);
        assertEquals(0, ordersFromLb.size());
    }

    //создаём заказы 6 типов:
    // -in_progress
    // -paid
    // -cancelled
    // -spam
    // -без статуса и с FinishDate
    // -без статуса и без FinishDate
    // предзагружаем в стейт, проверяем, что после обработки заказ без статуса и без FinishDate не экспортируется
    @Test
    public void testMultiProcessingForAllTypes() {
        cleanLb();
        uploadDataToYdb();

        var orders = getOrders();
        var keys = getOrders().stream()
                .map(Order::getKey)
                .collect(Collectors.toList());

        updatedOrdersProcessor.process(keys).join();

        int expectedAmount = 5;
        var ordersFromLB = getOrdersFromLb(expectedAmount);

        assertEquals("Wrong number of Order Ids found in LB",
                expectedAmount, ordersFromLB.size());

        var ordersIdsFromLb = ordersFromLB.stream().map(Export.OrderExport::getOrderId).collect(Collectors.toSet());
        var ordersIds = orders.stream().map(Order::getOrderId).collect(Collectors.toSet());
        ordersIds.removeAll(ordersIdsFromLb);
        assertEquals("Order IDs read from LB are different from the written ones",
                1, ordersIds.size());

        var remaining = ordersIds.stream().findFirst().orElse(0L);
        assertEquals("Order IDs read from LB are different from the written ones",
                (Long) buildOrderId("5"), remaining);
    }

    public void testNew(Order order) {
        ordersDaoYdb.saveAsync(List.of(order), QueryExecutionContext.write()).join();
        //проверяем, что заказа нет в state
        var states = getOrderStateDataUntouched(ydbTemplate, orderStateDaoYdb.getTablePrefix(),
                order.getCounterId(), order.getOrderId(), order.getCdpUid());
        assertEquals(0, states.size());
        //обрабатываем
        updatedOrdersProcessor.process(List.of(order.getKey())).join();
        //проверяем, что заказ есть в state
        states = getOrderStateDataUntouched(ydbTemplate, orderStateDaoYdb.getTablePrefix(),
                order.getCounterId(), order.getOrderId(), order.getCdpUid());
        assertEquals(1, states.size());
        checkOrderFromLb(states.get(0).getOrderId(),
                states.get(0).getCdpUid(),
                order.getCreateDateTime(),
                order.getUpdateDateTime(),
                order.getFinishDateTime());
    }

    public void testEqualityWithPreloadedState(Order order, OrderState stateToPreload, boolean samePaidFirstTime) {
        ordersDaoYdb.saveAsync(List.of(order), QueryExecutionContext.write()).join();
        //проверяем, что заказа нет в state
        var states = getOrderStateDataUntouched(ydbTemplate, orderStateDaoYdb.getTablePrefix(),
                order.getCounterId(), order.getOrderId(), order.getCdpUid());
        assertEquals(0, states.size());

        //загружаем stateToPreload, проверяем корректность загруженного
        orderStateDaoYdb.saveNewStatesAsync(List.of(stateToPreload), QueryExecutionContext.write()).join();
        states = getOrderStateDataUntouched(ydbTemplate, orderStateDaoYdb.getTablePrefix(),
                order.getCounterId(), order.getOrderId(), order.getCdpUid());
        assertEquals(1, states.size());
        assertEquals(stateToPreload.getInProgressFirstTime() != null ? stateToPreload.getInProgressFirstTime().truncatedTo(ChronoUnit.MILLIS) : null, states.get(0).getInProgressFirstTime() != null ? states.get(0).getInProgressFirstTime().truncatedTo(ChronoUnit.MILLIS) : null);
        assertEquals(stateToPreload.getPaidFirstTime() != null ? stateToPreload.getPaidFirstTime().truncatedTo(ChronoUnit.MILLIS) : null, states.get(0).getPaidFirstTime() != null ? states.get(0).getPaidFirstTime().truncatedTo(ChronoUnit.MILLIS) : null);
        //обрабатываем
        updatedOrdersProcessor.process(List.of(order.getKey())).join();
        //проверяем эквивалентность состояния
        states = getOrderStateDataUntouched(ydbTemplate, orderStateDaoYdb.getTablePrefix(),
                order.getCounterId(), order.getOrderId(), order.getCdpUid());
        assertEquals(1, states.size());
        assertEquals(stateToPreload.getInProgressFirstTime() != null ? stateToPreload.getInProgressFirstTime().truncatedTo(ChronoUnit.MILLIS) : null, states.get(0).getInProgressFirstTime() != null ? states.get(0).getInProgressFirstTime().truncatedTo(ChronoUnit.MILLIS) : null);
        if (samePaidFirstTime) {
            assertEquals(stateToPreload.getPaidFirstTime() != null ? stateToPreload.getPaidFirstTime().truncatedTo(ChronoUnit.MILLIS) : null, states.get(0).getPaidFirstTime() != null ? states.get(0).getPaidFirstTime().truncatedTo(ChronoUnit.MILLIS) : null);
        } else {
            assertNotEquals(stateToPreload.getPaidFirstTime() != null ? stateToPreload.getPaidFirstTime().truncatedTo(ChronoUnit.MILLIS) : null, states.get(0).getPaidFirstTime() != null ? states.get(0).getPaidFirstTime().truncatedTo(ChronoUnit.MILLIS) : null);
        }
        checkOrderFromLb(states.get(0).getOrderId(),
                states.get(0).getCdpUid(),
                order.getCreateDateTime(),
                order.getUpdateDateTime(),
                order.getFinishDateTime());
    }

    private void uploadDataToYdb() {
        var orders = getOrders();
        ordersDaoYdb.saveAsync(orders, QueryExecutionContext.write()).join();

        var orderStates = orders.stream()
                .map(x -> new OrderState(new OrderKey(x.getCdpUid(), x.getCounterId(), x.getOrderId()),
                        2,
                        x.getUpdateDateTime() != null ? x.getUpdateDateTime() : null,
                        x.getFinishDateTime() != null ? x.getFinishDateTime() : null))
                .collect(Collectors.toList());
        orderStateDaoYdb.saveNewStatesAsync(orderStates, QueryExecutionContext.write()).join();
    }

    private void createOrderStatuses() {
        schemaDao.saveOrderStatuses(counterId, getOrdersTypeMapping());
    }

    private void createCounter() {
        cdpCountersDaoYdb.addCounters(List.of(
                new CdpCounter(counterId, CdpCounter.AddReason.FEATURE)
        ));
    }

    private void checkOrderFromLb(long expectedOrderId,
                                  long expectedCdpUid,
                                  @Nullable Instant expectedCreateDateTime,
                                  @Nullable Instant expectedUpdateDateTime,
                                  @Nullable Instant expectedFinishDateTime) {
        var orderFromLb = getOrderFromLb(expectedCdpUid, expectedOrderId);
        assertNotNull(orderFromLb);
        assertEquals(counterId, orderFromLb.getCounterId());
        assertEquals(expectedOrderId, orderFromLb.getOrderId());
        assertEquals(expectedCdpUid, orderFromLb.getCdpUid());
        assertEquals(expectedCreateDateTime, fromTimestamp(orderFromLb.getCreateDateTime()));
        assertEquals(expectedUpdateDateTime, fromTimestamp(orderFromLb.getUpdateDateTime()));
        assertEquals(expectedFinishDateTime, fromTimestamp(orderFromLb.getFinishDateTime()));
    }

    @Nullable
    private Instant fromTimestamp(@Nullable Timestamp timestamp) {
        if (timestamp == null) {
            return null;
        }
        return ProtoSerializerUtil.toInstant(timestamp);
    }

    @Nullable
    private Export.OrderExport getOrderFromLb(long cdpUid, long orderId) {
        var serializer = new GenericProtoSerializer<>(Export.OrderExport.parser());
        try {
            var response = syncConsumer.read();
            while (response != null) {
                for (var batch : response.getBatches()) {
                    for (var message : batch.getMessageData()) {
                        var x = serializer.deserialize(message.getDecompressedData());
                        if (cdpUid == x.getCdpUid() && orderId == x.getOrderId()) {
                            syncConsumer.commit(response.getCookie());
                            return x;
                        }
                    }
                }
                syncConsumer.commit(response.getCookie());
                response = syncConsumer.read();
            }
        } catch (InterruptedException | TimeoutException e) {
            e.printStackTrace();
        }
        return null;
    }

    private List<Export.OrderExport> getOrdersFromLb(int amount) {
        var entities = new ArrayList<Export.OrderExport>();
        int i = 0;
        var serializer = new GenericProtoSerializer<>(Export.OrderExport.parser());
        try {
            while (i < amount) {
                var response = syncConsumer.read();
                if (response != null) {
                    for (var batch : response.getBatches()) {
                        for (var message : batch.getMessageData()) {
                            var x = serializer.deserialize(message.getDecompressedData());
                            entities.add(x);
                            i++;
                        }
                    }
                    syncConsumer.commit(response.getCookie());
                } else {
                    break;
                }
            }
        } catch (InterruptedException | TimeoutException e) {
            e.printStackTrace();
        }
        return entities;
    }

    private void cleanLb() {
        try {
            var response = syncConsumer.read();
            while (response != null) {
                syncConsumer.commit(response.getCookie());
                response = syncConsumer.read();
            }
        } catch (InterruptedException | TimeoutException e) {
            e.printStackTrace();
        }
    }

    private static List<OrderStatus> getOrdersTypeMapping() {
        return List.of(
                new OrderStatus("in_progress", "in_progress", OrderStatusType.IN_PROGRESS),
                new OrderStatus("paid", "paid", OrderStatusType.PAID),
                new OrderStatus("spam", "spam", OrderStatusType.SPAM),
                new OrderStatus("cancelled", "cancelled", OrderStatusType.CANCELLED)
        );
    }

    private static List<OrderState> getOrderStateDataUntouched(YdbTemplate ydbTemplate, String tablePrefix, int counterId, long orderId, long cdpUid) {
        String sql = String.format(
                "PRAGMA TablePathPrefix = \"%s\";\n" +
                        "SELECT \n" +
                        COUNTER_ID + " AS " + COUNTER_ID + ",\n" +
                        CDP_UID + " AS " + CDP_UID + ",\n" +
                        ORDER_ID + " AS " + ORDER_ID + ",\n" +
                        "CAST(IF(order_versions." + VERSION + " IS NULL, 1, order_versions." + VERSION + " + 1) AS UInt32) AS " + VERSION + ",\n" +
                        IN_PROGRESS_FIRST_TIME + " AS " + IN_PROGRESS_FIRST_TIME + ",\n" +
                        PAID_FIRST_TIME + " AS " + PAID_FIRST_TIME + "\n" +
                        "FROM order_versions\n" +
                        "WHERE " + CDP_UID + " = " + cdpUid + "\n" +
                        "AND " + COUNTER_ID + " = " + counterId + "\n" +
                        "AND " + ORDER_ID + " = " + orderId + "\n", tablePrefix);
        return ydbTemplate.query(sql,
                Params.empty(),
                OrderStateDaoYdb.ROW_MAPPER
        );
    }

    private static List<Order> getOrders() {
        var in_progress = getOrder("1", "in_progress");
        in_progress.setFinishDateTime(null);

        var paid = getOrder("2", "paid");
        var cancelled = getOrder("3", "cancelled");
        var spam = getOrder("4", "spam");

        var without_status_unfinished = getOrder("5", "some_unmapped_status");
        without_status_unfinished.setFinishDateTime(null);

        var without_status_finished = getOrder("6", "some_unmapped_status");
        return List.of(
                in_progress,
                paid,
                cancelled,
                spam,
                without_status_unfinished,
                without_status_finished
        );
    }

    private static Order getOrder(String orderId, String status) {
        return new Order(
                buildCdpUid("123", ClientType.CONTACT),
                counterId,
                buildOrderId(orderId),
                orderId,
                Instant.parse("2011-12-03T10:15:30Z"),
                Instant.parse("2013-06-03T10:15:30Z"),
                Instant.parse("2013-06-03T10:15:30Z"),
                0L,
                0L,
                status,
                Map.of(),
                Map.of(),
                EntityStatus.ACTIVE
        );
    }

    private void cleanYdb() {
        var tablePrefix = schemaDao.getTablePrefix();
        YdbSetupUtil.truncateTablesIfExists(tablePrefix + '/' + SchemaDaoYdb.LISTS_TABLE,
                tablePrefix + '/' + SchemaDaoYdb.LIST_ITEMS_TABLE,
                tablePrefix + '/' + SchemaDaoYdb.LIST_ITEMS_ATTRS_TABLE,
                tablePrefix + '/' + SchemaDaoYdb.CUSTOM_EVENTS_TABLE,
                tablePrefix + '/' + SchemaDaoYdb.ORDER_STATUSES_TABLE
        );

        tablePrefix = cdpCountersDaoYdb.getTablePrefix();
        YdbSetupUtil.truncateTablesIfExists(tablePrefix + '/' + CdpCountersDaoYdb.CDP_COUNTERS_TABLE);

        tablePrefix = orderStateDaoYdb.getTablePrefix();
        YdbSetupUtil.truncateTablesIfExists(tablePrefix + "/order_versions");

        tablePrefix = clientIdMatchingDaoYdb.getTablePrefix();
        YdbSetupUtil.truncateTablesIfExists(
                //ClientIdMatchingDao
                tablePrefix + "/client_client_id",
                tablePrefix + "/client_id_client",
                tablePrefix + "/client_id_user_id",
                tablePrefix + "/client_user_id",
                tablePrefix + "/client_id_client",

                //GluedYuidMatchingDao
                tablePrefix + "/client_glued_yuid",

                //CryptaIdMatchingDao
                tablePrefix + "/client_crypta_id"
        );

        tablePrefix = ordersDaoYdb.getTablePrefix();
        YdbSetupUtil.truncateTablesIfExists(
                tablePrefix + "/orders"
        );
    }

    @Configuration
    @Import({YdbConfig.class, LogbrokerConfig.class})
    static class Config {

        @Bean
        public SchemaDaoYdb schemaDao(YdbTemplate ydbTemplate) {
            return new SchemaDaoYdb(ydbTemplate, ydbTemplate.getDatabase() + "/schema");
        }

        @Bean
        public CdpCountersDaoYdb cdpCountersDao(YdbTemplate ydbTemplate) {
            var cdpCountersDaoYdb = new CdpCountersDaoYdb(ydbTemplate);
            cdpCountersDaoYdb.setTablePrefix(ydbTemplate.getDatabase() + "/system_data");
            return cdpCountersDaoYdb;
        }

        @Bean
        public OrderStateDaoYdb orderStateDao(YdbTemplate ydbTemplate) {
            var orderStateDaoYdb = new OrderStateDaoYdb(ydbTemplate);
            orderStateDaoYdb.setTablePrefix(ydbTemplate.getDatabase() + "/orders_export_meta");
            return orderStateDaoYdb;
        }

        @Bean
        public ClientIdMatchingDaoYdb clientIdMatchingDao(YdbTemplate ydbTemplate) {
            var clientIdMatchingDaoYdb = new ClientIdMatchingDaoYdb(ydbTemplate);
            clientIdMatchingDaoYdb.setTablePrefix(ydbTemplate.getDatabase() + "/matching");
            return clientIdMatchingDaoYdb;
        }

        @Bean
        public GluedYuidMatchingDaoYdb gluedYuidMatchingDao(YdbTemplate ydbTemplate, YdbTransactionManager transactionManager) {
            var gluedYuidMatchingDao = new GluedYuidMatchingDaoYdb(ydbTemplate, transactionManager);
            gluedYuidMatchingDao.setTablePrefix(ydbTemplate.getDatabase() + "/matching");
            return gluedYuidMatchingDao;
        }

        @Bean
        public CryptaIdMatchingDaoYdb cryptaIdMatchingDao(YdbTemplate ydbTemplate, YdbTransactionManager transactionManager) {
            var cryptaIdMatchingDao = new CryptaIdMatchingDaoYdb(ydbTemplate, transactionManager);
            cryptaIdMatchingDao.setTablePrefix(ydbTemplate.getDatabase() + "/matching");
            return cryptaIdMatchingDao;
        }

        @Bean
        public OrdersDaoYdb ordersDao(YdbTemplate ydbTemplate) {
            var ordersDaoYdb = new OrdersDaoYdb(ydbTemplate);
            ordersDaoYdb.setTablePrefix(ydbTemplate.getDatabase() + "/clients_data");
            return ordersDaoYdb;
        }

        @Bean
        public ProtoSerializer<Export.OrderExport> orderExportProtoSerializer() {
            return new GenericProtoSerializer<>(Export.OrderExport.parser());
        }

        @Bean
        public ReinitializingLogbrokerWriter<Export.OrderExport> ordersExportDownstream(
                LogbrokerWriterFactory factory,
                Serializer<Export.OrderExport> serializer,
                LogbrokerWriterConfig ordersExportDownstreamConfig) {
            return factory.reinitializingLogbrokerWriter(
                    ordersExportDownstreamConfig,
                    serializer
            );
        }

        @Bean(name = "ordersExportDownstreamConfig")
        public LogbrokerWriterConfig ordersExportDownstreamConfig() {
            var config = new LogbrokerWriterConfig();
            config.setTopic("/metrika/cdp/orders-export-topic");
            config.setSourceIdPrefix("cdp-orders-exporter-writer-source");
            return config;
        }

        @Bean
        public SyncConsumerConfig logbrokerSyncConsumerConfig(LogbrokerWriterConfig ordersExportDownstreamConfig) {
            return SyncConsumerConfig
                    .builder(List.of(ordersExportDownstreamConfig.getTopic()),
                            ordersExportDownstreamConfig.getSourceIdPrefix())
                    .setReadDataTimeout(3, TimeUnit.SECONDS)
                    .configureReader(x -> x.setMaxCount(0))
                    .build();
        }

        @Bean
        public SyncConsumer ordersSyncConsumer(LogbrokerClientAsyncFactory logbrokerClientAsyncFactory,
                                               SyncConsumerConfig ordersSyncConsumerConfig)
                throws ExecutionException, InterruptedException, TimeoutException {
            var syncConsumer = logbrokerClientAsyncFactory.syncConsumer(ordersSyncConsumerConfig).get();
            syncConsumer.init();
            return syncConsumer;
        }

        @Bean
        public Duration clientOrdersToExportDuration() {
            return Duration.ofDays(2);
        }

        @Bean
        public UpdatedOrdersProcessor updatedOrdersProcessor(
                SchemaDao schemaDao,
                OrderStateDao orderStateDao,
                ClientIdMatchingDao clientIdMatchingDao,
                GluedYuidMatchingDao gluedYuidMatchingDao,
                CryptaIdMatchingDao cryptaIdMatchingDao,
                CdpCountersDao cdpCountersDao,
                YdbTransactionManager ydbTransactionManager,
                LogbrokerWriter<Export.OrderExport> downstream,
                OrdersDao ordersDao
        ) {
            return new UpdatedOrdersProcessor(schemaDao, orderStateDao, clientIdMatchingDao,
                    gluedYuidMatchingDao, cryptaIdMatchingDao, cdpCountersDao, ydbTransactionManager,
                    true, downstream, ordersDao);
        }
    }
}
