package ru.yandex.autotests.metrika.tests.b2b.metrika.export;

import java.util.Collection;

import org.junit.Before;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.metadata.v1.PresetWrapper;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ExperimentParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.metrika.api.constructor.presets.PresetExternal;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.KVAZI_KAZINO;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_CDP;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_MARKET;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_NEWS;
import static ru.yandex.autotests.metrika.data.common.handles.RequestTypes.TABLE;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.HITS;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.VISITS;
import static ru.yandex.autotests.metrika.data.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.setParameters;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.Preset.cdp;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.Preset.ecommerce;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.Preset.experimentAB;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.Preset.table;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.Preset.vacuum;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.Preset.yan;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.any;

/**
 * Created by sourx on 27/06/16.
 */
@Features(Requirements.Feature.DATA)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Format.CSV,
        Requirements.Story.Report.Format.CSV})
@Title("B2B - Экспорт отчета 'таблица' в excel")
@RunWith(Parameterized.class)
public class B2bExportTableTest extends BaseB2bExportTest {
    private static final Counter COUNTER = YANDEX_MARKET;
    private static final Counter COUNTER_ECOMMERCE = Counters.ECOMMERCE_TEST;

    private static final String START_DATE = "2016-04-15";
    private static final String END_DATE = "2016-04-15";

    private static final String START_DATE_ECOMMERCE = DateConstants.Ecommerce.START_DATE;
    private static final String END_DATE_ECOMMERCE = DateConstants.Ecommerce.END_DATE;

    private static final String START_DATE_YAN = DateConstants.Yan.START_DATE;
    private static final String END_DATE_YAN = DateConstants.Yan.END_DATE;

    @Parameter()
    public PresetWrapper preset;

    @Parameter(1)
    public FreeFormParameters tail;

    @Parameters(name = "preset: \"{0}\"")
    public static Collection createParameters() {
        return MultiplicationBuilder.<PresetExternal, PresetWrapper, FreeFormParameters>builder(
                userOnTest.onMetadataSteps().getPresetsMeta(table(HITS).or(table(VISITS))),
                FreeFormParameters::makeParameters)
                .apply(any(), setParameters(new TableReportParameters()
                        .withId(COUNTER)
                        .withDate1(START_DATE)
                        .withDate2(END_DATE)
                        .withAccuracy("0.1")))
                .apply(ecommerce(), setParameters(new TableReportParameters()
                        .withId(COUNTER_ECOMMERCE)
                        .withDate1(START_DATE_ECOMMERCE)
                        .withDate2(END_DATE_ECOMMERCE)))
                .apply(yan(), setParameters(new TableReportParameters()
                        .withId(YANDEX_NEWS)
                        .withDate1(START_DATE_YAN)
                        .withDate2(END_DATE_YAN)
                        .withAccuracy("0.1")))
                .apply(vacuum(), setParameters(
                        new TableReportParameters()
                                .withId(Counters.YANDEX_EATS_ON_MAPS)
                                .withAccuracy("1")
                                .withDate1(DateConstants.Vacuum.START_DATE)
                                .withDate2(DateConstants.Vacuum.END_DATE)))
                .apply(experimentAB(), setParameters(makeParameters()
                        .append(new TableReportParameters()
                                .withId(KVAZI_KAZINO)
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)
                                .withAccuracy("0.1"))
                        .append(ExperimentParameters.experimentId(KVAZI_KAZINO))))
                .apply(cdp(), setParameters(
                        new TableReportParameters()
                                .withId(TEST_CDP)
                                .withAccuracy("1")
                                .withDate1(DateConstants.Cdp.START_DATE)
                                .withDate2(DateConstants.Cdp.END_DATE)))
                .build(PresetWrapper::new);
    }

    @Before
    public void setup() {
        requestType = TABLE;
        reportParameters = tail.append(new TableReportParameters()
                .withPreset(preset.getPreset().getName()));
    }
}
