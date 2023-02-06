package ru.yandex.autotests.metrika.tests.ft.report.webvisor.visitsgrid.filter;

import com.google.common.collect.ImmutableList;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.Arrays.asList;

/**
 * Created by konkov on 10.12.2014.
 */
@Features(Requirements.Feature.WEBVISOR)
@Stories({Requirements.Story.WebVisor.VISITS_GRID})
@Title("Вебвизор: таблица визитов, фильтрация")
@RunWith(Parameterized.class)
public class VisitsGridFilterTest extends VisitsGridFilterBaseTest {

    @Parameterized.Parameters(name = "Счетчик: {1}, измерения: {0}")
    public static Collection createParameters() {
        return CombinatorialBuilder.builder()
                .values(user.onWebVisorMetadataSteps().getWebVisorVisitFilterableDimensions().stream()
                        .filter(d -> !ImmutableList.of(
                                "ym:s:labelsAggregated",
                                "ym:s:regionAggregated",
                                "ym:s:screenResolutionWV").contains(d)))
                .values(COUNTERS)
                .build();
    }
}
