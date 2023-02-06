package ru.yandex.autotests.metrika.tests.ft.management.reportorder;

import org.junit.*;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportOrder;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportOrderStatus;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.reportorder.ReportOrderManagementTestData.REPORT_ORDER_USER;
import static ru.yandex.autotests.metrika.tests.ft.management.reportorder.ReportOrderManagementTestData.getDefaultReportOrder;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.REPORT_ORDER)
@Title("Заказанные отчеты: деактивация заказанного отчета")
public class InactivateReportOrderTest {

    private static final UserSteps user = new UserSteps().withUser(REPORT_ORDER_USER);

    private static Long counterId;

    private static ReportOrder inactivatedReportOrder;

    @BeforeClass
    public static void init() {
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();

        ReportOrder reportOrder = user.onManagementSteps().onReportOrderSteps()
                .createReportOrder(counterId, getDefaultReportOrder());

        inactivatedReportOrder = user.onManagementSteps().onReportOrderSteps()
                .inactivateReportOrder(counterId, reportOrder.getId());
    }

    @Test
    public void testInactivate() {
        assertThat("статус деактивированного заказанного отчета - неактивный", inactivatedReportOrder.getStatus(),
                equalTo(ReportOrderStatus.INACTIVE)
        );
    }

    @Test
    public void testGet() {
        ReportOrder receivedReportOrder = user.onManagementSteps().onReportOrderSteps()
                .getReportOrder(counterId, inactivatedReportOrder.getId());

        assertThat("статус полученного заказанного отчета - неактивный", receivedReportOrder.getStatus(),
                equalTo(ReportOrderStatus.INACTIVE)
        );
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
