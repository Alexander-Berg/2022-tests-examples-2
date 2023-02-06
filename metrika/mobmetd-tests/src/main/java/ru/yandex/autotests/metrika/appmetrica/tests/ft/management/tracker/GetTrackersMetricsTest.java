package ru.yandex.autotests.metrika.appmetrica.tests.ft.management.tracker;

import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;

import com.google.common.collect.ImmutableList;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.appmetrica.data.Application;
import ru.yandex.autotests.metrika.appmetrica.data.Applications;
import ru.yandex.autotests.metrika.appmetrica.data.User;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.metrika.mobmet.model.redirect.Campaign;
import ru.yandex.metrika.mobmet.model.redirect.CampaignMetrics;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.allOf;
import static org.hamcrest.Matchers.empty;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.resetCurrentLayer;
import static ru.yandex.autotests.metrika.appmetrica.data.ParallellismUtils.setCurrentLayerByApp;
import static ru.yandex.autotests.metrika.appmetrica.data.Users.SUPER_LIMITED;
import static ru.yandex.autotests.metrika.appmetrica.matchers.ResponseMatchers.equivalentTo;

/**
 * @author dancingelf
 */
@Features(Requirements.Feature.Management.TRACKER)
@Stories(Requirements.Story.Tracker.INFO)
@Title("Получение статистики по трекерам")
@RunWith(Parameterized.class)
public class GetTrackersMetricsTest {

    private static final User USER = SUPER_LIMITED;

    private static final UserSteps user = UserSteps.onTesting(USER);

    @Parameterized.Parameter
    public Long appId;

    @Parameterized.Parameters(name = "Приложение {0,number,#}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                .add(param(Applications.KINOPOISK))
                .build();
    }

    private List<String> requestedTrackingIds;
    private List<CampaignMetrics> metrics;

    @Before
    public void setup() {
        setCurrentLayerByApp(appId);
        // Запрашиваем список трекеров и метрики для указанного target uid-а, потому что SUPER_LIMITED так может.
        // Иначе нужно было бы выдать грант на приложение, а для приложений yastorepublisher это делается только через IDM.
        long appOwnerUid = user.onApplicationSteps().getApplication(appId).getUid();
        requestedTrackingIds = user.onTrackerSteps().getTrackerList(appId, appOwnerUid).stream()
                .map(Campaign::getTrackingId)
                .collect(Collectors.toList());
        metrics = user.onTrackerSteps().getTrackerMetrics(requestedTrackingIds, appOwnerUid);

        assumeThat("получены метрики для одного трекера", metrics, not(empty()));
    }

    @Test
    public void testTrackingIds() {
        List<String> actual = metrics.stream()
                .map(CampaignMetrics::getTrackingId)
                .collect(Collectors.toList());
        assertThat("Идентификаторы трекеров присутствуют в ответе в порядке запроса",
                actual, equivalentTo(requestedTrackingIds));
    }

    @Test
    public void testMetricsValues() {
        // К сожалению, мы не знаем конкретных значений метрик, поэтому остается проверить
        // только существование метрик с показателями не равными нулю
        assertThat("в ответе присутствуют данные метрик", metrics, hasItem(allOf(
                having(on(CampaignMetrics.class).getClicks(), greaterThan(0L)),
                having(on(CampaignMetrics.class).getInstalls(), greaterThan(0L)),
                having(on(CampaignMetrics.class).getConversion(), greaterThan(0.0)),
                having(on(CampaignMetrics.class).getRetentionD1(), greaterThan(0.0)),
                having(on(CampaignMetrics.class).getRetentionD7(), greaterThan(0.0)),
                having(on(CampaignMetrics.class).getRetentionD28(), greaterThan(0.0))
        )));
    }

    @After
    public void tearddown() {
        resetCurrentLayer();
    }

    public static Object[] param(Application application) {
        return toArray(application.get(ID));
    }
}
