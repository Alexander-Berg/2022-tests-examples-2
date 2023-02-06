package ru.yandex.autotests.metrika.tests.ft.management.reportorder;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.errors.ManagementError;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportOrder;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.nullValue;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.reportorder.ReportOrderManagementTestData.REPORT_ORDER_USER;
import static ru.yandex.autotests.metrika.tests.ft.management.reportorder.ReportOrderManagementTestData.getDefaultReportOrder;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.REPORT_ORDER)
@Title("Заказанные отчеты: удаление заказанного отчета")
public class DeleteReportOrderTest {

    private static final UserSteps user = new UserSteps().withUser(REPORT_ORDER_USER);

    private Long counterId;
    private Long reportOrderId;

    @Before
    public void init() {
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();

        reportOrderId = user.onManagementSteps().onReportOrderSteps()
                .createReportOrder(counterId, getDefaultReportOrder())
                .getId();
    }

    @Test
    public void test() {
        user.onManagementSteps().onReportOrderSteps()
                .deleteReportOrder(counterId, reportOrderId);

        ReportOrder receivedReportOrder = user.onManagementSteps().onReportOrderSteps()
                .getReportOrderAndExpectError(ManagementError.NO_OBJECT_ID, counterId, reportOrderId);

        assertThat("полученный заказанный отчет отсутствует", receivedReportOrder, nullValue());
    }

    @After
    public void cleanup() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
