package ru.yandex.metrika.cdp.api.tests.medium.service;

import java.time.ZoneId;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

import ru.yandex.direct.utils.DateTimeUtils;
import ru.yandex.metrika.api.constructor.contr.FeatureService;
import ru.yandex.metrika.api.management.tests.util.FeatureServiceMock;
import ru.yandex.metrika.apiclient.intapi.MetrikaIntapiFacade;
import ru.yandex.metrika.cdp.dao.CdpCountersDao;
import ru.yandex.metrika.cdp.dao.SchemaDao;
import ru.yandex.metrika.cdp.dao.UploadingsDao;
import ru.yandex.metrika.cdp.frontend.csv.CsvService;
import ru.yandex.metrika.cdp.services.CounterTimezoneProvider;
import ru.yandex.metrika.cdp.services.UploadingService;
import ru.yandex.metrika.cdp.validation.ValidationHelper;
import ru.yandex.metrika.cdp.ydb.AttributesDaoYdb;
import ru.yandex.metrika.cdp.ydb.CdpCountersDaoYdb;
import ru.yandex.metrika.cdp.ydb.SchemaDaoYdb;
import ru.yandex.metrika.cdp.ydb.UploadingsDaoYdb;
import ru.yandex.metrika.dbclients.config.YdbConfig;
import ru.yandex.metrika.dbclients.ydb.YdbTemplate;
import ru.yandex.metrika.util.locale.LocaleDictionaries;

import static org.mockito.Mockito.mock;

@Import({YdbConfig.class})
@Configuration
public class CommonServiceConfig {

    @Bean
    public CsvService csvService() {
        return new CsvService();
    }

    @Bean
    public LocaleDictionaries localeDictionaries() {
        return new LocaleDictionaries();
    }

    @Bean
    public CounterTimezoneProvider counterTimezoneProvider() {
        return counterId -> ZoneId.of(DateTimeUtils.MOSCOW_TIMEZONE);
    }

    @Bean
    public UploadingsDao uploadingsDao(YdbTemplate ydbTemplate) {
        var uploadingsDaoYdb = new UploadingsDaoYdb(ydbTemplate);
        uploadingsDaoYdb.setTablePrefix(ydbTemplate.getDatabase() + "/system_data");
        return uploadingsDaoYdb;
    }

    @Bean
    UploadingService uploadingService(UploadingsDao uploadingsDao) {
        return new UploadingService(uploadingsDao);
    }

    @Bean
    public FeatureService featureService() {
        return new FeatureServiceMock();
    }

    @Bean
    public AttributesDaoYdb attributesDaoYdb(YdbTemplate ydbTemplate) {
        var attributesDaoYdb = new AttributesDaoYdb(ydbTemplate);
        attributesDaoYdb.setTablePrefix(ydbTemplate.getDatabase() + "/schema");
        return attributesDaoYdb;
    }

    @Bean
    public SchemaDao schemaDao(YdbTemplate ydbTemplate) {
        return new SchemaDaoYdb(ydbTemplate, ydbTemplate.getDatabase() + "/schema");
    }

    @Bean
    public CdpCountersDao cdpCountersDao(YdbTemplate ydbTemplate) {
        var cdpCountersDaoYdb = new CdpCountersDaoYdb(ydbTemplate);
        cdpCountersDaoYdb.setTablePrefix(ydbTemplate.getDatabase() + "/system_data");
        return cdpCountersDaoYdb;
    }

    @Bean
    public ValidationHelper attributesValidationHelper(SchemaDao schemaDao,
                                                       CounterTimezoneProvider counterTimezoneProvider,
                                                       LocaleDictionaries localeDictionaries) {
        return new ValidationHelper(schemaDao, counterTimezoneProvider, localeDictionaries);
    }

    @Bean
    public MetrikaIntapiFacade metrikaIntapiFacade() {
        return mock(MetrikaIntapiFacade.class);
    }
}
