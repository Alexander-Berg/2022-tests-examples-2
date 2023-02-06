package ru.yandex.autotests.metrika.tests.ft.management.reportorder;

import org.hamcrest.Matcher;
import org.joda.time.DateTimeZone;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportOrder;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.matchers.jodatime.JodaTimeMatchers.dateTimeWithTimeZoneOffset;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getCounterWithTimeZone;
import static ru.yandex.autotests.metrika.tests.ft.management.reportorder.ReportOrderManagementTestData.REPORT_ORDER_USER;
import static ru.yandex.autotests.metrika.tests.ft.management.reportorder.ReportOrderManagementTestData.getSingleReportOrder;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.REPORT_ORDER)
@Title("Заказанные отчеты: проверка нестандартного часового пояса")
public class ReportOrderTimeZoneTest {

    private static final String TIME_ZONE = "Asia/Yekaterinburg";

    private static final UserSteps user = new UserSteps().withUser(REPORT_ORDER_USER);

    private static Long counterId;

    private Matcher<ReportOrder> matcher;

    private ReportOrder createdReportOrder;

    @BeforeClass
    public static void initClass() {
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getCounterWithTimeZone(TIME_ZONE))
                .getId();
    }

    @Before
    public void init() {
        ReportOrder reportOrder = getSingleReportOrder();

        createdReportOrder = user.onManagementSteps().onReportOrderSteps()
                .createReportOrder(counterId, reportOrder);

        int expectedOffset = DateTimeZone.forID(TIME_ZONE).getOffset(createdReportOrder.getCreateTime());

        matcher = allOf(
                beanEquivalent(reportOrder),
                hasProperty("createTime", dateTimeWithTimeZoneOffset(equalTo(expectedOffset)))
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
