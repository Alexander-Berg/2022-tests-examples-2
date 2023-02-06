package ru.yandex.autotests.metrika.tests.ft.report.metrika.presets;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.metadata.v1.PresetWrapper;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.stream.Collectors.toList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.Preset.table;

/**
 * Created by sonick on 23.03.16.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.PRESET})
@Title("Шаблоны отчета параметры пользователя")
@RunWith(Parameterized.class)
public class PresetUserParamsTest extends PresetBaseTest {

    @Parameterized.Parameters(name = "{0}")
    public static Collection createParameters() {
        return user.onMetadataSteps().getPresetsMeta(table(TableEnum.USER_PARAM)).stream()
                .map(p -> toArray(new PresetWrapper(p)))
                .collect(toList());
    }
    @Override
    protected TableReportParameters getReportParameters() {
        return new TableReportParameters()
                .withId(USER_PARAM_COUNTER.get(ID))
                .withPreset(parameter.getPreset().getName());
    }
}
