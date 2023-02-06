package ru.yandex.autotests.metrika.appmetrica.tests.ft.reporting.skad;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.skad.SKAdCVParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.skad.SKAdConfigParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData;
import ru.yandex.autotests.metrika.appmetrica.wrappers.SKAdConversionValueConfigWrapper;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.model.cv.SKAdCVConfig;
import ru.yandex.metrika.mobmet.model.cv.SKAdCVConversionModelEvent;
import ru.yandex.metrika.mobmet.model.cv.events.SKAdCVEvent;
import ru.yandex.metrika.segments.apps.misc.SKAdCVModelType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.List;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;
import static ru.yandex.autotests.metrika.appmetrica.tests.ft.management.TestData.*;
import static ru.yandex.autotests.metrika.appmetrica.wrappers.SKAdConversionValueConfigWrapper.wrap;
import static ru.yandex.metrika.segments.apps.bundles.AppEventType.EVENT_CLIENT;
import static ru.yandex.metrika.segments.apps.bundles.AppEventType.EVENT_REVENUE;
import static ru.yandex.metrika.segments.apps.misc.SKAdCVModelType.*;

/**
 * Запрос в clickhouse мы здесь фактически не проверяем, но всё равно нигде нет нужных данных.
 * Потому что разница видна только в момент изменения модели.
 */
@Features(Requirements.Feature.Management.SKAD)
@Stories({
        Requirements.Story.SKAdConversionValue.INFO
})
@Title("Получение списка SKAd Conversion Value событий")
@RunWith(Parameterized.class)
public class GetSKAdConversionValueEventsTest {

    private static final User OWNER = Users.SIMPLE_USER;

    private final UserSteps user = UserSteps.onTesting(OWNER);

    private Long appId;

    @Parameterized.Parameter
    public SKAdConversionValueConfigWrapper model;

    @Parameterized.Parameter(1)
    public SKAdCVModelType requestModelType;

    @Parameterized.Parameter(2)
    public List<SKAdCVEvent> expectedEvents;

    @Parameterized.Parameters(name = "Исходное состояние {0}, запрос событий модели {1}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.of(
                param(fullConversionModel(), CONVERSION, fullConversionExpectedModel()),
                param(defaultSKAdCVEngagementConfig(), ENGAGEMENT,
                        Collections.singletonList(new SKAdCVEvent().withEventType(EVENT_REVENUE))),
                param(defaultSKAdCVNotConfiguredConfig(), NOT_CONFIGURED, Collections.emptyList()),
                param(defaultSKAdCVRevenueConfig(), REVENUE, Collections.emptyList()),
                param(fullConversionModel(), ENGAGEMENT, Collections.emptyList())
        );
    }

    @Before
    public void setup() {
        Application addedApplication = user.onApplicationSteps().addApplication(getDefaultApplication());
        appId = addedApplication.getId();
    }

    @Test
    public void test() {
        user.onSKAdConversionValueSteps().updateConfig(appId, model.getConfig(),
                new SKAdConfigParameters().forceBundles());

        SKAdCVParameters request = new SKAdCVParameters()
                .withAppId(appId)
                .withModel(requestModelType)
                .withDate1("today")
                .withDate2("today");
        List<SKAdCVEvent> actual = user.onSKAdConversionValueSteps().getEvents(request);
        assertThat("найденные события эквивалентны ожидаемым", actual, equivalentTo(expectedEvents));
    }

    @After
    public void teardown() {
        user.onApplicationSteps().deleteApplicationAndIgnoreResult(appId);
    }

    private static SKAdCVConfig fullConversionModel() {
        List<SKAdCVConversionModelEvent> events = Arrays.asList(
                new SKAdCVConversionModelEvent().withEventType(EVENT_CLIENT).withEventName("a"),
                new SKAdCVConversionModelEvent().withEventType(EVENT_CLIENT).withEventName("b"),
                new SKAdCVConversionModelEvent().withEventType(EVENT_REVENUE)
        );
        SKAdCVConfig model = TestData.defaultSKAdCVConversionConfig();
        model.getConversionModel().withEvents(events);
        return model;
    }

    private static List<SKAdCVEvent> fullConversionExpectedModel() {
        return Arrays.asList(
                new SKAdCVEvent().withEventType(EVENT_CLIENT).withEventName("a"),
                new SKAdCVEvent().withEventType(EVENT_CLIENT).withEventName("b"),
                new SKAdCVEvent().withEventType(EVENT_REVENUE)
        );
    }

    private static Object[] param(SKAdCVConfig model, SKAdCVModelType requestModel, List<SKAdCVEvent> expectedEvents) {
        return toArray(wrap(model), requestModel, expectedEvents);
    }
}
