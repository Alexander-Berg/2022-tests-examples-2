package ru.yandex.autotests.metrika.tests.ft.report.metrika.access.nda;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_METRIKA_2_0;
import static ru.yandex.autotests.metrika.data.common.users.Users.*;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.nda;

@Features(Requirements.Feature.NDA)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.METADATA})
@Title("Доступ к метрикам NDA в отчетах")
@RunWith(Parameterized.class)
public class NdaMetricsPositiveTest {

    private static final Counter COUNTER = YANDEX_METRIKA_2_0;

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
                        of("суперпользователь", SUPER_USER),
                        of("менеджер", MANAGER),
                        of("менеджер-директ", MANAGER_DIRECT),
                        of("пользователь с правом чтения счетчика idm", USER_WITH_IDM_VIEW_PERMISSION),
                        of("пользователь с правом редактирования счетчика idm", USER_WITH_IDM_EDIT_PERMISSION),
                        of("саппорт", SUPPORT))
                .values(userTest.onMetadataSteps().getMetrics(nda()))
                .build();
    }

    @Before
    public void setup() {
        user = new UserSteps().withDefaultAccuracy().withUser(currentUser);
    }

    @Test
    public void accessUserSuccess() {
        user.onReportSteps().getTableReportAndExpectSuccess(
                new CommonReportParameters()
                        .withMetric(metricName)
                        .withId(COUNTER.get(ID)));
    }
}
