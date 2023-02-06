package ru.yandex.autotests.metrika.tests.ft.report.metrika.access.nda;

import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.MELDA_RU;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.data.parameters.StaticParameters.ignoreQuota;
import static ru.yandex.autotests.metrika.errors.ReportError.WRONG_METRIC;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.nda;

@Features(Requirements.Feature.NDA)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.METADATA})
@Title("Доступ к метрикам NDA в отчетах, негативные тесты")
@RunWith(Parameterized.class)
public class NdaMetricsNegativeTest {

    private static final User OWNER = METRIKA_TEST_COUNTERS;
    private static final User GUEST_VIEW = SIMPLE_USER6;
    private static final User GUEST_EDIT = SIMPLE_USER5;

    private static final Long COUNTER_ID = MELDA_RU.getId();

    protected static final UserSteps userTest = new UserSteps().withDefaultAccuracy();

    private static UserSteps user;

    @Parameterized.Parameter(0)
    public String title;

    @Parameterized.Parameter(1)
    public User currentUser;

    @Parameterized.Parameter(2)
    public String metricName;

    @Parameterized.Parameters(name = "Доступ: {0}, пользователь: {1}, метрика {2}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .vectorValues(
                        of("владелец обычный пользователь", OWNER),
                        of("гостевой доступ на чтение", GUEST_VIEW),
                        of("гостевой доступ на редактирование", GUEST_EDIT))
                .values(userTest.onMetadataSteps().getMetrics(nda()))
                .build();
    }

    @Before
    public void setup() {
        user = new UserSteps().withDefaultAccuracy().withUser(currentUser);
    }

    @Test
    public void accessUserSuccess() {
        user.onReportSteps().getTableReportAndExpectError(
                WRONG_METRIC,
                new CommonReportParameters()
                        .withMetric(metricName)
                        .withId(COUNTER_ID));
    }
}
