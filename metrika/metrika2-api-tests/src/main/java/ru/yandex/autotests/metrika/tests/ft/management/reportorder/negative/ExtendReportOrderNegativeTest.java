package ru.yandex.autotests.metrika.tests.ft.management.reportorder.negative;

import org.junit.*;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.errors.CustomError.expect;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.reportorder.ReportOrderManagementTestData.REPORT_ORDER_USER;
import static ru.yandex.autotests.metrika.tests.ft.management.reportorder.ReportOrderManagementTestData.getRegularReportOrder;
import static ru.yandex.autotests.metrika.tests.ft.management.reportorder.ReportOrderManagementTestData.getSingleReportOrder;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.REPORT_ORDER)
@Title("Заказанные отчеты: обновление даты окончания работы заказанного отчета (негативные)")
public class ExtendReportOrderNegativeTest {

    private static final UserSteps user = new UserSteps().withUser(REPORT_ORDER_USER);

    private static Long counterId;

    @BeforeClass
    public static void init() {
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();
    }

    @Test
    public void testSingleReportOrder() {
        Long reportOrderId = user.onManagementSteps().onReportOrderSteps()
                .createReportOrder(counterId, getSingleReportOrder())
                .getId();

        String token = user.onManagementSteps().onReportOrderSteps()
                .getReportOrderToken(counterId, reportOrderId, null);

        user.onManagementSteps().onReportOrderSteps()
                .extendReportOrderAndExpectError(
                        expect(400L, equalTo("Можно продлить только регулярный отчёт.")),
                        counterId,
                        reportOrderId,
                        token
                );
    }

    @Test
    public void testIncorrectToken() {
        Long reportOrderId = user.onManagementSteps().onReportOrderSteps()
                .createReportOrder(counterId, getRegularReportOrder())
                .getId();

        user.onManagementSteps().onReportOrderSteps()
                .extendReportOrderAndExpectError(
                        expect(400L, equalTo("Неверный токен")),
                        counterId,
                        reportOrderId,
                        "incorrect_token"
                );
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
