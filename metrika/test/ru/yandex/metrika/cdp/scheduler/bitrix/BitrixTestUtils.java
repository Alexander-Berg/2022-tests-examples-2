package ru.yandex.metrika.cdp.scheduler.bitrix;

import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

import com.google.common.cache.CacheBuilder;
import com.google.common.cache.CacheLoader;
import com.google.common.cache.LoadingCache;
import org.junit.Assert;

import ru.yandex.metrika.cdp.dto.schema.connector.Connector;
import ru.yandex.metrika.cdp.dto.schema.connector.ConnectorAttributes;
import ru.yandex.metrika.cdp.dto.schema.connector.ConnectorAttributesFactory;
import ru.yandex.metrika.cdp.dto.schema.connector.ConnectorStatus;
import ru.yandex.metrika.cdp.dto.schema.connector.ConnectorType;
import ru.yandex.metrika.cdp.dto.schema.connector.bitrix.BitrixConnectorAttributes;
import ru.yandex.metrika.cdp.scheduler.bitrix.dto.BitrixAbstractEntity;
import ru.yandex.metrika.cdp.scheduler.bitrix.validation.BitrixAbstractEntityValidator;

public class BitrixTestUtils {
    public static final Integer NOT_ACTIVE_COUNTER_ID = 1;
    public static final Integer COUNTER_ID_WITHOUT_CONNECTOR = 2;
    public static final Integer COUNTER_ID_WITH_DISABLED_LEADS = 3;
    public static final String DEALS_STATUSES_ENTITY_NAME = "DEAL_STAGE";
    public static final String LEADS_STATUSES_ENTITY_NAME = "STATUS";
    public static final List<String> DEFAULT_CLIENT_ID_NAMES = Arrays.asList(
            "metrika_client_id",
            "metrikaclientid",
            "metrika-client-id",
            "metrica_client_id",
            "metricaclientid",
            "metrica-client-id",
            "metrika_client_ids",
            "metrikaclientids",
            "metrika-client-ids",
            "metrica_client_ids",
            "metricaclientids",
            "metrica-client-ids",
            "metrika",
            "metrica",
            "clientid",
            "clientids",
            "client-id",
            "client-ids"
    );

    public static final LoadingCache<Integer, Connector> connectorsCache = CacheBuilder.newBuilder()
            .build(new CacheLoader<>() {
                @Override
                public Connector load(Integer counterId) {
                    return loadAll(List.of(counterId)).get(counterId);
                }

                @Override
                public Map<Integer, Connector> loadAll(Iterable<? extends Integer> keys) {
                    return StreamSupport.stream(keys.spliterator(), false)
                            .collect(Collectors.toMap(counterId -> counterId, BitrixTestUtils::getConnector));
                }
            });

    public static Connector getConnector(int counterId) {
        if (COUNTER_ID_WITHOUT_CONNECTOR == counterId) {
            return new Connector(
                    counterId,
                    ConnectorType.BITRIX
            );
        }

        ConnectorAttributes attributes = ConnectorAttributesFactory.getConnectorAttributes(counterId, ConnectorType.BITRIX);
        if (COUNTER_ID_WITH_DISABLED_LEADS == counterId) {
            attributes.update(new BitrixConnectorAttributes(false));
        }
        return new Connector(
                counterId,
                "test.url",
                ConnectorType.BITRIX,
                ConnectorStatus.CONNECTED,
                Instant.now(),
                attributes
        );
    }

    public static final LoadingCache<Integer, Boolean> activeCountersCache = CacheBuilder.newBuilder()
            .build(new CacheLoader<>() {
                @Override
                public Boolean load(Integer counterId) {
                    return loadAll(List.of(counterId)).get(counterId);
                }

                @Override
                public Map<Integer, Boolean> loadAll(Iterable<? extends Integer> keys) {
                    return StreamSupport.stream(keys.spliterator(), false)
                            .collect(Collectors.toMap(counterId -> counterId, counterId -> !NOT_ACTIVE_COUNTER_ID.equals(counterId)));
                }
            });

    public static void assertValidatorErrorsSize(BitrixAbstractEntityValidator<? extends BitrixAbstractEntity> validator,
                                                 int expectedErrorsSize) {
        assertValidatorErrorsSize(validator, 1, expectedErrorsSize);
    }

    public static void assertValidatorErrorsSize(BitrixAbstractEntityValidator<? extends BitrixAbstractEntity> validator,
                                                 int entitiesNumber,
                                                 int expectedErrorsSize) {
        if (expectedErrorsSize == 0) {
            Assert.assertEquals(0, validator.getErrorsById().size());
        } else {
            Assert.assertEquals(entitiesNumber, validator.getErrorsById().size());
            validator.getErrorsById().values().stream()
                    .map(List::size)
                    .forEach(size -> Assert.assertEquals(expectedErrorsSize, (long) size));
        }
    }
}
