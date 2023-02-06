package ru.yandex.autotests.metrika.tests.ft.report.metrika.dimensions;

import java.util.Collection;
import java.util.List;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.data.common.DateConstants;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.common.counters.Counters;
import ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.management.v1.ClientsParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.CommonReportParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.ParametrizationParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static java.util.function.Function.identity;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.everyItem;
import static org.junit.runners.Parameterized.Parameter;
import static org.junit.runners.Parameterized.Parameters;
import static ru.yandex.autotests.irt.testutils.matchers.CompositeMatcher.matchEvery;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.U_LOGIN;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.DRESSTOP;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.IKEA_VSEM;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.KVAZI_KAZINO;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.TEST_EXPENSES;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum.ATTRIBUTION;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum.CURRENCY;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum.GOAL_ID;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.ParametrizationTypeEnum.GROUP;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.ADVERTISING;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.DOWNLOADS;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.EXPENSES_VISITS;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.EXTERNAL_LINKS;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.HITS;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.SHARE_SERVICES;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.SITE_SPEED;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.USER_PARAM;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.VISITS;
import static ru.yandex.autotests.metrika.data.parameters.management.v1.DelegateParameters.ulogin;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.ExperimentParameters.experimentId;
import static ru.yandex.autotests.metrika.data.parameters.report.v1.GoalIdParameters.goalId;
import static ru.yandex.autotests.metrika.matchers.Matchers.iterableHasDimensionValuesFilled;
import static ru.yandex.autotests.metrika.matchers.NoDuplicatesMatcher.hasNoDuplicates;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.addCurrencies;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.addGroups;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.setParameters;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.any;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.ecommerce;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.matches;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.parameterized;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.table;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.yan;
import static ru.yandex.autotests.metrika.utils.AllureUtils.addTestParameter;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;
import static ru.yandex.autotests.metrika.utils.Utils.aggregate;
import static ru.yandex.metrika.segments.site.parametrization.Attribution.LAST;

/**
 * Created by konkov on 15.08.2014.
 */
@Features({Requirements.LONG_RUNNING, Requirements.Feature.REPORT})
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.DIMENSIONS})
@Title("Отчет 'таблица': измерения")
@RunWith(Parameterized.class)
public class TableDimensionsTest {

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();

    private static final Counter COUNTER = IKEA_VSEM;
    private static final Counter USER_PARAM_COUNTER = Counters.YANDEX_METRIKA_2_0;
    private static final String START_DATE = "2015-06-20";
    private static final String END_DATE = "2015-06-21";

    private static final Counter ADVERTISING_COUNTER = DRESSTOP;
    private static final String ADVERTISING_START_DATE = DateConstants.Advertising.START_DATE;
    private static final String ADVERTISING_END_DATE = DateConstants.Advertising.END_DATE;

    private static final Counter EXPENSE_COUNTER = TEST_EXPENSES;
    private static final String EXPENSE_START_DATE = DateConstants.Expense.START_DATE;
    private static final String EXPENSE_END_DATE = DateConstants.Expense.END_DATE;

    private static final String VISIT_METRIC = "ym:s:visits";
    private static final String HIT_METRIC = "ym:pv:pageviews";
    private static final String SHARE_SERVICES_METRIC = "ym:sh:shares";
    private static final String SITE_SPEED_METRIC = "ym:sp:pageviews";
    private static final String EXTERNAL_LINKS_METRIC = "ym:el:links";
    private static final String DOWNLOADS_METRIC = "ym:dl:downloads";
    private static final String ADVERTISING_METRIC = "ym:ad:clicks";
    private static final String USER_PARAM_METRIC = "ym:up:params";
    private static final String EXPENSE_METRIC = "ym:ev:expenses<currency>";


    @Parameter()
    public String dimensionName;

    @Parameter(value = 1)
    public FreeFormParameters tail;

    @Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        //перебираем измерения
        return MultiplicationBuilder.<String, String, FreeFormParameters>builder(
                user.onMetadataSteps().getDimensions(any()),
                FreeFormParameters::makeParameters)
                //параметры, общие для всех измерений
                .apply(any(), setParameters(
                        new TableReportParameters()
                                .withId(COUNTER.get(ID))
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)))
                .apply(table(VISITS), setParameters(
                        new TableReportParameters().withMetric(VISIT_METRIC)))
                .apply(table(HITS), setParameters(
                        new TableReportParameters().withMetric(HIT_METRIC)))
                .apply(table(SHARE_SERVICES), setParameters(
                        new TableReportParameters().withMetric(SHARE_SERVICES_METRIC)))
                .apply(table(SITE_SPEED), setParameters(
                        new TableReportParameters().withMetric(SITE_SPEED_METRIC)))
                .apply(table(EXTERNAL_LINKS), setParameters(
                        new TableReportParameters().withMetric(EXTERNAL_LINKS_METRIC)))
                .apply(table(DOWNLOADS), setParameters(
                        new TableReportParameters().withMetric(DOWNLOADS_METRIC)))
                .apply(table(USER_PARAM), setParameters(
                        new TableReportParameters()
                                .withId(USER_PARAM_COUNTER)
                                .withMetric(USER_PARAM_METRIC)))
                .apply(table(ADVERTISING), setParameters(
                        new TableReportParameters()
                                .withId(ADVERTISING_COUNTER)
                                .withMetric(ADVERTISING_METRIC)
                                .withDate1(ADVERTISING_START_DATE)
                                .withDate2(ADVERTISING_END_DATE)
                                .withDirectClientLogins(
                                        user.onManagementSteps().onClientSteps().getClientLogins(
                                                new ClientsParameters()
                                                        .withCounters(ADVERTISING_COUNTER.get(ID))
                                                        .withDate1(ADVERTISING_START_DATE)
                                                        .withDate2(ADVERTISING_END_DATE),
                                                ulogin(ADVERTISING_COUNTER.get(U_LOGIN))))))
                .apply(table(EXPENSES_VISITS), setParameters(
                        new TableReportParameters()
                                .withId(EXPENSE_COUNTER)
                                .withMetric(EXPENSE_METRIC)
                                .withDate1(EXPENSE_START_DATE)
                                .withDate2(EXPENSE_END_DATE)))
                //для ecommerce свои даты и счетчик
                .apply(ecommerce(), setParameters(
                        new TableReportParameters()
                                .withId(Counters.ECOMMERCE_TEST)
                                .withDate1(DateConstants.Ecommerce.START_DATE)
                                .withDate2(DateConstants.Ecommerce.END_DATE)
                                .withAccuracy("1")))
                //для РСЯ свои даты и счетчик
                .apply(yan(), setParameters(
                        new TableReportParameters()
                                .withId(Counters.YANDEX_NEWS)
                                .withDate1(DateConstants.Yan.START_DATE)
                                .withDate2(DateConstants.Yan.END_DATE)
                                .withAccuracy("0.1")))
                //подставим goal_id
                .apply(parameterized(GOAL_ID), setParameters(goalId(COUNTER)))
                .apply(parameterized(GOAL_ID).and(ecommerce()),
                        setParameters(goalId(Counters.ECOMMERCE_TEST)))
                .apply(parameterized(ParametrizationTypeEnum.EXPERIMENT), setParameters(aggregate(
                        new CommonReportParameters().withId(KVAZI_KAZINO), experimentId(KVAZI_KAZINO))))
                .apply(table(ADVERTISING).and(parameterized(GOAL_ID)),
                        setParameters(goalId(ADVERTISING_COUNTER)))
                //подставим атрибуцию
                .apply(parameterized(ATTRIBUTION), setParameters(
                        new ParametrizationParameters().withAttribution(LAST)))
                //размножим по всем валютам
                .apply(parameterized(CURRENCY), addCurrencies())
                //размножим по всем периодам группировки
                .apply(parameterized(GROUP), addGroups())
                .apply(matches(equalTo("ym:s:networkType")), setParameters(
                        new TableReportParameters()
                                .withDate1("2017-01-20")
                                .withDate2("2017-01-21")))
                .apply(matches(containsString("DirectBanner"))
                        .or(matches(containsString("directBanner")))
                        .or(matches(containsString("DirectPhraseOrCond")))
                        .or(matches(containsString("DirectPlatform"))), setParameters(
                        new TableReportParameters()
                                .withAccuracy("0.001")
                                .withDate1("2016-03-01")
                                .withDate2("2016-03-01")))
                .build(identity());
    }

    private StatV1DataGETSchema result;

    @Before
    public void setup() {
        addTestParameter("Измерение", dimensionName);

        result = user.onReportSteps().getTableReportAndExpectSuccess(
                new TableReportParameters().withDimension(dimensionName),
                tail);
    }

    @Test
    public void checkDimensionValuesValidityAndUniqueness() {
        List<List<String>> dimensions = user.onResultSteps().getDimensions(result);

        assertThat("значения измерений не содержат пустых и некорректных значений, а также дубликатов", dimensions,
                matchEvery(everyItem(iterableHasDimensionValuesFilled()), hasNoDuplicates()));
    }
}
