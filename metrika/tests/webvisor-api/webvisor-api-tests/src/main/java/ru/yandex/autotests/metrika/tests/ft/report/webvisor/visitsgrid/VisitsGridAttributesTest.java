package ru.yandex.autotests.metrika.tests.ft.report.webvisor.visitsgrid;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.WebvisorV2MetadataDefaultVisitDimensionsGETSchema;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static freemarker.template.utility.Collections12.singletonList;
import static java.lang.String.format;
import static java.util.Arrays.asList;
import static org.apache.commons.collections4.ListUtils.union;
import static ru.yandex.autotests.metrika.matchers.Matchers.iterableHasDimensionValuesFilledAllowNullOrEmpty;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 09.12.2014.
 */
@Features(Requirements.Feature.WEBVISOR)
@Stories({Requirements.Story.WebVisor.VISITS_GRID})
@Title("Вебвизор: таблица визитов, доступные атрибуты")
@RunWith(Parameterized.class)
public class VisitsGridAttributesTest extends VisitsGridBaseTest {

    @Parameterized.Parameters(name = "Счетчик: {1}, измерения: {0}")
    public static Collection createParameters() {
        WebvisorV2MetadataDefaultVisitDimensionsGETSchema defaults = user.onWebVisorMetadataSteps()
                .getWebVisorDefaultVisitDimensions();

        List<String> dimensions = user.onWebVisorMetadataSteps().getWebVisorVisitDimensions();

        List<List<String>> parameters = new ArrayList<>();

        for (String dimension : dimensions) {
            parameters.add(union(defaults.getRequired(), asList(dimension)));
        }

        return CombinatorialBuilder.builder()
                .values(dimensions.stream()
                        .map(dimension -> union(defaults.getRequired(), singletonList(dimension))))
                .values(COUNTERS)
                .build();
    }

    @Test
    public void visitsGridAttributeTest() {
        String attributeName = dimensions.get(dimensions.size() - 1);
        List<String> dimensionValues = user.onResultSteps().getDimensionValues(attributeName, report);

        assertThat(format("поле %s заполнено", attributeName), dimensionValues,
                iterableHasDimensionValuesFilledAllowNullOrEmpty());
    }
}
