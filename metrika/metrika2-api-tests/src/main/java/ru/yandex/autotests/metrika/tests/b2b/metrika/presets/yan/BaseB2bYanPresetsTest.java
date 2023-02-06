package ru.yandex.autotests.metrika.tests.b2b.metrika.presets.yan;

import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bYanTest;

import java.util.Collection;

import static java.util.stream.Collectors.toList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.Preset.yan;

public class BaseB2bYanPresetsTest extends BaseB2bYanTest {

    @Parameterized.Parameter()
    public String preset;

    @Parameterized.Parameters(name = "{0}")
    public static Collection createParameters() {
        return userOnTest.onMetadataSteps().getPresetsMeta(yan()).stream()
                .map(p -> toArray(p.getName()))
                .collect(toList());
    }
}
