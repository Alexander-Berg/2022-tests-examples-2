package ru.yandex.metrika.cdp.tests.medium.ydb;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.TimeUnit;

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

import ru.yandex.metrika.cdp.dto.core.EntityStatus;
import ru.yandex.metrika.cdp.dto.core.Order;
import ru.yandex.metrika.cdp.ydb.OrdersDaoYdb;
import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.dbclients.YdbSetupUtil;
import ru.yandex.metrika.dbclients.config.YdbConfig;
import ru.yandex.metrika.dbclients.ydb.YdbTemplate;
import ru.yandex.metrika.dbclients.ydb.async.QueryExecutionContext;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

@RunWith(SpringRunner.class)
@ContextConfiguration
public class OrdersDaoYdbTest {

    private static final String CLIENTS_DATA_FOLDER = "clients_data";
    private static final String ORDERS_TABLE_PREFIX = EnvironmentHelper.ydbDatabase + "/" + CLIENTS_DATA_FOLDER;
    private static final String ORDERS_TABLE_PATH = ORDERS_TABLE_PREFIX + "/" + "orders";

    @BeforeClass
    public static void beforeClass() {
        YdbSetupUtil.setupYdbFolders(CLIENTS_DATA_FOLDER);
    }

    @Autowired
    private OrdersDaoYdb ordersDaoYdb;

    @Before
    public void setUp() {
        YdbSetupUtil.truncateTablesIfExists(ORDERS_TABLE_PATH);
    }

    @Test
    public void saveAndGetTest() {
        var order = new Order(
                1,
                2,
                3L,
                "3",
                Instant.now().minusMillis(TimeUnit.DAYS.toMillis(20)),
                Instant.now().minusMillis(TimeUnit.DAYS.toMillis(10)),
                Instant.now().minusMillis(TimeUnit.DAYS.toMillis(5)),
                100L,
                10L,
                "done",
                Map.of("iphone", 10, "ipad", 20),
                Map.of("test", Set.of("val1", "val2")),
                EntityStatus.ACTIVE
        );


        ordersDaoYdb.saveAsync(List.of(order), QueryExecutionContext.write()).join();

        var orderFromDbO = ordersDaoYdb.getAsync(List.of(order.getKey()), QueryExecutionContext.read()).join().stream().findFirst();
        assertTrue(orderFromDbO.isPresent());
        assertEquals(order, orderFromDbO.get());
    }

    @Configuration
    @Import(YdbConfig.class)
    static class Config {

        @Bean
        public OrdersDaoYdb ordersDaoYdb(YdbTemplate ydbTemplate) {
            return new OrdersDaoYdb(ydbTemplate, ORDERS_TABLE_PREFIX);
        }

    }

}
