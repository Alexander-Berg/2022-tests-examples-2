package ru.yandex.metrika.cdp.core.tests.medium;

import java.io.IOException;
import java.time.Instant;
import java.time.LocalDate;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

import org.junit.Before;
import org.junit.BeforeClass;
import org.springframework.beans.factory.annotation.Autowired;

import ru.yandex.metrika.cdp.core.tests.medium.steps.DataSteps;
import ru.yandex.metrika.cdp.core.tests.medium.steps.TestSteps;
import ru.yandex.metrika.cdp.dto.core.Client;
import ru.yandex.metrika.cdp.dto.core.ClientType;
import ru.yandex.metrika.cdp.dto.core.ClientUpdate;
import ru.yandex.metrika.cdp.dto.core.EntityStatus;
import ru.yandex.metrika.cdp.dto.core.Order;
import ru.yandex.metrika.cdp.dto.core.OrderUpdate;
import ru.yandex.metrika.cdp.dto.core.UpdateType;
import ru.yandex.metrika.cdp.processing.dto.matching.CdpClientIdChange;
import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.dbclients.YdbSetupUtil;
import ru.yandex.metrika.util.StringUtil;

import static ru.yandex.metrika.cdp.common.FieldNames.Client.BIRTH_DATE;
import static ru.yandex.metrika.cdp.common.FieldNames.Client.CREATE_DATE_TIME;
import static ru.yandex.metrika.cdp.common.FieldNames.Client.NAME;
import static ru.yandex.metrika.cdp.common.FieldNames.Client.UPDATE_DATE_TIME;
import static ru.yandex.metrika.cdp.common.FieldNames.Order.COST;
import static ru.yandex.metrika.cdp.common.FieldNames.Order.PRODUCTS;
import static ru.yandex.metrika.cdp.common.FieldNames.Order.REVENUE;
import static ru.yandex.metrika.cdp.processing.dto.matching.CdpClientIdChange.add;
import static ru.yandex.metrika.cdp.processing.dto.matching.CdpClientIdChange.remove;

public abstract class AbstractCdpCoreTest {

    @Autowired
    protected DataSteps dataSteps;

    @Autowired
    protected TestSteps testSteps;

    protected static final Order ORDER = new Order(1, 2, 3L, "aa", Instant.now(), Instant.now(), Instant.now(), 10L, 5L, "status", Map.of("a", 1, "b", 2), Map.of("attr1", Set.of("q", "w")), EntityStatus.ACTIVE);
    protected static final Order ORDER_UPDATED = new Order(1, 2, 3L, "aa", ORDER.getCreateDateTime(), Instant.now(), Instant.now(), 10L, 5L, "status", Map.of("a", 1, "b", 2, "c", 3), Map.of("attr1", Set.of("q", "w", "e")), EntityStatus.ACTIVE);

    protected static final OrderUpdate ORDER_SAVE = new OrderUpdate(ORDER, UpdateType.SAVE, UUID.randomUUID(), Set.of(REVENUE, COST, PRODUCTS), 32123);
    protected static final OrderUpdate ORDER_UPDATE = new OrderUpdate(ORDER_UPDATED, UpdateType.UPDATE, UUID.randomUUID(), Set.of(REVENUE, COST, PRODUCTS), 32123);


    protected static final Set<String> emails = Set.of("test@example.com", "test@yandex.ru");
    public static final Set<String> emailsMd5 = emails.stream().map(StringUtil::stringMd5).collect(Collectors.toSet());
    public static final Set<String> phones = Set.of("+79001000000", "+79002000000", "+79003000000");
    public static final Set<String> phonesMd5 = phones.stream().map(StringUtil::stringMd5).collect(Collectors.toSet());

    public static final Set<String> changedPhones = Set.of("+79001000000", "+79002000000", "+79004000000");
    public static final Set<String> changedPhonesMd5 = changedPhones.stream().map(StringUtil::stringMd5).collect(Collectors.toSet());

    public static final Set<String> changedEmails = Set.of("test@example.com", "test@changed.ru");
    public static final Set<String> changedEmailsMd5 = changedEmails.stream().map(StringUtil::stringMd5).collect(Collectors.toSet());

    public static final Client CLIENT = new Client(1, 2, "externalHardId", "Bob", LocalDate.now().minusDays(10), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(10)), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(5)), Set.of(1L, 2L, 3L, -1L), Set.of("client_user_id", "test"), emails, phones, emailsMd5, phonesMd5, EntityStatus.ACTIVE, Map.of("test", Set.of("val1", "val2")), ClientType.CONTACT, null);
    public static final Client CLIENT_UPDATED = new Client(1, 2, "externalHardId", "Bob", LocalDate.now().minusDays(10), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(10)), Instant.now().minusMillis(TimeUnit.DAYS.toMillis(5)), Set.of(1L, 2L, -1L, 0L), Set.of("client_user_id", "test", "update_test"), changedEmails, changedPhones, changedEmailsMd5, changedPhonesMd5, EntityStatus.ACTIVE, Map.of("test", Set.of("val1", "val2", "val3")), ClientType.CONTACT, null);

    public static final CdpClientIdChange ADD_CDP_CLIENT_ID = add(0L, CLIENT.getCounterId(), CLIENT.getCdpUid());
    public static final CdpClientIdChange REMOVE_CDP_CLIENT_ID = remove(3L, CLIENT.getCounterId(), CLIENT.getCdpUid());

    public static final ClientUpdate CLIENT_SAVE = new ClientUpdate(CLIENT, UpdateType.SAVE, UUID.randomUUID(), Set.of(NAME, BIRTH_DATE, CREATE_DATE_TIME, UPDATE_DATE_TIME), 12321);
    public static final ClientUpdate CLIENT_UPDATE = new ClientUpdate(CLIENT_UPDATED, UpdateType.UPDATE, UUID.randomUUID(), Set.of(NAME, BIRTH_DATE, CREATE_DATE_TIME, UPDATE_DATE_TIME), 12321);


    @BeforeClass
    public static void beforeClass() throws IOException {
        CdpCoreTestSetup.setup();
    }

    @Before
    public void setUp() {
        YdbSetupUtil.truncateTablesIfExists(
                EnvironmentHelper.ydbDatabase + "/clients_data/orders",
                EnvironmentHelper.ydbDatabase + "/clients_data/clients",
                EnvironmentHelper.ydbDatabase + "/clients_data/events",
                EnvironmentHelper.ydbDatabase + "/schema/attributes"
        );
    }
}
