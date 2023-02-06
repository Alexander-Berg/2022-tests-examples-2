package ru.yandex.autotests.metrika.tests.ft.report.webvisor.visitsgrid;

import com.google.common.collect.ImmutableList;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.WebvisorV2MetadataDefaultVisitDimensionsGETSchema;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static ch.lambdaj.Lambda.collect;
import static java.util.Arrays.asList;
import static org.apache.commons.collections4.ListUtils.union;

/**
 * Created by konkov on 09.12.2014.
 */
@Features(Requirements.Feature.WEBVISOR)
@Stories({Requirements.Story.WebVisor.VISITS_GRID})
@Title("Вебвизор: таблица визитов, обязательные атрибуты")
@RunWith(Parameterized.class)
public class VisitsGridRequireAttributesTest extends VisitsGridBaseTest {

    @Parameterized.Parameters(name = "Счетчик: {1}, измерения: {0}")
    public static Collection createParameters() {
        WebvisorV2MetadataDefaultVisitDimensionsGETSchema defaults = user.onWebVisorMetadataSteps()
                .getWebVisorDefaultVisitDimensions();

        return CombinatorialBuilder.builder()
                .values(ImmutableList.of(
                        defaults.getRequired(),
                        union(defaults.getRequired(), defaults.getFirstColumn()),
                        union(defaults.getRequired(), defaults.getDefaults()),
                        union(defaults.getRequired(), defaults.getPopup()),
                        union(defaults.getRequired(), defaults.getCustomDisplayed()),
                        collect(asList(
                                defaults.getRequired(),
                                defaults.getFirstColumn(),
                                defaults.getDefaults(),
                                defaults.getPopup()))))
                .values(COUNTERS)
                .build();
    }

}
