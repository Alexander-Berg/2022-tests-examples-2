package ru.yandex.autotests.metrika.tests.ft.management.reportorder;

import org.joda.time.LocalDate;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.management.client.external.reportorder.ReportOrderFrequency;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import static org.hamcrest.Matchers.*;
import static ru.yandex.autotests.metrika.tests.ft.management.ManagementTestData.getDefaultCounter;
import static ru.yandex.autotests.metrika.tests.ft.management.reportorder.ReportOrderManagementTestData.REPORT_ORDER_USER;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * @author zgmnkv
 */
@Features(Requirements.Feature.MANAGEMENT)
@Stories(Requirements.Story.Management.REPORT_ORDER)
@Title("Заказанные отчеты: получение дат окончаний отчетов в зависимости от регулярности")
public class GetReportOrderEndDatesTest {

    private static final UserSteps user = new UserSteps().withUser(REPORT_ORDER_USER);

    private Long counterId;

    @Before
    public void init() {
        counterId = user.onManagementSteps().onCountersSteps()
                .addCounterAndExpectSuccess(getDefaultCounter())
                .getId();
    }

    @Test
    public void test() {
        Map<ReportOrderFrequency, LocalDate> endDates = user.onManagementSteps().onReportOrderSteps()
                .getReportOrderEndDates(counterId);

        assertThat("даты окончаний соответствуют ожиданию", endDates,
               allOf(Stream.of(ReportOrderFrequency.values())
                       .map(frequency -> hasEntry(equalTo(frequency), greaterThan(LocalDate.now())))
                       .collect(Collectors.toList())
               )
        );
    }

    @After
    public void cleanup() {
        user.onManagementSteps().onCountersSteps()
                .deleteCounterAndIgnoreStatus(counterId);
    }
}
