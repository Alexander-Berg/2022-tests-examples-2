package ru.yandex.autotests.metrika.appmetrica.tests.ft.reporting.invariant;

import java.util.Collection;
import java.util.List;
import java.util.function.Supplier;

import com.google.common.collect.ImmutableList;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized.Parameter;
import org.junit.runners.Parameterized.Parameters;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.appmetrica.core.ParallelizedParameterized;
import ru.yandex.autotests.metrika.appmetrica.data.Table;
import ru.yandex.autotests.metrika.appmetrica.data.Users;
import ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.TableReportParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.UserSteps;
import ru.yandex.autotests.metrika.appmetrica.tests.Requirements;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.stream.Collectors.toList;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assumeThat;
import static ru.yandex.autotests.metrika.appmetrica.data.Application.ID;
import static ru.yandex.autotests.metrika.appmetrica.data.Applications.YANDEX_MUSIC;
import static ru.yandex.autotests.metrika.appmetrica.data.Tables.CLIENT_EVENTS_JOIN;
import static ru.yandex.autotests.metrika.appmetrica.data.Tables.GENERIC_EVENTS;
import static ru.yandex.autotests.metrika.appmetrica.data.Tables.USERS;
import static ru.yandex.autotests.metrika.appmetrica.steps.UserSteps.assumeOnResponse;

/**
 * Проверяем инвариант группировки по атрибут профиля с сегментацией по атрибуту профиля
 */
@Features(Requirements.Feature.DATA)
@Stories(Requirements.Story.DIMENSIONS)
@Title("Инварианты фильтрации (инварианты)")
@RunWith(ParallelizedParameterized.class)
public class ProfileAttributeInvariantTest {

    private static final long APP_WITH_CUSTOM_PROFILES = YANDEX_MUSIC.get(ID);

    private static final List<String> CUSTOM_PROFILES_ATTRIBUTES =
            List.of("customStringAttribute2962", "customBoolAttribute2959", "customCounterAttribute45");

    private static final UserSteps user = UserSteps.onTesting(Users.SUPER_LIMITED);

    @Parameter()
    public long appId;

    @Parameter(1)
    public Table namespace;

    @Parameter(2)
    public String profileDimension;

    @Parameter(3)
    public String metric;

    @Parameter(4)
    public FreeFormParameters otherParams;

    @Parameters(name = "appId={0}, namespace = {1}, dimension={2}, metric={3}")
    public static Collection<Object[]> createParameters() {
        return ImmutableList.<Object[]>builder()
                //todo: MOBMET-15878 когда появятся в проде данные, то надо найти и добавить кейс для
                // customNumberAttribute и для интервальных группировок
                .addAll(params(APP_WITH_CUSTOM_PROFILES, GENERIC_EVENTS, CUSTOM_PROFILES_ATTRIBUTES, "users", null))
                .addAll(params(APP_WITH_CUSTOM_PROFILES, CLIENT_EVENTS_JOIN, CUSTOM_PROFILES_ATTRIBUTES,
                        "eventsPerDevice", null))
                .addAll(params(APP_WITH_CUSTOM_PROFILES, USERS, CUSTOM_PROFILES_ATTRIBUTES, "newUsersShare", null))
                //todo: добавить воронки после решения вопроса об отправках пушей в них
//                .addAll(params(APP_WITH_CUSTOM_PROFILES, USER_FUNNELS_JOIN, CUSTOM_PROFILES_ATTRIBUTES,
//                        "devicesInStep2",
//                        () -> new FreeFormParameters().append(
//                                "funnel_pattern",
//                                "cond(ym:uft, isAnyEvent == 'yes' and sessionType=='foreground')  " +
//                                        "cond(ym:uft, eventType=='EVENT_CLIENT' and eventLabel=='PlayTrack' and " +
//                                        "sessionType=='foreground')"
//                        )))
                .build();
    }

    private static Collection<Object[]> params(long appId,
                                               Table namespace,
                                               List<String> profileDimensions,
                                               String metric,
                                               Supplier<FreeFormParameters> otherParams) {
        Supplier<FreeFormParameters> params = otherParams != null ? otherParams : FreeFormParameters::new;
        return profileDimensions.stream()
                .map(profileDimension -> new Object[]{appId, namespace, profileDimension, metric, params.get()})
                .collect(toList());
    }

    @Test
    public void test() {
        IFormParameters params = getProfileGroupedParams();
        StatV1DataGETSchema profileGroupedResult = user.onReportSteps().getTableReport(params);
        assumeOnResponse(profileGroupedResult);

        String profileAttributeValue = profileGroupedResult.getData().get(0).getDimensions().get(0).get("name");

        params = getProfileSegmentedParams(
                namespace.getNamespace() + profileDimension + "=='" + profileAttributeValue + "'");
        StatV1DataGETSchema profileFilteredResult = user.onReportSteps().getTableReport(params);
        assumeOnResponse(profileFilteredResult);

        params = getProfileSegmentedParams("exists ym:p:device,ym:p:profileOrigin with " +
                "(" + profileDimension + "=='" + profileAttributeValue + "')");
        StatV1DataGETSchema profileSegmentedResult = user.onReportSteps().getTableReport(params);
        assumeOnResponse(profileSegmentedResult);

        long profileGroupedMetric = Math.round(profileGroupedResult.getData().get(0).getMetrics().get(0));
        long profileFilteredMetric = Math.round(profileFilteredResult.getTotals().get(0));
        long profileSegmentedMetric = Math.round(profileSegmentedResult.getTotals().get(0));

        assumeThat("значения метрик с группировкой по атрибуту профиля и с фильтром по нему равны",
                profileGroupedMetric,
                equalTo(profileFilteredMetric));
        assertThat("значения метрик с группировкой по атрибуту профиля и с сегментацией по нему равны",
                profileGroupedMetric,
                equalTo(profileSegmentedMetric));
    }

    private IFormParameters getProfileGroupedParams() {
        return otherParams.append(new TableReportParameters()
                .withDimension(namespace.getNamespace() + profileDimension)
                .withMetric(namespace.getNamespace() + metric)
                .withId(appId)
                .withAccuracy("1")
                .withDate1("24daysAgo")
                .withDate2("21daysAgo")
                .withSort("-" + namespace.getNamespace() + metric)
                .withLimit(10)
                .withLang("ru")
                .withRequestDomain("com"));
    }

    private IFormParameters getProfileSegmentedParams(String filter) {
        return otherParams.append(new TableReportParameters()
                .withDimension(namespace.getNamespace() + "gender")
                .withMetric(namespace.getNamespace() + metric)
                .withId(appId)
                .withAccuracy("1")
                .withDate1("24daysAgo")
                .withDate2("21daysAgo")
                .withFilters(filter)
                .withIncludeUndefined(true)
                .withLang("ru")
                .withRequestDomain("com"));
    }
}
