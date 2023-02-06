package ru.yandex.autotests.topsites.api.tests;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.joda.time.YearMonth;
import org.junit.Test;

import ru.yandex.autotests.topsites.steps.UserSteps;
import ru.yandex.metrika.api.topsites.snapshot.ReportPeriod;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Title;
import ru.yandex.topsites.GlobalTopsitesReport2PeriodsAvailableGETSchema;

import static org.hamcrest.Matchers.everyItem;
import static org.hamcrest.Matchers.hasProperty;
import static org.hamcrest.Matchers.iterableWithSize;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.topsites.api.TopSitesFeatures.GENERAL;
import static ru.yandex.autotests.topsites.core.TopSitesMatchers.isPeriodOfWholeMonthOrWindowSize;

@Features(GENERAL)
@Title("Проверка ручки доступных периодов")
public class ReportPeriodsAvailableTest {

    private static final UserSteps userSteps = new UserSteps();

    private final static int WINDOW_SIZE = 29;

    @Test
    @Title("start и end верны v2")
    public void formatV2() {
        GlobalTopsitesReport2PeriodsAvailableGETSchema periodsAvailable = userSteps.onTopSitesSteps().getPeriodsAvailable2();
        assertThat("Периоды содержат корректные данные", periodsAvailable.getData(),
                everyItem(isPeriodOfWholeMonthOrWindowSize(WINDOW_SIZE)));
    }

    @Test
    @Title("Для каждого месяца есть только один период v2")
    public void onePeriodForMonthV2() {
        GlobalTopsitesReport2PeriodsAvailableGETSchema periodsAvailable = userSteps.onTopSitesSteps().getPeriodsAvailable2();
        Map<Object, List<ReportPeriod>> byMonth =
                periodsAvailable.getData().stream().filter(rp -> rp.getMonth() != null)
                        .collect(Collectors.groupingBy(ReportPeriod::getMonth));
        assertThat("Месяц есть у тех, у кого должен", byMonth.entrySet(), everyItem(hasProperty("value", iterableWithSize(1))));
    }
}
