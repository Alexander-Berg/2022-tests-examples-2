package ru.yandex.autotests.metrika.tests.ft.report.webvisor.hitsgrid;

import com.google.common.collect.ImmutableList;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.WebvisorV2MetadataDefaultHitDimensionsGETSchema;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static org.apache.commons.collections4.ListUtils.union;

/**
 * Created by konkov on 09.12.2014.
 */
@Features(Requirements.Feature.WEBVISOR)
@Stories({Requirements.Story.WebVisor.HITS_GRID})
@Title("Вебвизор: таблица просмотров, обязательные атрибуты")
@RunWith(Parameterized.class)
public class HitsGridRequiredAttributesTest extends HitsGridBaseTest {

    @Parameterized.Parameters(name = "Счетчик: {1}, измерения: {0}")
    public static Collection createParameters() {
        WebvisorV2MetadataDefaultHitDimensionsGETSchema defaults = user.onWebVisorMetadataSteps()
                .getWebVisorDefaultHitDimensions();

        return CombinatorialBuilder.builder()
                .values(ImmutableList.of(
                        defaults.getRequired(),
                        union(defaults.getRequired(), defaults.getDefaults())))
                .values(COUNTERS)
                .build();
    }

}
