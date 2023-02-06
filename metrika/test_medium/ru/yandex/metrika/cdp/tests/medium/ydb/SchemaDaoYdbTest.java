package ru.yandex.metrika.cdp.tests.medium.ydb;

import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

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

import ru.yandex.metrika.cdp.dto.schema.Attribute;
import ru.yandex.metrika.cdp.dto.schema.AttributeType;
import ru.yandex.metrika.cdp.dto.schema.CustomList;
import ru.yandex.metrika.cdp.dto.schema.ListItem;
import ru.yandex.metrika.cdp.dto.schema.ListType;
import ru.yandex.metrika.cdp.dto.schema.OrderStatus;
import ru.yandex.metrika.cdp.dto.schema.OrderStatusType;
import ru.yandex.metrika.cdp.dto.schema.internal.ListItemAttributeInternal;
import ru.yandex.metrika.cdp.dto.schema.internal.ListItemInternal;
import ru.yandex.metrika.cdp.dto.schema.internal.ListItemKeyInternal;
import ru.yandex.metrika.cdp.dto.schema.internal.ListKeyInternal;
import ru.yandex.metrika.cdp.dto.schema.internal.OrdersStatusInternal;
import ru.yandex.metrika.cdp.ydb.SchemaDaoYdb;
import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.dbclients.YdbSetupUtil;
import ru.yandex.metrika.dbclients.config.YdbConfig;
import ru.yandex.metrika.dbclients.ydb.YdbTemplate;
import ru.yandex.metrika.dbclients.ydb.async.QueryExecutionContext;
import ru.yandex.metrika.util.collections.Collectors2;
import ru.yandex.metrika.util.collections.F;

import static java.util.stream.Collectors.groupingBy;
import static org.junit.Assert.assertEquals;

@RunWith(SpringRunner.class)
@ContextConfiguration
public class SchemaDaoYdbTest {

    private static final String SCHEMA_FOLDER = "system_data";
    private static final String SCHEMA_TABLE_PREFIX = EnvironmentHelper.ydbDatabase + "/" + SCHEMA_FOLDER;
    private static final String LISTS_TABLE_PATH = SCHEMA_TABLE_PREFIX + "/" + SchemaDaoYdb.LISTS_TABLE;
    private static final String LIST_ITEMS_TABLE_PATH = SCHEMA_TABLE_PREFIX + "/" + SchemaDaoYdb.LIST_ITEMS_TABLE;
    private static final String LIST_ITEMS_ATTRS_TABLE_PATH = SCHEMA_TABLE_PREFIX + "/" + SchemaDaoYdb.LIST_ITEMS_ATTRS_TABLE;
    private static final String CUSTOM_EVENTS_TABLE_PATH = SCHEMA_TABLE_PREFIX + "/" + SchemaDaoYdb.CUSTOM_EVENTS_TABLE;
    private static final String ORDER_STATUSES_TABLE_PATH = SCHEMA_TABLE_PREFIX + "/" + SchemaDaoYdb.ORDER_STATUSES_TABLE;
    private static final String CONNECTORS_TABLE_PATH = SCHEMA_TABLE_PREFIX + "/" + SchemaDaoYdb.CONNECTORS_TABLE;
    private static final String BITRIX_CONNECTORS_ATTRIBUTES_TABLE_PATH = SCHEMA_TABLE_PREFIX + "/" + SchemaDaoYdb.BITRIX_CONNECTORS_ATTRIBUTES_TABLE;

    @Autowired
    private SchemaDaoYdb schemaDaoYdb;

    @BeforeClass
    public static void beforeClass() {
        YdbSetupUtil.setupYdbFolders(SCHEMA_FOLDER);
    }

    @Before
    public void setUp() {
        YdbSetupUtil.truncateTablesIfExists(
                LISTS_TABLE_PATH,
                LIST_ITEMS_TABLE_PATH,
                LIST_ITEMS_ATTRS_TABLE_PATH,
                CUSTOM_EVENTS_TABLE_PATH,
                ORDER_STATUSES_TABLE_PATH,
                CONNECTORS_TABLE_PATH,
                BITRIX_CONNECTORS_ATTRIBUTES_TABLE_PATH
        );
    }

    @Test
    public void testSaveList() {
        var attribute1 = new Attribute(42, "attr1", AttributeType.TEXT, false, "Атрибут 1");
        var attribute2 = new Attribute(42, "attr2", AttributeType.TEXT, true, "Атрибут 2");

        var customList = new CustomList(
                "list",
                "Лист",
                List.of(attribute1, attribute2),
                List.of(
                        new ListItem("item1", "Первый", Map.of(attribute1, Set.of("value1_1"), attribute2, Set.of("value1_2_1", "value2_2_1"))),
                        new ListItem("item2", "Первый", Map.of(attribute1, Set.of("value1_2"), attribute2, Set.of("value1_2_2", "value2_2_2")))
                )
        );

        schemaDaoYdb.saveList(42, customList);

        var allItemsList = schemaDaoYdb.getListItems(42, ListType.CUSTOM, "list", QueryExecutionContext.read());
        var allItemsAttrsList = schemaDaoYdb.getListAttrs(42, ListType.CUSTOM, "list", QueryExecutionContext.read());

        var items = customList.getItems();
        Objects.requireNonNull(items);
        var listKeyInternal = new ListKeyInternal(42, ListType.CUSTOM, customList.getName());
        var listItemKeyInternal1 = new ListItemKeyInternal(listKeyInternal, items.get(0).getName());
        var listItemKeyInternal2 = new ListItemKeyInternal(listKeyInternal, items.get(1).getName());

        var listItemInternal1 = new ListItemInternal(listItemKeyInternal1, items.get(0).getHumanized());
        var listItemInternal2 = new ListItemInternal(listItemKeyInternal2, items.get(1).getHumanized());

        assertEquals(
                List.of(listItemInternal1, listItemInternal2),
                allItemsList
        );

        assertEquals(
                List.of(
                        new ListItemAttributeInternal(listItemKeyInternal1, attribute1.getName(), "value1_1"),
                        new ListItemAttributeInternal(listItemKeyInternal1, attribute2.getName(), "value1_2_1"),
                        new ListItemAttributeInternal(listItemKeyInternal1, attribute2.getName(), "value2_2_1"),
                        new ListItemAttributeInternal(listItemKeyInternal2, attribute1.getName(), "value1_2"),
                        new ListItemAttributeInternal(listItemKeyInternal2, attribute2.getName(), "value1_2_2"),
                        new ListItemAttributeInternal(listItemKeyInternal2, attribute2.getName(), "value2_2_2")
                ),
                allItemsAttrsList
        );
    }

    @Test
    public void testSaveAndGetAllOrdersStatuses() {
        var statusesMap = Map.of(
                42,
                List.of(
                        new OrderStatus("1", "one", OrderStatusType.IN_PROGRESS),
                        new OrderStatus("2", null, OrderStatusType.PAID)
                ),
                100500,
                List.of(
                        new OrderStatus("3", "three", OrderStatusType.CANCELLED),
                        new OrderStatus("4", "", OrderStatusType.SPAM)
                )
        );
        statusesMap.forEach(schemaDaoYdb::saveOrderStatuses);

        var fromDB = F.stream(schemaDaoYdb.getAllOrderStatusesMapping())
                .collect(groupingBy(OrdersStatusInternal::getCounterId, Collectors2.toListMapping(OrdersStatusInternal::asOrderStatus)));

        assertEquals(statusesMap, fromDB);
    }

    @Configuration
    @Import(YdbConfig.class)
    static class Config {

        @Bean
        public SchemaDaoYdb schemaDaoYdb(YdbTemplate ydbTemplate) {
            return new SchemaDaoYdb(ydbTemplate, SCHEMA_TABLE_PREFIX);
        }

    }
}
