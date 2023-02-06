package ru.yandex.autotests.metrika.tests.ft.management.reportorder;

import org.hamcrest.Matcher;
import org.joda.time.*;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportOrder;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportOrderStatus;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static com.google.common.collect.ImmutableList.of;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.matchers.jodatime.JodaTimeMatchers.localDateWithField;
import static ru.yandex.autotests.metrika.tests.ft.management.reportorder.ReportOrderManagementTestData.*;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.REPORT_ORDER)
@Title("Заказанные отчеты: создание заказанного отчета")
@RunWith(Parameterized.class)
public class CreateReportOrderTest {

    private static final UserSteps user = new UserSteps().withUser(REPORT_ORDER_USER);

    private static Long counterId;

    private Matcher<ReportOrder> matcher;

    private ReportOrder createdReportOrder;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> getParameters() {
        return of(
                toArray("Одноразовый отчет", getSingleReportOrder(), anything()),
                toArray("Ежедневный отчет", getDailyReportOrder(),
                        hasProperty("endDate", greaterThan(LocalDate.now()))
                ),
                toArray("Еженедельный отчет", getWeeklyReportOrder(),
                        hasProperty("endDate", allOf(
                                greaterThan(LocalDate.now()),
                                localDateWithField(DateTimeFieldType.dayOfWeek(), equalTo(DateTimeConstants.MONDAY))
                        ))
                ),
                toArray("Ежемесячный отчет", getMonthlyReportOrder(),
                        hasProperty("endDate", allOf(
                                greaterThan(LocalDate.now()),
                                localDateWithField(DateTimeFieldType.dayOfMonth(), equalTo(1))
                        ))
                ),
                toArray("Отчет с одним email получателя", getReportOrderWithSingleRecipientEmail(), anything()),
                toArray("Отчет с несколькими email получателей", getReportOrderWithMultipleRecipientEmails(), anything()),
                toArray("Отчет со всеми параметрами отчета", getReportOrderWithAllReportParams(), anything())
        );
    }

    @SuppressWarnings("unused")
    @Parameterized.Parameter
    public String description;

    @Parameterized.Parameter(1)
    public ReportOrder reportOrder;

    @Parameterized.Parameter(2)
    public Matcher<ReportOrder> additionalMatcher;

    @BeforeClass
    public static void initClass() {
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();
    }

    @Before
    public void init() {
        createdReportOrder = user.onManagementSteps().onReportOrderSteps()
                .createReportOrder(counterId, reportOrder);

        matcher = allOf(
                beanEquivalent(reportOrder),
                hasProperty("id", notNullValue()),
                hasProperty("ownerLogin", equalTo(REPORT_ORDER_USER.get(User.LOGIN))),
                hasProperty("createTime", notNullValue()),
                hasProperty("status", equalTo(ReportOrderStatus.ACTIVE)),
                additionalMatcher
        );
    }

    @Test
    public void testCreate() {
        assertThat("созданный заказанный отчет соответствует ожиданию", createdReportOrder, matcher);
    }

    @Test
    public void testGet() {
        ReportOrder receivedReportOrder = user.onManagementSteps().onReportOrderSteps()
                .getReportOrder(counterId, createdReportOrder.getId());

        assertThat("полученный заказанный отчет соответствует ожиданию", receivedReportOrder, matcher);
    }

    @AfterClass
    public static void cleanupClass() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
