package ru.yandex.autotests.metrika.tests.b2b.metrika.presets.advertising;

import org.junit.BeforeClass;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ClientsParameters;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.tests.b2b.BaseB2bAdvertisingTest;
import ru.yandex.metrika.segments.site.parametrization.Attribution;

import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.Preset.table;

/**
 * Created by konkov on 30.07.2015.
 */
public abstract class BaseB2bAdvertisingPresetsTest extends BaseB2bAdvertisingTest {
    protected static List<String> directClientLogins;

    @BeforeClass
    public static void init() {
        directClientLogins = userOnTest.onManagementSteps().onClientSteps().getClientLogins(
                new ClientsParameters()
                        .withCounters(COUNTER.get(Counter.ID))
                        .withDate1(START_DATE)
                        .withDate2(END_DATE),
                ulogin(COUNTER.get(Counter.U_LOGIN)));
    }

    @Parameterized.Parameter()
    public String preset;

    @Parameterized.Parameter(1)
    public Attribution attribution;

    @Parameterized.Parameters(name = "preset: {0}, attribution: {1}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .values(userOnTest.onMetadataSteps().getPresetsRaw(table(TableEnum.ADVERTISING)))
                .values(Attribution.values())
                .build();
    }
}
