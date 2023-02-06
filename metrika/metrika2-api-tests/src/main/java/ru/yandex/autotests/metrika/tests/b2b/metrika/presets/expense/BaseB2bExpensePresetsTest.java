package ru.yandex.autotests.metrika.tests.b2b.metrika.presets.expense;

import java.util.Collection;

import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bExpenseTest;

import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.Preset.table;

public abstract class BaseB2bExpensePresetsTest extends BaseB2bExpenseTest {

    @Parameterized.Parameter
    public String preset;

    @Parameterized.Parameters(name = "Пресет: {0}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .values(userOnTest.onMetadataSteps().getPresetsRaw(table(TableEnum.EXPENSES_VISITS)))
                .build();
    }
}
