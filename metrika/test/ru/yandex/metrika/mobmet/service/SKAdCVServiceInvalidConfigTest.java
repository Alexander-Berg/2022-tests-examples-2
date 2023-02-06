package ru.yandex.metrika.mobmet.service;

import java.math.BigDecimal;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Objects;

import org.hamcrest.Description;
import org.hamcrest.TypeSafeMatcher;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.ExpectedException;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.metrika.api.WrongParameterException;
import ru.yandex.metrika.mobmet.dao.SKAdConversionValueDao;
import ru.yandex.metrika.mobmet.model.cv.SKAdCVConfig;
import ru.yandex.metrika.mobmet.model.cv.SKAdCVConversionModel;
import ru.yandex.metrika.mobmet.model.cv.SKAdCVConversionModelEvent;
import ru.yandex.metrika.mobmet.model.cv.SKAdCVEngagementModel;
import ru.yandex.metrika.mobmet.model.cv.SKAdCVRevenueModel;
import ru.yandex.metrika.mobmet.model.cv.SKAdMeasurementTime;
import ru.yandex.metrika.mobmet.model.cv.SKAdMeasurementTimeUnit;
import ru.yandex.metrika.mobmet.service.cv.model.ConversionCvModelHandler;
import ru.yandex.metrika.mobmet.service.cv.model.EngagementCvModelHandler;
import ru.yandex.metrika.mobmet.service.cv.model.NotConfiguredCvModelHandler;
import ru.yandex.metrika.mobmet.service.cv.model.RevenueCvModelHandler;
import ru.yandex.metrika.segments.apps.bundles.AppEventType;

import static org.mockito.Matchers.anyList;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static ru.yandex.metrika.segments.apps.bundles.AppEventType.EVENT_CLIENT;
import static ru.yandex.metrika.segments.apps.bundles.AppEventType.EVENT_REVENUE;
import static ru.yandex.metrika.segments.apps.bundles.AppEventType.EVENT_UPDATE;
import static ru.yandex.metrika.segments.apps.misc.SKAdCVModelType.CONVERSION;
import static ru.yandex.metrika.segments.apps.misc.SKAdCVModelType.NOT_CONFIGURED;
import static ru.yandex.metrika.segments.apps.misc.SKAdCVModelType.REVENUE;

@RunWith(Parameterized.class)
public class SKAdCVServiceInvalidConfigTest {

    private static final int APP_ID = 1;
    private static final String BUNDLE_ID = "ru.yandex.test";

    private SKAdCVService service;

    @Rule
    public ExpectedException expectedException = ExpectedException.none();

    @Parameterized.Parameter
    public String errorMessage;

    @Parameterized.Parameter(1)
    public SKAdCVConfig config;

    @Parameterized.Parameters
    public static Collection<Object[]> data() {
        return List.of(
                param("max_measurement_time is null",
                        revenueConfig(EVENT_REVENUE, null, "RUB", BigDecimal.ONE).withMaxMeasurementTime(null)),
                param("Illegal currency: ODS", revenueConfig(EVENT_REVENUE, null, "ODS", BigDecimal.ONE)),
                param("Empty config shouldn't contain model",
                        revenueConfig(EVENT_REVENUE, null, "RUB", BigDecimal.ONE).withModelType(NOT_CONFIGURED)),
                param("Too many models in config", revenueConfig(EVENT_REVENUE, null, "RUB", BigDecimal.ONE)
                        .withEngagementModel(new SKAdCVEngagementModel(EVENT_REVENUE, null, null, 1))),
                param("Event list is empty", conversionConfig(List.of())),
                param("Too many events", conversionConfig(List.of(
                        new SKAdCVConversionModelEvent(EVENT_CLIENT, "event1", null),
                        new SKAdCVConversionModelEvent(EVENT_CLIENT, "event2", null),
                        new SKAdCVConversionModelEvent(EVENT_CLIENT, "event3", null),
                        new SKAdCVConversionModelEvent(EVENT_CLIENT, "event4", null),
                        new SKAdCVConversionModelEvent(EVENT_CLIENT, "event5", null),
                        new SKAdCVConversionModelEvent(EVENT_CLIENT, "event6", null),
                        new SKAdCVConversionModelEvent(EVENT_CLIENT, "event7", null)))),
                param("Illegal event subtype 'subtype' for event type 'EVENT_CLIENT'", conversionConfig(List.of(
                        new SKAdCVConversionModelEvent(EVENT_CLIENT, "event", "subtype")))),
                param("Illegal event type: EVENT_UPDATE", conversionConfig(List.of(
                        new SKAdCVConversionModelEvent(EVENT_UPDATE, "event", "subtype")))),
                param("Event list contains duplicates", conversionConfig(List.of(
                        new SKAdCVConversionModelEvent(EVENT_CLIENT, "event", null),
                        new SKAdCVConversionModelEvent(EVENT_CLIENT, "event", null))))
        );
    }

    @Before
    public void before() {
        BundleIdsService bundleIdsService = mock(BundleIdsService.class);
        when(bundleIdsService.getAppStoreBundleIds(APP_ID)).thenReturn(List.of(BUNDLE_ID));
        SKAdConversionValueDao skadDao = mock(SKAdConversionValueDao.class);
        when(skadDao.getUsedBundleIds(anyList())).thenReturn(Map.of());
        service = new SKAdCVService(bundleIdsService, skadDao, List.of(
                new NotConfiguredCvModelHandler(),
                new ConversionCvModelHandler(),
                new RevenueCvModelHandler(),
                new EngagementCvModelHandler()));
    }

    @Test
    public void invalid() {
        expectedException.expect(new TypeSafeMatcher<WrongParameterException>() {
            @Override
            protected boolean matchesSafely(WrongParameterException e) {
                return Objects.equals(errorMessage, e.getMessage());
            }

            @Override
            public void describeTo(Description matcherDescription) {
                matcherDescription.appendValue(errorMessage);
            }
        });
        service.makeAdditionalValidation(APP_ID, config, false);
    }

    private static Object[] param(String errorMessage, SKAdCVConfig config) {
        return new Object[]{errorMessage, config};
    }

    private static SKAdCVConfig conversionConfig(List<SKAdCVConversionModelEvent> events) {
        return new SKAdCVConfig()
                .withBundleIds(List.of(BUNDLE_ID))
                .withModelType(CONVERSION)
                .withConversionModel(new SKAdCVConversionModel(events))
                .withMaxMeasurementTime(new SKAdMeasurementTime(100, SKAdMeasurementTimeUnit.DAYS));
    }

    private static SKAdCVConfig revenueConfig(AppEventType eventType, String subtype, String currency, BigDecimal step) {
        return new SKAdCVConfig()
                .withBundleIds(List.of(BUNDLE_ID))
                .withModelType(REVENUE)
                .withRevenueModel(new SKAdCVRevenueModel(eventType, subtype, currency, step))
                .withMaxMeasurementTime(new SKAdMeasurementTime(100, SKAdMeasurementTimeUnit.DAYS));
    }
}
