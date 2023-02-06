package ru.yandex.autotests.metrika.tests.ft.management.reportorder;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportOrder;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.notNullValue;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.reportorder.ReportOrderManagementTestData.REPORT_ORDER_USER;
import static ru.yandex.autotests.metrika.tests.ft.management.reportorder.ReportOrderManagementTestData.getRegularReportOrder;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.REPORT_ORDER)
@Title("Заказанные отчеты: обновление даты окончания работы заказанного отчета")
public class ExtendReportOrderTest {

    private static final UserSteps user = new UserSteps().withUser(REPORT_ORDER_USER);

    private Long counterId;
    private Long reportOrderId;
    private String token;

    @Before
    public void init() {
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();

        reportOrderId = user.onManagementSteps().onReportOrderSteps()
                .createReportOrder(counterId, getRegularReportOrder())
                .getId();

        token = user.onManagementSteps().onReportOrderSteps()
                .getReportOrderToken(counterId, reportOrderId, null);
    }

    @Test
    public void test() {
        ReportOrder extendedReportOrder = user.onManagementSteps().onReportOrderSteps()
                .extendReportOrder(counterId, reportOrderId, token);

        assertThat("дата окончания не пустая", extendedReportOrder.getEndDate(),
                notNullValue()
        );
    }

    @After
    public void cleanup() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
