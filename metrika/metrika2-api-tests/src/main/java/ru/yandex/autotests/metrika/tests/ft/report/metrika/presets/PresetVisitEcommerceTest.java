package ru.yandex.autotests.metrika.tests.ft.report.metrika.presets;

import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.metadata.v1.PresetWrapper;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;

import static java.util.stream.Collectors.toList;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.ECOMMERCE_TEST;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.VISITS;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.Preset.ecommerce;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.Preset.table;

/**
 * Created by konkov on 03.09.2014.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.PRESET})
@Title("Шаблоны отчетов по визитам, ecommerce")
@RunWith(Parameterized.class)
public class PresetVisitEcommerceTest extends PresetBaseTest {

    private static final Counter COUNTER_ECOMMERCE = ECOMMERCE_TEST;
    private static final String START_DATE_ECOMMERCE = DateConstants.Ecommerce.START_DATE;
    private static final String END_DATE_ECOMMERCE = DateConstants.Ecommerce.END_DATE;

    @Parameters(name = "{0}")
    public static Collection createParameters() {
        return user.onMetadataSteps().getPresetsMeta(table(VISITS).and(ecommerce())).stream()
                .map(p -> toArray(new PresetWrapper(p)))
                .collect(toList());
    }

    @Override
    protected TableReportParameters getReportParameters() {
        return super.getReportParameters()
                .withId(COUNTER_ECOMMERCE.get(ID))
                .withDate1(START_DATE_ECOMMERCE)
                .withDate2(END_DATE_ECOMMERCE);
    }
}
