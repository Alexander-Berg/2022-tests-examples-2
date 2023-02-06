package ru.yandex.autotests.metrika.tests.ft.report.metrika.permission;

import java.util.Collection;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.common.CounterConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.data.parameters.report.v1.BytimeReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonDrilldownReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.DrillDownReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static com.google.common.collect.ImmutableList.of;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.BY_TIME;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.COMPARISON;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.COMPARISON_DRILLDOWN;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.DRILLDOWN;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.TABLE;

@Features(Requirements.Feature.REPORT)
@Stories(Requirements.Story.Report.PERMISSION)
@Title("Доступ к отчету")
@RunWith(Parameterized.class)
public class PermissionPositiveTest {
    private static UserSteps user;

    private static final String METRIC_NAME = "ym:s:visits";
    private static final String DIMENSION_NAME = "ym:s:age";

    private static final String START_DATE = "2014-11-26";
    private static final String END_DATE = "2014-11-26";

    @Parameterized.Parameter()
    public RequestType<?> requestType;

    @Parameterized.Parameter(1)
    public IFormParameters parameters;

    @Parameterized.Parameter(2)
    public String title;

    @Parameterized.Parameter(3)
    public User currentUser;

    @Parameterized.Parameter(4)
    public Counter counter;

    @Parameterized.Parameters(name = "Отчет: {0}, пользователь: {3}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .vectorValues(
                        of(TABLE, new TableReportParameters()
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)),
                        of(DRILLDOWN, new DrillDownReportParameters()
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)),
                        of(COMPARISON, new ComparisonReportParameters()
                                .withDate1_a(START_DATE)
                                .withDate2_a(END_DATE)
                                .withDate1_b(START_DATE)
                                .withDate2_b(END_DATE)),
                        of(COMPARISON_DRILLDOWN, new ComparisonDrilldownReportParameters()
                                .withDate1_a(START_DATE)
                                .withDate2_a(END_DATE)
                                .withDate1_b(START_DATE)
                                .withDate2_b(END_DATE)),
                        of(BY_TIME, new BytimeReportParameters()
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)))
                .vectorValues(
                        of("менеджер", Users.MANAGER, CounterConstants.LITE_DATA),
                        of("менеджер Директа", Users.MANAGER_DIRECT, CounterConstants.LITE_DATA),
                        of("саппорт", Users.SUPPORT, CounterConstants.LITE_DATA),
                        of("суперпользователь", Users.SUPER_USER, CounterConstants.LITE_DATA),
                        of("иной пользователь", Users.SIMPLE_USER, CounterConstants.PUBLIC_COUNTER),
                        of("с пустым токеном", Users.USER_WITH_EMPTY_TOKEN, CounterConstants.PUBLIC_COUNTER),
                        of("представитель", Users.PERMISSION_TEST_USER, Counters.TEST_DELEGATE_COUNTER),
                        of("с правом на просмотр", Users.PERMISSION_TEST_USER, Counters.TEST_VIEW_PERMISSION_COUNTER),
                        of("с правом на редактирование", Users.PERMISSION_TEST_USER, Counters.TEST_EDIT_PERMISSION_COUNTER),
                        of("яндекс менеджер", Users.YAMANAGER, Counters.YANDEX_DIRECT),
                        of("Суперcмотритель (Технические счетчики), Справочник", Users.YA_SERVICE_READ_SPRAV, Counters.YANDEX_EATS_ON_MAPS)
                )
                .build();
    }

    @Before
    public void setup() {
        user = new UserSteps().withUser(currentUser);
    }

    @Test
    public void checkData() {
        user.onReportSteps().getReportAndExpectSuccess(
                requestType,
                new CommonReportParameters()
                        .withId(counter)
                        .withMetric(METRIC_NAME)
                        .withDimension(DIMENSION_NAME),
                parameters);
    }
}
