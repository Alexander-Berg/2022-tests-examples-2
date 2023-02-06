package ru.yandex.autotests.metrika.tests.ft.management.reportorder;

import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportOrder;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.List;

import static com.google.common.collect.ImmutableList.of;
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
@Title("Заказанные отчеты: отписка от заказанного отчета")
public class ReportOrderUnsubscribeTest {

    private static final List<String> EMAILS = of("user1@example.com", "user2@example.org");
    private static final String EMAIL_TO_UNSUBSCRIBE = "user1@example.com";
    private static final List<String> EMAILS_AFTER_UNSUBSCRIBE = of("user2@example.org");

    private static final UserSteps user = new UserSteps().withUser(REPORT_ORDER_USER);
    private static final UserSteps unauthorizedUser = new UserSteps().withUser(Users.USER_WITH_EMPTY_TOKEN);

    private static Long counterId;

    private static ReportOrder unsubscribedReportOrder;

    @BeforeClass
    public static void init() {
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();

        ReportOrder reportOrder = user.onManagementSteps().onReportOrderSteps()
                .createReportOrder(counterId, getDefaultReportOrder()
                        .withRecipientEmails(EMAILS)
                );

        String token = user.onManagementSteps().onReportOrderSteps()
                .getReportOrderToken(counterId, reportOrder.getId(), EMAIL_TO_UNSUBSCRIBE);

        unsubscribedReportOrder = unauthorizedUser.onManagementSteps().onReportOrderSteps()
                .unsubscribe(counterId, reportOrder.getId(), EMAIL_TO_UNSUBSCRIBE, token);
    }

    @Test
    public void testUnsubscribe() {
        assertThat("email-ы получателей не содержат отписанный email", unsubscribedReportOrder.getRecipientEmails(),
                equalTo(EMAILS_AFTER_UNSUBSCRIBE)
        );
    }

    @Test
    public void testGet() {
        ReportOrder receivedReportOrder = user.onManagementSteps().onReportOrderSteps()
                .getReportOrder(counterId, unsubscribedReportOrder.getId());

        assertThat("email-ы получателей не содержат отписанный email", receivedReportOrder.getRecipientEmails(),
                equalTo(EMAILS_AFTER_UNSUBSCRIBE)
        );
    }

    @AfterClass
    public static void cleanup() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
