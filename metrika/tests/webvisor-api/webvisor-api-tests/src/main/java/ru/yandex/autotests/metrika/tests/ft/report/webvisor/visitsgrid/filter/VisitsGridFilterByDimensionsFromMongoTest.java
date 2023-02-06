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
 * Created by konkov on 22.12.2014.
 */
@Features(Requirements.Feature.WEBVISOR)
@Stories({Requirements.Story.WebVisor.VISITS_GRID})
@Title("Вебвизор: таблица визитов, фильтрация по измерениям из mongodb")
@RunWith(Parameterized.class)
public class VisitsGridFilterByDimensionsFromMongoTest extends VisitsGridFilterBaseTest {

    @Parameterized.Parameters(name = "Счетчик: {1}, измерения: {0}")
    public static Collection createParameters() {
        return CombinatorialBuilder.builder()
                .values(ImmutableList.of(
                        "ym:s:webVisorViewed",
                        "ym:s:webVisorSelected"))
                .values(COUNTERS)
                .build();
    }
}
