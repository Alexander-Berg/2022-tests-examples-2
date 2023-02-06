package ru.yandex.autotests.metrika.tests.ft.report.metrika.filters.table;

import java.util.Collection;
import java.util.List;
import java.util.function.Predicate;
import java.util.stream.Stream;

import com.google.common.collect.ImmutableList;
import org.apache.commons.lang3.ArrayUtils;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;

import ru.yandex.autotests.irt.testutils.beandiffer.beanconstraint.BeanConstraint;
import ru.yandex.autotests.irt.testutils.beandiffer.beanconstraint.BeanConstraints;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.commons.junitparams.MultiplicationBuilder;
import ru.yandex.autotests.metrika.commons.rules.IgnoreParameters;
import ru.yandex.autotests.metrika.commons.rules.ParametersIgnoreRule;
import ru.yandex.autotests.metrika.data.common.counters.Counter;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.filters.Term;
import ru.yandex.autotests.metrika.properties.MetrikaApiProperties;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.constructor.response.DimensionMetaExternal;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import static org.apache.commons.lang3.ArrayUtils.toArray;
import static org.hamcrest.Matchers.greaterThan;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.irt.testutils.beandiffer.BeanDifferMatcher.beanEquivalent;
import static ru.yandex.autotests.metrika.data.common.counters.Counter.ID;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.IKEA_VSEM;
import static ru.yandex.autotests.metrika.data.metadata.v1.enums.TableEnum.VISITS;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Modifiers.setParameters;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.any;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.dimension;
import static ru.yandex.autotests.metrika.steps.metadata.MetadataSteps.Predicates.table;

/**
 * этот тест должен проверять следующее соображение:
 * пусть
 * - есть измерение dimId, которое имеет в качестве дополнительного атрибута name измерение dimName.
 * - если измерение dimId принимает значение А, то измерение dimName принимает некоторое значение B.
 * тогда ответ апи с фильтрами dimId==A и dimName==B должны совпадать.
 * <p>
 * вероятность того, что эти фильтры будут по-разному эквивалентны в table и в не table, невелика, поэтому здесь.
 * Created by orantius on 20.10.16.
 */
@Features(Requirements.Feature.REPORT)
@Stories({Requirements.Story.Report.Type.TABLE, Requirements.Story.Report.Parameter.FILTERS})
@Title("Фильтры: фильтры по расшифрованным id")
@RunWith(Parameterized.class)
public class TableFilterIdNameTest {

    @Rule
    public final ParametersIgnoreRule ignoreRule = new ParametersIgnoreRule(true);

    private static final Counter COUNTER = IKEA_VSEM;
    private static final String START_DATE = "2017-01-20";
    private static final String END_DATE = "2017-01-21";
    private static final String VISIT_METRIC = "ym:s:visits";

    private static final UserSteps user = new UserSteps().withDefaultAccuracy();

    @Parameterized.Parameter()
    public DimensionHolder pairOfIdName;

    @Parameterized.Parameter(value = 1)
    public FreeFormParameters tail;

    private String filterId;
    private String filterName;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> createParameters() {
        //перебираем измерения
        return MultiplicationBuilder.<DimensionMetaExternal, DimensionHolder, FreeFormParameters>builder(
                user.onMetadataSteps().getDimensionsMeta(dimension(table(VISITS)).and(allKeysPresent("id", "name"))),
                FreeFormParameters::new)
                .apply(any(), setParameters(
                        new TableReportParameters()
                                .withId(COUNTER.get(ID))
                                .withDate1(START_DATE)
                                .withDate2(END_DATE)
                                .withMetric(VISIT_METRIC)
                ))
                .build(m -> DimensionHolder.from(m));
    }

    public static class DimensionHolder {
        private final String id;

        private final String name;

        public DimensionHolder(String id, String name) {
            this.id = id;
            this.name = name;
        }

        public String getId() {
            return id;
        }

        public String getName() {
            return name;
        }

        @Override
        public String toString() {
            return id + " " + name;
        }

        public static DimensionHolder from(DimensionMetaExternal dimension) {
            return new DimensionHolder(
                    dimension.getFields().get("id").getDim(),
                    dimension.getFields().get("name").getDim());
        }
    }

    @Before
    public void setup() {
        StatV1DataGETSchema response = user.onReportSteps().getTableReportAndExpectSuccess(
                new TableReportParameters()
                        .withDimension(pairOfIdName.getId())
                        .withLimit(1)
                        .withId(COUNTER.get(ID))
                        .withMetric(VISIT_METRIC)
                        .withDate1(START_DATE)
                        .withDate2(END_DATE));

        int rows = user.onResultSteps().getDimensions(response).size();

        assumeThat("Недостаточно данных для проведения проверки", rows, greaterThan(0));

        String value = user.onResultSteps().getDimensions(response).get(0).get(0);
        filterId = Term.dimension(pairOfIdName.getId()).equalTo(value).build();

        String valueName = user.onResultSteps().getDimensionsOnlyName(response).get(0).get(0);
        filterName = Term.dimension(pairOfIdName.getName()).equalTo(valueName).build();
    }

    @Test
    @IgnoreParameters(reason = "unsupported", tag = "ignored")
    public void check() {
        StatV1DataGETSchema resultId = user.onReportSteps().getTableReportAndExpectSuccess(
                new TableReportParameters()
                        .withDimension(pairOfIdName.getId())
                        .withFilters(filterId),
                tail);

        // измерение одинаковое чтобы ответ был максимально похожим.
        StatV1DataGETSchema resultName = user.onReportSteps().getTableReportAndExpectSuccess(
                new TableReportParameters()
                        .withDimension(pairOfIdName.getId())
                        .withFilters(filterName),
                tail);

        assertThat("ответы совпадают", resultName, beanEquivalent(resultId)
                .fields(ignore()));
    }

    private BeanConstraint ignore() {
        return BeanConstraints.ignore(
                ArrayUtils.addAll(
                        MetrikaApiProperties.getInstance().getDefaultIgnoredFields(),
                        "query/filters",
                        "query/humanizedFilter"));
    }

    private static Predicate<DimensionMetaExternal> allKeysPresent(String... keys) {
        return d -> Stream.of(keys).allMatch(k -> d.getFields() != null ? d.getFields().containsKey(k) : false);
    }

    @IgnoreParameters.Tag(name = "ignored")
    public static Collection<Object[]> ignoreParameters() {
        return ImmutableList.of(
                toArray((Predicate<DimensionHolder>) p -> IGNORED.contains(p.getId()), any()));
    }

    private static final List<String> IGNORED = ImmutableList.of(
            "ym:s:<attribution>DirectPlatform",
            "ym:s:firstDirectPlatform",
            "ym:s:lastSignDirectPlatform",
            "ym:s:lastDirectPlatform",
            "ym:s:experimentAB<experiment_ab>",
            "ym:s:datePeriod<group>",
            "ym:s:firstVisitDatePeriod<group>",
            "ym:s:moscowDatePeriod<group>",
            "ym:s:previousVisitDatePeriod<group>",
            "ym:s:browserDatePeriod<group>"
    );
}
