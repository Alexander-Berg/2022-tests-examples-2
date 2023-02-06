package ru.yandex.autotests.metrika.tests.ft.report.metrika.presets;

import org.junit.BeforeClass;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.metadata.v1.PresetWrapper;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ClientsParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static java.util.stream.Collectors.toList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.Preset.table;

/**
 * Created by konkov on 10.07.2015.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.PRESET})
@Title("Шаблоны отчетов по кликам Директа")
@RunWith(Parameterized.class)
public class PresetAdvertisingTest extends PresetBaseTest {

    private static final String START_DATE = DateConstants.Advertising.START_DATE;
    //запрос за 1 день
    private static final String END_DATE = DateConstants.Advertising.START_DATE;

    private static List<String> directClientLogins;

    @Parameterized.Parameters(name = "{0}")
    public static Collection createParameters() {
        return user.onMetadataSteps().getPresetsMeta(table(TableEnum.ADVERTISING)).stream()
                .map(p -> toArray(new PresetWrapper(p)))
                .collect(toList());

    }

    @BeforeClass
    public static void init() {
        directClientLogins = user.onManagementSteps().onClientSteps().getClientLogins(
                new ClientsParameters()
                        .withCounters(COUNTER_ADVERTISING.get(ID))
                        .withDate1(START_DATE)
                        .withDate2(END_DATE),
                ulogin(COUNTER_ADVERTISING.get(Counter.U_LOGIN)));
    }

    @Override
    protected TableReportParameters getReportParameters() {
        return super.getReportParameters()
                .withId(COUNTER_ADVERTISING)
                .withDate1(START_DATE)
                .withDate2(END_DATE)
                .withDirectClientLogins(directClientLogins);
    }
}
