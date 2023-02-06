package ru.yandex.autotests.metrika.tests.ft.report.metrika.presets;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.metadata.v1.PresetWrapper;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.stream.Collectors.toList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.Preset.*;

/**
 * Created by konkov on 03.09.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.PRESET})
@Title("Шаблоны отчетов по визитам")
@RunWith(Parameterized.class)
public class PresetVisitTest extends PresetBaseTest {

    @Parameterized.Parameters(name = "{0}")
    public static Collection<PresetWrapper[]> createParameters() {
        return user.onMetadataSteps()
                .getPresetsMeta(table(TableEnum.VISITS)
                        .and(ecommerce().negate())
                        .and(yan().negate())
                        .and(cdp().negate()))
                .stream()
                .map(p -> toArray(new PresetWrapper(p)))
                .collect(toList());
    }
}
