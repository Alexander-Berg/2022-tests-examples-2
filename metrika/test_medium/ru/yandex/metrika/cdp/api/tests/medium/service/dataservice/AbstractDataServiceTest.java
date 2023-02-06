package ru.yandex.metrika.cdp.api.tests.medium.service.dataservice;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.TimeoutException;
import java.util.function.Consumer;

import org.junit.Before;
import org.junit.ClassRule;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runners.Parameterized;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.rules.SpringClassRule;
import org.springframework.test.context.junit4.rules.SpringMethodRule;

import ru.yandex.kikimr.persqueue.consumer.SyncConsumer;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.ConsumerReadResponse;
import ru.yandex.kikimr.persqueue.consumer.transport.message.inbound.data.MessageData;
import ru.yandex.metrika.api.constructor.contr.FeatureService;
import ru.yandex.metrika.api.management.client.external.goals.CdpGoals;
import ru.yandex.metrika.api.management.tests.util.FeatureServiceMock;
import ru.yandex.metrika.apiclient.intapi.MetrikaIntapiFacade;
import ru.yandex.metrika.cdp.api.config.ValidatorConfig;
import ru.yandex.metrika.cdp.api.tests.medium.service.AbstractServiceTest;
import ru.yandex.metrika.cdp.api.tests.medium.service.CommonServiceConfig;
import ru.yandex.metrika.cdp.config.LogbrokerConfig;
import ru.yandex.metrika.cdp.dao.AttributesDao;
import ru.yandex.metrika.cdp.dao.CdpCountersDao;
import ru.yandex.metrika.cdp.dao.OrderStatusMappingChangeDao;
import ru.yandex.metrika.cdp.dao.OrdersDao;
import ru.yandex.metrika.cdp.dao.SchemaDao;
import ru.yandex.metrika.cdp.dto.CdpCounter;
import ru.yandex.metrika.cdp.dto.core.AbstractEntity;
import ru.yandex.metrika.cdp.dto.core.ClientUpdate;
import ru.yandex.metrika.cdp.dto.core.EntityUpdate;
import ru.yandex.metrika.cdp.dto.core.OrderUpdate;
import ru.yandex.metrika.cdp.dto.core.UpdateType;
import ru.yandex.metrika.cdp.dto.uploading.ApiValidationStatus;
import ru.yandex.metrika.cdp.dto.uploading.UploadingMeta;
import ru.yandex.metrika.cdp.dto.uploading.UploadingStatus;
import ru.yandex.metrika.cdp.frontend.csv.CsvService;
import ru.yandex.metrika.cdp.frontend.data.DataService;
import ru.yandex.metrika.cdp.frontend.schema.SchemaService;
import ru.yandex.metrika.cdp.proto.ClientUpdateProtoSerializer;
import ru.yandex.metrika.cdp.proto.OrderUpdateProtoSerializer;
import ru.yandex.metrika.cdp.services.ConnectorService;
import ru.yandex.metrika.cdp.services.CounterTimezoneProvider;
import ru.yandex.metrika.cdp.services.UploadingService;
import ru.yandex.metrika.cdp.ydb.AttributesDaoYdb;
import ru.yandex.metrika.cdp.ydb.OrderStatusMappingChangeDaoYdb;
import ru.yandex.metrika.cdp.ydb.OrdersDaoYdb;
import ru.yandex.metrika.config.EnvironmentHelper;
import ru.yandex.metrika.dbclients.YdbSetupUtil;
import ru.yandex.metrika.dbclients.ydb.YdbTemplate;
import ru.yandex.metrika.dbclients.ydb.async.YdbTransactionManager;
import ru.yandex.metrika.lb.serialization.proto.ProtoDtoSerializer;
import ru.yandex.metrika.lb.write.LogbrokerWriter;
import ru.yandex.metrika.util.ApiInputValidator;
import ru.yandex.metrika.util.locale.LocaleDictionaries;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.Mockito.doReturn;

@ContextConfiguration(classes = {AbstractDataServiceTest.DataConfig.class})
public abstract class AbstractDataServiceTest extends AbstractServiceTest {
    @ClassRule
    public static final SpringClassRule scr = new SpringClassRule();

    @Rule
    public final SpringMethodRule smr = new SpringMethodRule();

    @Parameterized.Parameter
    public Consumer<AbstractDataServiceTest> check;

    @Parameterized.Parameter(1)
    public String testName;

    CdpCounter counterBefore;
    CdpCounter counter;
    UploadingMeta uploadingMeta;
    boolean hasFeatureBefore;
    boolean hasFeature;

    public static final String ORDER_COLUMNS_MAPPING = "\"client_type\":\"Клиент\"," +
            "\"client_uniq_id\":\"Имя клиента\"," +
            "\"id\":\"ИД\"," +
            "\"create_date_time\":\"Создан\"," +
            "\"update_date_time\":\"Обновлен\"," +
            "\"finish_date_time\":\"Завершен\"," +
            "\"revenue\":\"Сумма\"," +
            "\"order_status\":\"Статус\"," +
            "\"products\":\"Состав\"";

    public static final String CONTACT_COLUMNS_MAPPING = "\"emails\":\"emails\"," +
            "\"uniq_id\":\"ИД\"," +
            "\"name\":\"Имя\"," +
            "\"birth_date\":\"Дата рождения\"," +
            "\"client_ids\":\"ИД клиентов\"," +
            "\"phones\":\"phones\"";


    private static final Logger log = LoggerFactory.getLogger(AbstractDataServiceTest.class);

    @Autowired
    protected DataService dataService;

    @Autowired
    @Qualifier("ordersSyncConsumer")
    protected SyncConsumer ordersSyncConsumer;

    @Autowired
    @Qualifier("contactsSyncConsumer")
    protected SyncConsumer contactsSyncConsumer;

    @Autowired
    protected CdpCountersDao cdpCountersDao;

    @Autowired
    protected MetrikaIntapiFacade metrikaIntapiFacade;

    @Autowired
    protected FeatureService featureService;

    protected final OrderUpdateProtoSerializer orderUpdateProtoSerializer = new OrderUpdateProtoSerializer();
    protected final ClientUpdateProtoSerializer clientUpdateProtoSerializer = new ClientUpdateProtoSerializer();

    @Before
    public void init() {
        //clean
        YdbSetupUtil.truncateTablesIfExists(EnvironmentHelper.ydbDatabase + "/system_data/cdp_counters");
        ((FeatureServiceMock) featureService).clear();
        cdpCountersDao.invalidateFlagCaches();

        CdpGoals goals = new CdpGoals(100, 200);
        doReturn(goals).when(metrikaIntapiFacade).getCdpGoals(anyInt());
    }

    @Test
    public void test() {
        check.accept(this);
    }

    protected <R extends ProtoDtoSerializer<T, ?>, T extends EntityUpdate<?>> List<T> readEntityFromLb(SyncConsumer consumer,
                                                                                                       R protoSerializer,
                                                                                                       UUID id,
                                                                                                       int objectCount) {
        try {
            int entitiesRead = 0;
            var result = new ArrayList<T>();
            while (entitiesRead != objectCount) {
                ConsumerReadResponse response = consumer.read();
                if (response != null) {
                    var batches = response.getBatches();
                    log.info("reading from LB. Batch size: " + batches.size());
                    for (var batch : batches) {
                        List<MessageData> messages = batch.getMessageData();
                        log.info("Messages amount in batch: " + messages.size());
                        for (var message : messages) {

                            T item = protoSerializer
                                    .deserialize(message.getDecompressedData());
                            if (item.getUploadingId().equals(id)) {
                                result.add(item);
                                entitiesRead++;
                            } else {
                                log.warn("Have read some strange entity from LB. Expected uploadingId was " + id +
                                        " but had instead " + item);
                            }
                        }
                    }
                    consumer.commit(response.getCookie());
                } else {
                    String error = "LB returns null, when object expected; already read " + entitiesRead +
                            " entities, expected total " + objectCount;
                    log.error(error);
                    throw new RuntimeException(error);
                }
            }
            return result;
        } catch (InterruptedException | TimeoutException e) {
            log.error("Exception while reading LB: " + e.getMessage(), e);
        }
        return List.of();
    }

    protected static List<Object[]> getCommonParameters() {
        return Arrays.asList(
                new Object[][]{
                        {c(test -> assertNull(test.counterBefore)), "Тест отсутствия счётчика до загрузки"},
                        {c(test -> assertFalse(test.hasFeatureBefore)), "Тест отсутствия фичи до загрузки"},
                        {c(test -> assertTrue(
                                test.uploadingMeta.getUploadingStatus().equals(UploadingStatus.COMPLETED)
                                        || test.uploadingMeta.getUploadingStatus().equals(UploadingStatus.IN_PROCESS))),
                                "Тест UploadingStatus после загрузки"},
                        {c(test -> assertEquals(ApiValidationStatus.PASSED, test.uploadingMeta.getApiValidationStatus())),
                                "Тест ApiValidationStatus после загрузки"},
                        {c(test -> assertEquals(UpdateType.APPEND, test.uploadingMeta.getUpdateType())),
                                "Тест UpdateType загруженных данных"},
                        {c(test -> assertEquals(CdpCounter.AddReason.UPLOAD, test.counter.getAddReason())),
                                "Тест причины создания счётчика"},
                        {c(test -> assertTrue(test.hasFeature)), "Тест наличия фичи после загрузки"},
                }
        );
    }

    protected static <T extends AbstractEntity<?>> void assertEqualUpdates(EntityUpdate<T> fromLb, EntityUpdate<T> fromLocal) {
        assertEquals(fromLocal, fromLb);
        assertEquals(fromLocal.getSettedOptionalFields(), fromLb.getSettedOptionalFields());
        assertEquals(fromLocal.getSeqNo(), fromLb.getSeqNo());
    }

    private static Consumer<AbstractDataServiceTest> c(Consumer<AbstractDataServiceTest> x) {
        return x;
    }

    @Configuration
    @Import({CommonServiceConfig.class,
            LogbrokerConfig.class,
            LogbrokerConfigForDataService.class,
            ValidatorConfig.class})
    static class DataConfig {

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
                MetrikaIntapiFacade metrikaIntapiFacade
        ) {
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

        @Bean
        public DataService dataService(LogbrokerWriter<ClientUpdate> clientsLogbrokerWriter,
                                       LogbrokerWriter<OrderUpdate> ordersLogbrokerWriter,
                                       CounterTimezoneProvider counterTimezoneProvider,
                                       UploadingService uploadingService,
                                       CsvService csvService,
                                       SchemaService schemaService,
                                       AttributesDaoYdb attributesDaoYdb,
                                       ApiInputValidator apiInputValidator,
                                       CdpCountersDao cdpCountersDao,
                                       FeatureService featureService) {
            return new DataService(
                    clientsLogbrokerWriter, ordersLogbrokerWriter,
                    counterTimezoneProvider,
                    uploadingService,
                    csvService,
                    schemaService,
                    attributesDaoYdb,
                    apiInputValidator,
                    cdpCountersDao,
                    featureService
            );
        }
    }
}
