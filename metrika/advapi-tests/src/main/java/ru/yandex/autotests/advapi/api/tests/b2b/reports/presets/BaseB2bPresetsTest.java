package ru.yandex.autotests.advapi.api.tests.b2b.reports.presets;

import org.junit.runners.Parameterized;
import ru.yandex.autotests.advapi.api.tests.b2b.reports.BaseB2bTest;
import ru.yandex.autotests.advapi.data.metadata.PresetWrapper;
import ru.yandex.autotests.advapi.data.metadata.TableEnum;

import java.util.Collection;

import static java.util.stream.Collectors.toList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.advapi.steps.report.MetadataSteps.Predicates.Preset.table;

/**
 * Created by omaz on 05.12.2014.
 */
public abstract class BaseB2bPresetsTest extends BaseB2bTest {

    @Parameterized.Parameter()
    public PresetWrapper preset;

    @Parameterized.Parameters(name = "{0}")
    public static Collection createParameters() {
        return userOnTest.onMetadataSteps().getPresetsMeta(table(TableEnum.EVENTS)).stream()
                .map(p -> toArray(new PresetWrapper(p)))
                .collect(toList());
    }

    @Override
    protected void assumeOnResponses(Object testingBean, Object referenceBean) {
        super.assumeOnResponses(testingBean, referenceBean);
        userOnTest.onResultSteps().assumeSuccessBoth(testingBean, referenceBean);
    }
}
