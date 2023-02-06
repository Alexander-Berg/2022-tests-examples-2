package ru.yandex.autotests.metrika.tests.ft.management.reportorder;

import org.hamcrest.Matcher;
import org.joda.time.DateTimeFieldType;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.actions.EditAction;
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
@Title("Заказанные отчеты: изменение заказанного отчета")
@RunWith(Parameterized.class)
public class EditReportOrderTest {

    private static final UserSteps user = new UserSteps().withUser(REPORT_ORDER_USER);

    private static Long counterId;

    private Matcher<ReportOrder> matcher;

    private ReportOrder editedReportOrder;

    @Parameterized.Parameters(name = "Действие: {1}")
    public static Collection<Object[]> getParameters() {
        return of(
                toArray(getDefaultReportOrder(), getChangeNameAction(), anything()),
                toArray(getReportOrderWithSingleRecipientEmail(), getChangeSingleRecipientEmailAction(), anything()),
                toArray(getReportOrderWithMultipleRecipientEmails(), getChangeMultipleRecipientEmailsAction(), anything()),
                toArray(getSingleReportOrder(), getChangeSingleReportOrderDatesAction(), anything()),
                toArray(getWeeklyReportOrder(), getChangeRegularReportOrderFrequencyToMonthlyAction(),
                        hasProperty("endDate", localDateWithField(DateTimeFieldType.dayOfMonth(), equalTo(1)))
                )
        );
    }

    @Parameterized.Parameter
    public ReportOrder reportOrder;

    @Parameterized.Parameter(1)
    public EditAction<ReportOrder> editAction;

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
        ReportOrder createdReportOrder = user.onManagementSteps().onReportOrderSteps()
                .createReportOrder(counterId, reportOrder);

        reportOrder = editAction.edit(reportOrder);

        editedReportOrder = user.onManagementSteps().onReportOrderSteps()
                .editReportOrder(counterId, createdReportOrder.getId(), reportOrder);

        matcher = allOf(
                beanEquivalent(reportOrder),
                hasProperty("id", equalTo(createdReportOrder.getId())),
                hasProperty("ownerLogin", equalTo(createdReportOrder.getOwnerLogin())),
                hasProperty("createTime", equalTo(createdReportOrder.getCreateTime())),
                hasProperty("status", equalTo(ReportOrderStatus.ACTIVE)),
                additionalMatcher
        );
    }

    @Test
    public void testEdit() {
        assertThat("измененный заказанный отчет соответствует ожиданию", editedReportOrder, matcher);
    }

    @Test
    public void testGet() {
        ReportOrder receivedReportOrder = user.onManagementSteps().onReportOrderSteps()
                .getReportOrder(counterId, editedReportOrder.getId());

        assertThat("полученный заказанный отчет соответствует ожиданию", receivedReportOrder, matcher);
    }

    @AfterClass
    public static void cleanupClass() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
