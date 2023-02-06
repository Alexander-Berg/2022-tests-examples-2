package ru.yandex.autotests.metrika.tests.ft.management.reportorder.negative;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static com.google.common.collect.ImmutableList.of;
import static org.hamcrest.Matchers.equalTo;
import static ru.yandex.autotests.metrika.errors.CustomError.expect;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.reportorder.ReportOrderManagementTestData.REPORT_ORDER_USER;
import static ru.yandex.autotests.metrika.tests.ft.management.reportorder.ReportOrderManagementTestData.getDefaultReportOrder;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.REPORT_ORDER)
@Title("Заказанные отчеты: отписка от заказанного отчета (негативные)")
public class ReportOrderUnsubscribeNegativeTest {

    private static final String EMAIL = "user@test.com";

    private static final UserSteps user = new UserSteps().withUser(REPORT_ORDER_USER);
    private static final UserSteps unauthorizedUser = new UserSteps().withUser(Users.USER_WITH_EMPTY_TOKEN);

    private Long counterId;
    private Long reportOrderId;

    @Before
    public void init() {
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();

        reportOrderId = user.onManagementSteps().onReportOrderSteps()
                .createReportOrder(counterId, getDefaultReportOrder()
                        .withRecipientEmails(of(EMAIL))
                )
                .getId();
    }

    @Test
    public void test() {
        unauthorizedUser.onManagementSteps().onReportOrderSteps()
                .unsubscribeAndExpectError(
                        expect(400L, equalTo("Неверный токен")),
                        counterId,
                        reportOrderId,
                        EMAIL,
                        "incorrect_token"
                );
    }

    @After
    public void cleanup() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
