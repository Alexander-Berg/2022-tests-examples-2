package ru.yandex.autotests.metrika.tests.b2b.metrika.presets.ecommerce;

import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bEcommerceTest;

import java.util.Collection;

import static java.util.stream.Collectors.toList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.Preset.ecommerce;

/**
 * Created by konkov on 28.09.2015.
 */
public abstract class BaseB2bEcommercePresetsTest extends BaseB2bEcommerceTest {

    @Parameterized.Parameter()
    public String preset;

    @Parameterized.Parameters(name = "{0}")
    public static Collection createParameters() {
        return userOnTest.onMetadataSteps().getPresetsMeta(ecommerce()).stream()
                .map(p -> toArray(p.getName()))
                .collect(toList());
    }
}
