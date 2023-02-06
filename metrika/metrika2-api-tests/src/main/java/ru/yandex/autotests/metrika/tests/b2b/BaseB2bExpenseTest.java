package ru.yandex.autotests.metrika.tests.b2b;

import java.util.List;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ClientsParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ComparisonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;

import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_EXPENSES;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;

public abstract class BaseB2bExpenseTest extends BaseB2bTest {

    protected static final Counter COUNTER = TEST_EXPENSES;

    protected static final String START_DATE = DateConstants.Expense.START_DATE;
    protected static final String END_DATE = DateConstants.Expense.END_DATE;

    protected static final String START_DATE_B = DateConstants.Expense.START_DATE_B;
    protected static final String END_DATE_B = DateConstants.Expense.END_DATE_B;

    @Override
    protected void assumeOnResponses(Object testingBean, Object referenceBean) {
        super.assumeOnResponses(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeSuccessBoth(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeNotEmptyBoth(testingBean, referenceBean);
    }

    public static IFormParameters commonParameters() {
        return makeParameters()
                .append(ulogin(COUNTER.get(Counter.U_LOGIN)))
                .append(new CommonReportParameters()
                        .withId(COUNTER.get(Counter.ID))
                        .withDirectClientLogins(getClientLogins())
                );
    }

    public static IFormParameters dateParameters() {
        return new TableReportParameters()
                .withDate1(START_DATE)
                .withDate2(END_DATE);
    }

    public static IFormParameters comparisonDateParameters() {
        return new ComparisonReportParameters()
                .withDate1_a(START_DATE)
                .withDate2_a(END_DATE)
                .withDate1_b(START_DATE_B)
                .withDate2_b(END_DATE_B);
    }

    public static IFormParameters goalIdParameters() {
        return goalId(COUNTER);
    }

    private static List<String> getClientLogins() {
        return userOnTest.onManagementSteps().onClientSteps().getClientLogins(
                new ClientsParameters().withCounters(COUNTER.get(Counter.ID)),
                ulogin(COUNTER.get(Counter.U_LOGIN))
        );
    }
}
