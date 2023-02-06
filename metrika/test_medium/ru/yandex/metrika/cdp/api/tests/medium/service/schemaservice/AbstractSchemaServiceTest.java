package ru.yandex.metrika.cdp.api.tests.medium.service.schemaservice;

import java.util.List;
import java.util.Map;
import java.util.Set;

import org.junit.Before;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

import ru.yandex.metrika.api.constructor.contr.FeatureService;
import ru.yandex.metrika.api.management.client.external.goals.CdpGoals;
import ru.yandex.metrika.apiclient.intapi.MetrikaIntapiFacade;
import ru.yandex.metrika.cdp.api.config.ValidatorConfig;
import ru.yandex.metrika.cdp.api.tests.medium.service.AbstractServiceTest;
import ru.yandex.metrika.cdp.api.tests.medium.service.CommonServiceConfig;
import ru.yandex.metrika.cdp.dao.AttributesDao;
import ru.yandex.metrika.cdp.dao.CdpCountersDao;
import ru.yandex.metrika.cdp.dao.OrderStatusMappingChangeDao;
import ru.yandex.metrika.cdp.dao.OrdersDao;
import ru.yandex.metrika.cdp.dao.SchemaDao;
import ru.yandex.metrika.cdp.dto.schema.Attribute;
import ru.yandex.metrika.cdp.dto.schema.AttributeType;
import ru.yandex.metrika.cdp.dto.schema.CustomList;
import ru.yandex.metrika.cdp.dto.schema.ListItem;
import ru.yandex.metrika.cdp.frontend.csv.CsvService;
import ru.yandex.metrika.cdp.frontend.schema.SchemaService;
import ru.yandex.metrika.cdp.services.ConnectorService;
import ru.yandex.metrika.cdp.services.CounterTimezoneProvider;
import ru.yandex.metrika.cdp.services.UploadingService;
import ru.yandex.metrika.cdp.ydb.OrderStatusMappingChangeDaoYdb;
import ru.yandex.metrika.cdp.ydb.OrdersDaoYdb;
import ru.yandex.metrika.cdp.ydb.SchemaDaoYdb;
import ru.yandex.metrika.dbclients.YdbSetupUtil;
import ru.yandex.metrika.dbclients.ydb.YdbTemplate;
import ru.yandex.metrika.dbclients.ydb.async.YdbTransactionManager;
import ru.yandex.metrika.util.ApiInputValidator;
import ru.yandex.metrika.util.collections.F;
import ru.yandex.metrika.util.locale.LocaleDictionaries;

import static java.util.stream.Collectors.toMap;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.Mockito.doReturn;

public abstract class AbstractSchemaServiceTest extends AbstractServiceTest {

    @Autowired
    protected SchemaService schemaService;

    @Autowired
    protected SchemaDaoYdb schemaDao;

    @Autowired
    protected MetrikaIntapiFacade metrikaIntapiFacade;

    public final Attribute attr = new Attribute(getCounterId(),
            "day_the_earth_stood_still",
            AttributeType.DATE,
            false,
            "День, когда земля остановилась");
    public final Attribute attr2 = new Attribute(getCounterId(),
            "names_of_pet",
            AttributeType.TEXT,
            true,
            "Имeна домашних животных");

    @Before
    public void clean() {
        var tablePrefix = schemaDao.getTablePrefix();
        YdbSetupUtil.truncateTablesIfExists(tablePrefix + SchemaDaoYdb.LISTS_TABLE,
                tablePrefix + SchemaDaoYdb.LIST_ITEMS_TABLE,
                tablePrefix + SchemaDaoYdb.LIST_ITEMS_ATTRS_TABLE,
                tablePrefix + SchemaDaoYdb.CUSTOM_EVENTS_TABLE,
                tablePrefix + SchemaDaoYdb.ORDER_STATUSES_TABLE,
                tablePrefix + SchemaDaoYdb.CONNECTORS_TABLE,
                tablePrefix + SchemaDaoYdb.BITRIX_CONNECTORS_ATTRIBUTES_TABLE);

        CdpGoals goals = new CdpGoals(100, 200);
        doReturn(goals).when(metrikaIntapiFacade).getCdpGoals(anyInt());
    }

    static protected boolean isAttributeEqual(Attribute attr1, Attribute attr2) {
        return (attr1.getHumanized().equals(attr2.getHumanized()) &&
                attr1.getName().equals(attr2.getName()) &&
                attr1.getType().equals(attr2.getType()) &&
                attr1.getMultivalued().equals(attr2.getMultivalued()));
    }

    protected static boolean areListItemsEqual(ListItem item, ListItem anotherItem) {
        if (item == anotherItem) {
            return true;
        }
        if (!item.getName().equals(anotherItem.getName())) {
            return false;
        }
        if (!item.getHumanized().equals(anotherItem.getHumanized())) {
            return false;
        }
        if (item.getAttributeValues().size() != anotherItem.getAttributeValues().size()) {
            return false;
        }
        var attributesFromAnotherItem = anotherItem
                .getAttributeValues()
                .entrySet()
                .stream()
                .collect(toMap(x -> x.getKey().getName(), F.id()));
        for (var itemAttributeWithValue : item.getAttributeValues().entrySet()) {
            //attribute from item should be equal to the attribute with same name from anotherItem
            var correspondingEntryFromAnotherItemAttributes =
                    attributesFromAnotherItem.get(itemAttributeWithValue.getKey().getName());
            if (!isAttributeEqual(itemAttributeWithValue.getKey(),
                    correspondingEntryFromAnotherItemAttributes.getKey())) {
                return false;
            }
            if (correspondingEntryFromAnotherItemAttributes.getValue() == null) {
                return false;
            }
            if (!itemAttributeWithValue.getValue().containsAll(correspondingEntryFromAnotherItemAttributes.getValue())) {
                return false;
            }
        }
        return true;
    }

    protected CustomList getCustomList() {
        var customList = new CustomList();
        customList.setName("some_custom_list");
        customList.setHumanized("Какой-то пользовательский список");
        customList.setAttributes(List.of(attr, attr2));
        customList.setItems(getListOfItems());
        return customList;
    }

    private List<ListItem> getListOfItems() {
        var firstItem = new ListItem();
        firstItem.setHumanized("Первый элемент");
        firstItem.setName("first_item");
        firstItem.setAttributeValues(Map.of(attr, Set.of("23.12.1999"), attr2, Set.of("Васька", "Мотя", "Аська")));

        var secondItem = new ListItem();
        secondItem.setHumanized("Второй элемент");
        secondItem.setName("second_item");
        secondItem.setAttributeValues(Map.of(attr, Set.of("13.01.2012"), attr2, Set.of("Зорька", "Мурка")));
        return List.of(firstItem, secondItem);
    }

    @Configuration
    @Import({CommonServiceConfig.class, ValidatorConfig.class})
    static class SchemaConfig {

        @Bean
        public OrdersDaoYdb ordersDaoYdb(YdbTemplate ydbTemplate) {
            var ordersDaoYdb = new OrdersDaoYdb(ydbTemplate);
            ordersDaoYdb.setTablePrefix(ydbTemplate.getDatabase() + "/clients_data");
            return ordersDaoYdb;
        }

        @Bean
        public OrderStatusMappingChangeDao orderStatusMappingChangeDao(YdbTemplate ydbTemplate) {
            var orderStatusMappingChangeDaoYdb = new OrderStatusMappingChangeDaoYdb(ydbTemplate);
            orderStatusMappingChangeDaoYdb.setTablePrefix(ydbTemplate.getDatabase() + "/system_data");
            return orderStatusMappingChangeDaoYdb;
        }

        @Bean
        public ConnectorService connectorService(SchemaDao schemaDao,
                                                 OrderStatusMappingChangeDao orderStatusMappingChangeDao) {
            return new ConnectorService(
                    schemaDao,
                    orderStatusMappingChangeDao
            );
        }

        @Bean
        public SchemaService schemaService(
                SchemaDao schemaDao,
                AttributesDao attributesDao,
                UploadingService uploadingService,
                CsvService csvService,
                ConnectorService connectorService,
                OrdersDao ordersDaoYdb,
                CounterTimezoneProvider counterTimezoneProvider,
                ApiInputValidator validator,
                YdbTransactionManager transactionManager,
                OrderStatusMappingChangeDao orderStatusMappingChangeDao,
                LocaleDictionaries localeDictionaries,
                FeatureService featureService,
                CdpCountersDao cdpCountersDao,
                MetrikaIntapiFacade metrikaIntapiFacade) {
            return new SchemaService(
                    schemaDao,
                    attributesDao,
                    uploadingService,
                    csvService,
                    connectorService,
                    ordersDaoYdb,
                    counterTimezoneProvider,
                    validator,
                    transactionManager,
                    orderStatusMappingChangeDao,
                    localeDictionaries,
                    featureService,
                    cdpCountersDao,
                    metrikaIntapiFacade
            );
        }
    }
}
