package ru.yandex.metrika.cdp.api.tests.medium.service;

import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Function;
import java.util.stream.Collectors;

import org.junit.BeforeClass;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.multipart.MultipartFile;

import ru.yandex.metrika.cdp.dto.core.AbstractEntity;
import ru.yandex.metrika.cdp.dto.core.EntityUpdate;
import ru.yandex.metrika.cdp.dto.core.UpdateType;
import ru.yandex.metrika.cdp.dto.schema.Attribute;
import ru.yandex.metrika.cdp.dto.schema.EntityNamespace;
import ru.yandex.metrika.cdp.frontend.csv.CSVMetadataGenerator;
import ru.yandex.metrika.cdp.frontend.csv.CsvService;
import ru.yandex.metrika.cdp.frontend.csv.converter.anysetter.AttributesConversionContext;
import ru.yandex.metrika.cdp.frontend.data.CSVColumnNames;
import ru.yandex.metrika.cdp.frontend.data.DelimiterType;
import ru.yandex.metrika.cdp.frontend.rows.AbstractRowWithAttributes;
import ru.yandex.metrika.cdp.frontend.rows.AbstractUpdateRowWithAttributes;
import ru.yandex.metrika.cdp.frontend.rows.ValidatingRowProcessor;
import ru.yandex.metrika.cdp.frontend.rows.ValidatingUpdateRowProcessor;
import ru.yandex.metrika.cdp.services.CounterTimezoneProvider;
import ru.yandex.metrika.cdp.validation.AttributesValidationSequence;
import ru.yandex.metrika.cdp.ydb.AttributesDaoYdb;
import ru.yandex.metrika.dbclients.YdbSetupUtil;
import ru.yandex.metrika.util.ApiInputValidator;

public abstract class AbstractServiceTest {
    @Autowired
    protected CsvService csvService;

    @Autowired
    protected CounterTimezoneProvider counterTimezoneProvider;

    @Autowired
    protected ApiInputValidator apiInputValidator;

    @Autowired
    protected AttributesDaoYdb attributesDao;

    private static volatile boolean ydbNotInitialized = true;

    public static int getCounterId() {
        return 42;
    }

    @BeforeClass
    public static void initYdb() {
        if (ydbNotInitialized) {
            YdbSetupUtil.setupYdbFolders("schema", "segments_data", "system_data", "clients_data");
            ydbNotInitialized = false;
        }
    }

    protected <T, R extends AbstractRowWithAttributes<T>> List<T> parseRows(
            CSVColumnNames mapping,
            MultipartFile file,
            EntityNamespace entityNamespace,
            Class<R> rowClass
    ) {
        return csvService.parseRows(mapping,
                DelimiterType.SEMICOLON,
                file,
                CSVMetadataGenerator.customAnySetterGenerator(AttributesConversionContext.class).generateMeta(rowClass),
                new ValidatingRowProcessor<>(
                        getCounterId(),
                        counterTimezoneProvider.getTimezone(getCounterId()),
                        apiInputValidator,
                        getAttributes(getCounterId(), entityNamespace),
                        AttributesValidationSequence.class
                ),
                AttributesConversionContext.factory(attributesDao, getCounterId(), entityNamespace)
        );
    }

    protected <M extends AbstractEntity<?>, U extends EntityUpdate<M>, R extends AbstractUpdateRowWithAttributes<M, U>> List<U> parseUpdateRows(
            CSVColumnNames mapping,
            MultipartFile file,
            EntityNamespace entityNamespace,
            Class<R> rowClass,
            UUID uploadingId,
            UpdateType updateType
    ) {
        return csvService.parseUpdateRows(mapping,
                DelimiterType.SEMICOLON,
                file,
                CSVMetadataGenerator.customAnySetterGenerator(AttributesConversionContext.class).generateMeta(rowClass),
                new ValidatingUpdateRowProcessor<>(
                        getCounterId(),
                        counterTimezoneProvider.getTimezone(getCounterId()),
                        apiInputValidator,
                        getAttributes(getCounterId(), entityNamespace),
                        uploadingId,
                        updateType,
                        AttributesValidationSequence.class
                ),
                AttributesConversionContext.factory(attributesDao, getCounterId(), entityNamespace)
        );
    }

    private Map<String, Attribute> getAttributes(int counterId,
                                                 EntityNamespace entityType) {
        return attributesDao.get(counterId, entityType).stream()
                .collect(Collectors.toMap(Attribute::getName, Function.identity()));
    }
}
