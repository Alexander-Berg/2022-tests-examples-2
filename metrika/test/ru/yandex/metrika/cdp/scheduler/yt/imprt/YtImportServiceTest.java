package ru.yandex.metrika.cdp.scheduler.yt.imprt;

import java.time.ZoneOffset;
import java.util.List;
import java.util.Map;
import java.util.function.Function;

import javax.annotation.Nonnull;

import org.apache.logging.log4j.Level;
import org.jetbrains.annotations.NotNull;
import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.inside.yt.kosher.CloseableYt;
import ru.yandex.inside.yt.kosher.Yt;
import ru.yandex.inside.yt.kosher.impl.YtConfiguration;
import ru.yandex.metrika.api.constructor.contr.FeatureService;
import ru.yandex.metrika.api.constructor.contr.FeatureServiceImpl;
import ru.yandex.metrika.cdp.dao.AttributesDao;
import ru.yandex.metrika.cdp.dto.core.ClientUpdate;
import ru.yandex.metrika.cdp.dto.core.OrderUpdate;
import ru.yandex.metrika.cdp.proto.ClientUpdateProtoSerializer;
import ru.yandex.metrika.cdp.proto.OrderUpdateProtoSerializer;
import ru.yandex.metrika.cdp.services.UploadingService;
import ru.yandex.metrika.cdp.validation.ValidationHelper;
import ru.yandex.metrika.cdp.ydb.AttributesDaoYdb;
import ru.yandex.metrika.cdp.ydb.SchemaDaoYdb;
import ru.yandex.metrika.cdp.ydb.UploadingsDaoYdb;
import ru.yandex.metrika.dbclients.mysql.DbUtils;
import ru.yandex.metrika.dbclients.mysql.MySqlJdbcTemplate;
import ru.yandex.metrika.dbclients.redis.RedisConnector;
import ru.yandex.metrika.dbclients.redis.RedisSourceList;
import ru.yandex.metrika.dbclients.ydb.YdbClientProperties;
import ru.yandex.metrika.dbclients.ydb.YdbTemplate;
import ru.yandex.metrika.dbclients.ydb.async.YdbSessionManager;
import ru.yandex.metrika.lb.write.LogbrokerShardingWriterConfig;
import ru.yandex.metrika.lb.write.LogbrokerWriterFactory;
import ru.yandex.metrika.lb.write.ShardingLogbrokerWriter;
import ru.yandex.metrika.lb.write.UnsignedLongShardSelector;
import ru.yandex.metrika.util.locale.LocaleDictionaries;
import ru.yandex.metrika.util.log.Log4jSetup;

import static ru.yandex.metrika.util.app.XmlPropertyConfigurer.getTextFromFile;

/**
 * {@link YtImportService}.
 */
public class YtImportServiceTest {

    private static final String ytProxyAddress = "hahn.yt.yandex.net";
    private static final String ytTablePath = "//home/metrika/cdp/experiments/import_clients_example";
    private static final String clientsLbTopic = "/metrika/test/experiments/cdp/cdp-clients-topic";
    private static final String ordersLbTopic = "/metrika/test/experiments/cdp/cdp-orders-topic";
    private static final String lbSourceIdPrefix = "cdp-yt-importer-writer";
    private static final String lbBalancerHost = "lbkx.logbroker.yandex.net";
    private static final String ydbHost = "ydb-ru-prestable.yandex.net:2135";
    private static final String ydbDatabase = "/ru-prestable/metrika/testing/cdp";
    private static final int lbPartitionsCount = 2;

    @SuppressWarnings("SameParameterValue")
    private <T> T useImportService(@NotNull Function<YtImportService, T> importServiceConsumer) throws Exception {
        Log4jSetup.basicArcadiaSetup(Level.INFO);

        ShardingLogbrokerWriter<ClientUpdate> clientsLogbrokerWriter = getClientsLogbrokerWriter();
        ShardingLogbrokerWriter<OrderUpdate> ordersLogbrokerWriter = getOrdersLogbrokerWriter();
        CloseableYt yt = getYt();
        YdbSessionManager ydbSessionManager = getYdbSessionManager();
        UploadingService uploadingService = getUploadingService(ydbSessionManager);
        var attributesDao = getAttributesDao(ydbSessionManager);
        var attributesValidationHelper = getAttributesValidationHelper(ydbSessionManager);

        FeatureService featureService = getFeatureService();
        YtImportService importService = new YtImportService(
                yt,
                clientsLogbrokerWriter,
                ordersLogbrokerWriter,
                uploadingService,
                attributesDao,
                attributesValidationHelper,
                featureService);

        var res = importServiceConsumer.apply(importService);

        yt.close();
        clientsLogbrokerWriter.close();
        ydbSessionManager.close();

        return res;
    }

    private MySqlJdbcTemplate getCountersTemplate() {
        return DbUtils.makeJdbcTemplateForTests("haproxy-test.metrika.yandex.net", 4056, "metrika",
                getTextFromFile("~/.mysql/pass_old"), "conv_main");
    }

    private ValidationHelper getAttributesValidationHelper(YdbSessionManager ydbSessionManager) throws Exception {
        var ydbTemplate = new YdbTemplate(ydbSessionManager);
        var schemaDaoYdb = new SchemaDaoYdb(ydbTemplate);
        schemaDaoYdb.setTablePrefix(ydbDatabase + "/schema");
        LocaleDictionaries localeDictionaries = new LocaleDictionaries();
        localeDictionaries.afterPropertiesSet();
        return new ValidationHelper(schemaDaoYdb, counterId -> ZoneOffset.UTC, localeDictionaries);
    }

    private AttributesDao getAttributesDao(YdbSessionManager ydbSessionManager) {
        var ydbTemplate = new YdbTemplate(ydbSessionManager);
        var attributesDaoYdb = new AttributesDaoYdb(ydbTemplate);
        attributesDaoYdb.setTablePrefix(ydbDatabase + "/schema");
        attributesDaoYdb.afterPropertiesSet();
        return attributesDaoYdb;
    }

    private UploadingService getUploadingService(YdbSessionManager ydbSessionManager) {
        var ydbTemplate = new YdbTemplate(ydbSessionManager);
        var uploadingsDaoYdb = new UploadingsDaoYdb(ydbTemplate);
        uploadingsDaoYdb.setTablePrefix(ydbDatabase + "/system_data");
        uploadingsDaoYdb.afterPropertiesSet();

        return new UploadingService(uploadingsDaoYdb);
    }

    private FeatureService getFeatureService() {
        RedisSourceList sources = new RedisSourceList();
        RedisConnector connector = new RedisConnector(sources);

        return new FeatureServiceImpl(connector, getCountersTemplate(), "counter_features", "counter_id");
    }

    @Nonnull
    private YdbSessionManager getYdbSessionManager() {
        var properties = new YdbClientProperties();
        properties.setDatabase(ydbDatabase);
        properties.setEndpoint(ydbHost);
        properties.setCallThreadCount(1);
        properties.setYdbToken(getTextFromFile("~/.ydb/token"));

        return new YdbSessionManager(properties);
    }

    private CloseableYt getYt() {
        return Yt.builder(
                YtConfiguration.builder()
                        .withApiHost(ytProxyAddress)
                        .withToken(getTextFromFile("~/.yt/token"))
                        .build()
        ).http().build();
    }

    private ShardingLogbrokerWriter<ClientUpdate> getClientsLogbrokerWriter() {
        LogbrokerShardingWriterConfig lbWriterConfig = new LogbrokerShardingWriterConfig();
        lbWriterConfig.setTopic(clientsLbTopic);
        lbWriterConfig.setTokenValue(getTextFromFile("~/.logbroker/token"));
        lbWriterConfig.setSourceIdPrefix(lbSourceIdPrefix);
        lbWriterConfig.setPartitionsCount(lbPartitionsCount);
        return new LogbrokerWriterFactory(lbBalancerHost).shardingLogbrokerWriter(
                lbWriterConfig,
                new ClientUpdateProtoSerializer(),
                new UnsignedLongShardSelector<>(lbWriterConfig, cu -> cu.getClient().getCdpUid())
        );
    }

    private ShardingLogbrokerWriter<OrderUpdate> getOrdersLogbrokerWriter() {
        LogbrokerShardingWriterConfig lbWriterConfig = new LogbrokerShardingWriterConfig();
        lbWriterConfig.setTopic(ordersLbTopic);
        lbWriterConfig.setTokenValue(getTextFromFile("~/.logbroker/token"));
        lbWriterConfig.setSourceIdPrefix(lbSourceIdPrefix);
        lbWriterConfig.setPartitionsCount(lbPartitionsCount);
        return new LogbrokerWriterFactory(lbBalancerHost).shardingLogbrokerWriter(
                lbWriterConfig,
                new OrderUpdateProtoSerializer(),
                new UnsignedLongShardSelector<>(lbWriterConfig, ou -> ou.getOrder().getCdpUid())
        );
    }

    @Ignore("Start only locally.")
    @Test
    public void basic() throws Exception {
        var ytImportResult = useImportService(importService -> importService.importContactsFromYt(1, ytTablePath));
        System.out.println(ytImportResult);
        for (Map.Entry<String, List<String>> stringListEntry : ytImportResult.errorsById.entrySet()) {
            System.out.println(stringListEntry.getKey() + ":" + stringListEntry.getValue());
        }
    }

}
