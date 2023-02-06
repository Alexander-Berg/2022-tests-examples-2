package ru.yandex.metrika.cdp.chwriter.tests.medium;

import java.io.IOException;
import java.time.Instant;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.function.Function;
import java.util.stream.Collectors;

import gnu.trove.set.hash.TLongHashSet;
import org.junit.Before;
import org.junit.BeforeClass;
import org.springframework.beans.factory.annotation.Autowired;

import ru.yandex.metrika.cdp.chwriter.tests.medium.steps.DataSteps;
import ru.yandex.metrika.cdp.chwriter.tests.medium.steps.TestSteps;
import ru.yandex.metrika.cdp.dto.core.Client;
import ru.yandex.metrika.cdp.dto.core.ClientKey;
import ru.yandex.metrika.cdp.dto.core.ClientType;
import ru.yandex.metrika.cdp.dto.core.EntityStatus;
import ru.yandex.metrika.cdp.dto.core.Order;
import ru.yandex.metrika.cdp.dto.schema.OrderStatus;
import ru.yandex.metrika.cdp.dto.schema.OrderStatusType;
import ru.yandex.metrika.cdp.processing.dto.export.ClientVersion;
import ru.yandex.metrika.cdp.processing.dto.export.OrderVersion;
import ru.yandex.metrika.cdp.ydb.OrdersDaoYdb;
import ru.yandex.metrika.cdp.ydb.SchemaDaoYdb;
import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.dbclients.YdbSetupUtil;
import ru.yandex.metrika.util.StringUtil;

public abstract class AbstractCdpChWriterTest {

    @Autowired
    protected SchemaDaoYdb schemaDaoYdb;

    @Autowired
    protected OrdersDaoYdb ordersDaoYdb;

    @Autowired
    protected TestSteps testSteps;

    @Autowired
    protected DataSteps dataSteps;

    protected static final Set<String> emails = Set.of("test@example.com", "test@yandex.ru");
    protected static final Set<String> emailsMd5 = emails.stream()
            .map(StringUtil::stringMd5)
            .collect(Collectors.toSet());
    protected static final Set<String> phones = Set.of("+79001000000", "+79002000000", "+79003000000");
    protected static final Set<String> phonesMd5 = phones.stream()
            .map(StringUtil::stringMd5)
            .collect(Collectors.toSet());


    protected static final int COUNTER_ID_1 = 42;
    protected static final int COUNTER_ID_2 = 47;

    protected static final int CDP_UID_1 = 1;
    protected static final int CDP_UID_2 = 2;

    protected static final ClientKey CLIENT_KEY_1 = new ClientKey(CDP_UID_1, COUNTER_ID_1);
    protected static final ClientKey CLIENT_KEY_2 = new ClientKey(CDP_UID_2, COUNTER_ID_2);

    protected static final String ORDER_STATUS_ID_1 = "order_status_1";
    protected static final String ORDER_STATUS_ID_2 = "order_status_2";
    protected static final String ORDER_STATUS_ID_3 = "order_status_3";
    protected static final String ORDER_STATUS_ID_4 = "order_status_4";

    protected static final String PAID_ORDER_STATUS_ID_1 = "paid_order_status_1";
    protected static final String PAID_ORDER_STATUS_ID_2 = "paid_order_status_2";

    protected static final String CANCELLED_ORDER_STATUS_ID = "order_status_3";

    protected static final String SPAM_ORDER_STATUS_ID_1 = "spam_order_status_1";
    protected static final String SPAM_ORDER_STATUS_ID_2 = "spam_order_status_2";
    protected static final String SPAM_ORDER_STATUS_ID_3 = "spam_order_status_3";

    protected static final OrderStatus PAID_ORDER_STATUS_1 = new OrderStatus(PAID_ORDER_STATUS_ID_1, "Статус заказа аналогичный 'Оплачен'", OrderStatusType.PAID);
    protected static final OrderStatus PAID_ORDER_STATUS_2 = new OrderStatus(PAID_ORDER_STATUS_ID_2, "Статус заказа аналогичный 'Оплачен'", OrderStatusType.PAID);

    protected static final OrderStatus ORDER_STATUS_1 = new OrderStatus(ORDER_STATUS_ID_1, "Статус заказа аналогичный 'В работе'", OrderStatusType.IN_PROGRESS);
    protected static final OrderStatus ORDER_STATUS_2 = new OrderStatus(ORDER_STATUS_ID_2, "Статус заказа аналогичный 'В работе'", OrderStatusType.IN_PROGRESS);
    protected static final OrderStatus ORDER_STATUS_3 = new OrderStatus(ORDER_STATUS_ID_3, "Статус заказа аналогичный 'В работе'", OrderStatusType.IN_PROGRESS);
    protected static final OrderStatus ORDER_STATUS_4 = new OrderStatus(ORDER_STATUS_ID_4, "Статус заказа аналогичный 'Оплачен'", OrderStatusType.PAID);

    protected static final OrderStatus CANCELLED_ORDER_STATUS = new OrderStatus(CANCELLED_ORDER_STATUS_ID, "Статус заказа аналогичный 'Отменен'", OrderStatusType.CANCELLED);

    protected static final OrderStatus SPAM_ORDER_STATUS_1 = new OrderStatus(SPAM_ORDER_STATUS_ID_1, "Статус заказа аналогичный 'Спам'", OrderStatusType.SPAM);
    protected static final OrderStatus SPAM_ORDER_STATUS_2 = new OrderStatus(SPAM_ORDER_STATUS_ID_2, "Статус заказа аналогичный 'Спам'", OrderStatusType.SPAM);
    protected static final OrderStatus SPAM_ORDER_STATUS_3 = new OrderStatus(SPAM_ORDER_STATUS_ID_3, "Статус заказа аналогичный 'Спам'", OrderStatusType.SPAM);

    protected static final Order ORDER_1 = new Order(CDP_UID_1, COUNTER_ID_1, 1, "a", Instant.now().minusMillis(TimeUnit.DAYS.toMillis(20)), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(10)), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(5)), 100L, 10L, ORDER_STATUS_ID_1, Map.of("ipa", 10, "brew dog", 20), Map.of("test", Set.of("val1", "val2")), EntityStatus.ACTIVE, List.of(UUID.randomUUID()), Instant.now());
    protected static final Order ORDER_2 = new Order(CDP_UID_1, COUNTER_ID_1, 2, "b", Instant.now().minusMillis(TimeUnit.DAYS.toMillis(20)), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(10)), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(5)), 100L, 10L, ORDER_STATUS_ID_2, Map.of("ipa", 10, "brew dog", 20), Map.of("test", Set.of("val1", "val2")), EntityStatus.ACTIVE, List.of(UUID.randomUUID()), Instant.now());
    protected static final Order ORDER_3 = new Order(CDP_UID_2, COUNTER_ID_2, 3, "l", Instant.now().minusMillis(TimeUnit.DAYS.toMillis(20)), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(10)), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(5)), 100L, 15L, ORDER_STATUS_ID_3, Map.of("ipa", 10, "brew dog", 20), Map.of("test", Set.of("val1", "val2")), EntityStatus.ACTIVE, List.of(UUID.randomUUID()), Instant.now());
    protected static final Order ORDER_4 = new Order(CDP_UID_2, COUNTER_ID_2, 4, "m", Instant.now().minusMillis(TimeUnit.DAYS.toMillis(20)), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(10)), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(5)), 130L, 10L, ORDER_STATUS_ID_4, Map.of("ipa", 10, "brew dog", 20), Map.of("test", Set.of("val1", "val2")), EntityStatus.ACTIVE, List.of(UUID.randomUUID()), Instant.now());

    protected static final Order CANCELLED_ORDER = new Order(CDP_UID_1, COUNTER_ID_1, 5, "c", Instant.now().minusMillis(TimeUnit.DAYS.toMillis(20)), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(10)), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(5)), 300L, 10L, CANCELLED_ORDER_STATUS_ID, Map.of("porter", 10), Map.of("test", Set.of("val5", "val6")), EntityStatus.ACTIVE, List.of(UUID.randomUUID()), Instant.now());

    protected static final Order SPAM_ORDER_1 = new Order(CDP_UID_1, COUNTER_ID_1, 6, "d", Instant.now().minusMillis(TimeUnit.DAYS.toMillis(20)), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(10)), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(5)), 400L, 10L, SPAM_ORDER_STATUS_ID_1, Map.of("oyster", 30), Map.of("test", Set.of("val7", "val8")), EntityStatus.ACTIVE, List.of(UUID.randomUUID()), Instant.now());
    protected static final Order SPAM_ORDER_2 = new Order(CDP_UID_1, COUNTER_ID_1, 7, "e", Instant.now().minusMillis(TimeUnit.DAYS.toMillis(20)), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(10)), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(5)), 400L, 10L, SPAM_ORDER_STATUS_ID_2, Map.of("oyster", 30), Map.of("test", Set.of("val7", "val8")), EntityStatus.ACTIVE, List.of(UUID.randomUUID()), Instant.now());
    protected static final Order SPAM_ORDER_3 = new Order(CDP_UID_1, COUNTER_ID_1, 8, "f", Instant.now().minusMillis(TimeUnit.DAYS.toMillis(20)), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(10)), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(5)), 400L, 10L, SPAM_ORDER_STATUS_ID_3, Map.of("oyster", 30), Map.of("test", Set.of("val7", "val8")), EntityStatus.ACTIVE, List.of(UUID.randomUUID()), Instant.now());

    protected static final Order PAID_ORDER_1 = new Order(CDP_UID_1, COUNTER_ID_1, 9, "g", Instant.now().minusMillis(TimeUnit.DAYS.toMillis(20)), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(10)), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(5)), 200L, 10L, PAID_ORDER_STATUS_ID_1, Map.of("stout", 5), Map.of("test", Set.of("val3", "val4")), EntityStatus.ACTIVE, List.of(UUID.randomUUID()), Instant.now());
    protected static final Order PAID_ORDER_2 = new Order(CDP_UID_1, COUNTER_ID_1, 10, "h", Instant.now().minusMillis(TimeUnit.DAYS.toMillis(20)), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(10)), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(5)), 200L, 10L, PAID_ORDER_STATUS_ID_2, Map.of("stout", 5), Map.of("test", Set.of("val3", "val4")), EntityStatus.ACTIVE, List.of(UUID.randomUUID()), Instant.now());

    protected static final Order PAID_ORDER_WITH_NULL_FINISH_DATE_1 = new Order(CDP_UID_1, COUNTER_ID_1, 11, "i", Instant.now().minusMillis(TimeUnit.DAYS.toMillis(20)), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(10)), null, 200L, 10L, PAID_ORDER_STATUS_ID_1, Map.of("stout", 5), Map.of("test", Set.of("val3", "val4")), EntityStatus.ACTIVE, List.of(UUID.randomUUID()), Instant.now());
    protected static final Order PAID_ORDER_WITH_NULL_FINISH_DATE_2 = new Order(CDP_UID_1, COUNTER_ID_1, 12, "g", Instant.now().minusMillis(TimeUnit.DAYS.toMillis(20)), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(10)), null, 400L, 10L, PAID_ORDER_STATUS_ID_2, Map.of("stout", 5), Map.of("test", Set.of("val3", "val4")), EntityStatus.ACTIVE, List.of(UUID.randomUUID()), Instant.now());

    protected static final Order PAID_ORDER_WITH_NULL_FINISH_AND_UPDATE_DATE_1 = new Order(CDP_UID_1, COUNTER_ID_1, 13, "k", Instant.now().minusMillis(TimeUnit.DAYS.toMillis(20)), null, null, 200L, 10L, PAID_ORDER_STATUS_ID_1, Map.of("stout", 5), Map.of("test", Set.of("val3", "val4")), EntityStatus.ACTIVE, List.of(UUID.randomUUID()), Instant.now());

    protected static final Client CLIENT_1 = new Client(CDP_UID_1, COUNTER_ID_1, "externalHardId", "Bob", LocalDate.now().minusDays(10), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(10)), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(5)), Set.of(1L, 2L, 3L, -1L), Set.of("client_user_id", "test"), emails, phones, emailsMd5, phonesMd5, EntityStatus.ACTIVE, Map.of("test", Set.of("val1", "val2")), ClientType.CONTACT, null, List.of(UUID.randomUUID()), Instant.now());

    protected static final Client CLIENT_2 = new Client(CDP_UID_2, COUNTER_ID_2, "someExternalHardId", "Alice", LocalDate.now().minusDays(20), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(15)), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(10)), Set.of(2L, 3L, 4L, -5L), Set.of("another_client_user_id", "test_test"), emails, phones, emailsMd5, phonesMd5, EntityStatus.ACTIVE, Map.of("test_test", Set.of("val5", "val6")), ClientType.CONTACT, null, List.of(UUID.randomUUID()), Instant.now());

    @BeforeClass
    public static void beforeClass() throws IOException {
        CdpChWriterTestSetup.setup();
    }

    @Before
    public void setUp() {
        dataSteps.truncateClientsCHTable();
        dataSteps.truncateOrdersCHTable();

        YdbSetupUtil.truncateTablesIfExists(
                EnvironmentHelper.ydbDatabase + "/clients_data/orders",
                EnvironmentHelper.ydbDatabase + "/clients_data/clients",
                EnvironmentHelper.ydbDatabase + "/schema/order_statuses",
                EnvironmentHelper.ydbDatabase + "/ch_writer_meta/client_versions",
                EnvironmentHelper.ydbDatabase + "/ch_writer_meta/order_versions",
                EnvironmentHelper.ydbDatabase + "/matching/client_crypta_id",
                EnvironmentHelper.ydbDatabase + "/matching/client_user_id",
                EnvironmentHelper.ydbDatabase + "/matching/client_glued_yuid",
                EnvironmentHelper.ydbDatabase + "/matching/client_client_id",
                EnvironmentHelper.ydbDatabase + "/matching/client_id_client",
                EnvironmentHelper.ydbDatabase + "/matching/client_id_user_id"
        );
    }

    protected CdpChWriterTestStateHolder prepareSingleClient() {
        var testData = new CdpChWriterTestStateHolder();
        testData.setClients(List.of(CLIENT_1));
        testData.setOrders(List.of(ORDER_1));
        testData.setOrderStatuses(Map.of(COUNTER_ID_1, List.of(ORDER_STATUS_1)));
        testData.setUserIds(Map.of(CLIENT_KEY_1, new TLongHashSet(List.of(222L))));
        testData.setCryptaIds(Map.of(CLIENT_KEY_1, new TLongHashSet(List.of(424L))));
        testData.setGluedIds(Map.of(CLIENT_KEY_1, new TLongHashSet(List.of(242L))));

        prepareTestData(testData);

        return testData;
    }

    protected CdpChWriterTestStateHolder updateSingleClient(CdpChWriterTestStateHolder testData) {
        testData.updateOrders(List.of(ORDER_2));
        testData.updateOrderStatuses(Map.of(COUNTER_ID_1, List.of(ORDER_STATUS_2)));
        testData.updateUserIds(Map.of(CLIENT_KEY_1, new TLongHashSet(List.of(322L))));
        testData.updateCryptaIds(Map.of(CLIENT_KEY_1, new TLongHashSet(List.of(666L))));
        testData.updateGluedIds(Map.of(CLIENT_KEY_1, new TLongHashSet(List.of(777L))));

        prepareTestData(testData);

        return testData;
    }

    protected CdpChWriterTestStateHolder prepareTwoClients() {
        var testData = new CdpChWriterTestStateHolder();

        testData.setClients(List.of(CLIENT_1, CLIENT_2));
        testData.setOrders(List.of(ORDER_1, ORDER_3));
        testData.setOrderStatuses(Map.of(COUNTER_ID_1, List.of(ORDER_STATUS_1), COUNTER_ID_2, List.of(ORDER_STATUS_3)));
        testData.setUserIds(Map.of(CLIENT_KEY_1, new TLongHashSet(List.of(222L)), CLIENT_KEY_2, new TLongHashSet(List.of(444L))));
        testData.setCryptaIds(Map.of(CLIENT_KEY_1, new TLongHashSet(List.of(424L)), CLIENT_KEY_2, new TLongHashSet(List.of(888L))));
        testData.setGluedIds(Map.of(CLIENT_KEY_1, new TLongHashSet(List.of(242L)), CLIENT_KEY_2, new TLongHashSet(List.of(121L))));

        prepareTestData(testData);

        return testData;
    }

    protected void prepareTestData(CdpChWriterTestStateHolder testData) {
        testSteps.prepareOrdersTable(testData.getOrders());
        testSteps.prepareClientsTable(testData.getClients());

        // прочитаем записанные данные, чтобы иметь актуальный systemLastUpdate
        testData.setOrders(testSteps.getOrdersTableData(testData.getOrderKeys()));
        testData.setClients(testSteps.getClientsTableData(testData.getClientKeys()));

        var orderVersions = testSteps.prepareOrderVersionsTable(testData.getOrderKeys());
        var clientVersions = testSteps.prepareClientVersionsTable(testData.getClientKeys());
        testSteps.prepareOrderStatusesTable(testData.getOrderStatuses());
        testSteps.prepareClientCryptaIdTable(testData.getCryptaIds());
        testSteps.prepareClientGluedYuidTable(testData.getGluedIds());
        testSteps.prepareClientUserIdTable(testData.getUserIds());
        testData.setOrderVersions(orderVersions.stream().collect(Collectors.toMap(OrderVersion::getKey, Function.identity())));
        testData.setClientVersions(clientVersions.stream().collect(Collectors.toMap(ClientVersion::getKey, Function.identity())));
    }

}
