package ru.yandex.autotests.metrika.tests.ft.report.webvisor.hitsgrid;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.WebvisorV2MetadataDefaultHitDimensionsGETSchema;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.lang.String.format;
import static java.util.Arrays.asList;
import static org.apache.commons.collections4.ListUtils.union;
import static ru.yandex.autotests.metrika.matchers.Matchers.iterableHasDimensionValuesFilledAllowNull;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

/**
 * Created by konkov on 10.12.2014.
 */
@Features(Requirements.Feature.WEBVISOR)
@Stories({Requirements.Story.WebVisor.HITS_GRID})
@Title("Вебвизор: таблица просмотров, доступные атрибуты")
@RunWith(Parameterized.class)
public class HitsGridAttributesTest extends HitsGridBaseTest {

    @Parameterized.Parameters(name = "Счетчик: {1}, измерения: {0}")
    public static Collection createParameters() {
        WebvisorV2MetadataDefaultHitDimensionsGETSchema defaults = user.onWebVisorMetadataSteps()
                .getWebVisorDefaultHitDimensions();

        List<String> dimensions = user.onWebVisorMetadataSteps().getWebVisorHitDimensions();

        List<List<String>> parameters = new ArrayList<>();

        for (String dimension : dimensions) {
            parameters.add(union(defaults.getRequired(), asList(dimension)));
        }

        return CombinatorialBuilder.builder()
                .values(parameters)
                .values(COUNTERS)
                .build();
    }

    @Test
    public void hitsGridAttributeTest() {
        String attributeName = dimensions.get(dimensions.size() - 1);
        List<String> dimensionValues = user.onResultSteps().getDimensionValues(attributeName, report);

        assertThat(format("поле %s заполнено", attributeName), dimensionValues,
                iterableHasDimensionValuesFilledAllowNull());
    }
}
