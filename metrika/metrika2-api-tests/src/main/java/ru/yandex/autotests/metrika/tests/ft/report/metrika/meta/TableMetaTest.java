package ru.yandex.autotests.metrika.tests.ft.report.metrika.meta;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import ru.yandex.autotests.metrika.Requirements;
import ru.yandex.autotests.metrika.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.commons.junitparams.combinatorial.CombinatorialBuilder;
import ru.yandex.autotests.metrika.data.parameters.report.v1.TableReportParameters;
import ru.yandex.autotests.metrika.steps.UserSteps;
import ru.yandex.metrika.api.constructor.response.DimensionMetaExternal;
import ru.yandex.metrika.api.constructor.response.Meta;
import ru.yandex.metrika.api.constructor.response.MetricMetaExternal;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.allure.annotations.Title;

import java.util.Collection;
import java.util.List;

import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static ru.yandex.autotests.metrika.data.common.counters.Counters.YANDEX_METRIKA_2_0;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assertThat;

@Features({Requirements.Feature.REPORT})
@Stories({Requirements.Story.Report.METADATA,
        Requirements.Story.Report.Parameter.METRICS, Requirements.Story.Report.Parameter.DIMENSIONS})
@Title("Отчет 'таблица' с метаданными: проверка информации о секретности данных в отчете")
@RunWith(Parameterized.class)
public class TableMetaTest {

    private static final String START_DATE = "2017-03-01";
    private static final String END_DATE = "2017-03-10";

    @Parameterized.Parameter()
    public ExpectedMetric expectedMetric;

    @Parameterized.Parameter(1)
    public ExpectedDimension expectedDimension;


    private final UserSteps user = new UserSteps().withDefaultAccuracy();

    @Parameterized.Parameters(name = "Метрика {0}, группировка {1}")
    public static Collection<Object[]> createParameters() {
        return CombinatorialBuilder.builder()
                .values(new ExpectedMetric("ym:s:robotPercentage", true, false),
                        new ExpectedMetric("ym:s:sumParams", false, true),
                        new ExpectedMetric("ym:s:visits", false, false))
                .values(new ExpectedDimension("ym:s:cookieEnabled", false, false),
                        new ExpectedDimension("ym:s:gender", true, false),
                        new ExpectedDimension("ym:s:startURLHash", false, true))
                .build();
    }


    @Test
    public void checkSensitivity() {
        StatV1DataGETSchema report = user.onReportSteps().getTableReportAndExpectSuccess(
                new TableReportParameters()
                        .withId(YANDEX_METRIKA_2_0)
                        .withMetric(expectedMetric.metric)
                        .withDimension(expectedDimension.dimension)
                        .withDate1(START_DATE)
                        .withDate2(END_DATE)
        );
        Meta meta = report.getMeta();

        checkMetrics(meta.getMetrics());
        checkDimensions(meta.getDimensions());
    }

    private void checkMetrics(List<MetricMetaExternal> metricsMeta) {
        assertThat("ровно одна метрика", metricsMeta, hasSize(1));
        MetricMetaExternal metricMeta = metricsMeta.get(0);
        assertThat(
                "метрика содержит секретные данные",
                metricMeta.getSecret(), equalTo(expectedMetric.isSecret)
        );

        assertThat(
                "метрика раскрывает секретные данные",
                metricMeta.getExposesSecretData(), equalTo(expectedMetric.exposesSecretData)
        );
    }


    private void checkDimensions(List<DimensionMetaExternal> dimensionsMeta) {
        assertThat("ровно одна группировка", dimensionsMeta, hasSize(1));
        DimensionMetaExternal dimensionMeta = dimensionsMeta.get(0);
        assertThat(
                "группировка содержит секретные данные",
                dimensionMeta.getSecret(), equalTo(expectedDimension.isSecret)
        );

        assertThat(
                "группировка раскрывает секретные данные",
                dimensionMeta.getExposesSecretData(), equalTo(expectedDimension.exposesSecretData)
        );
    }

    static private class ExpectedMetric {
        public String metric;
        public boolean isSecret;
        public boolean exposesSecretData;

        public ExpectedMetric(String metric, boolean isSecret, boolean exposesSecretData) {
            this.metric = metric;
            this.isSecret = isSecret;
            this.exposesSecretData = exposesSecretData;
        }

        @Override
        public String toString() {
            return "ExpectedMetric{" +
                    "metric='" + metric + '\'' +
                    ", isSecret=" + isSecret +
                    ", exposesSecretData=" + exposesSecretData +
                    '}';
        }
    }

    static private class ExpectedDimension {
        public String dimension;
        public boolean isSecret;
        public boolean exposesSecretData;

        public ExpectedDimension(String dimension, boolean isSecret, boolean exposesSecretData) {
            this.dimension = dimension;
            this.isSecret = isSecret;
            this.exposesSecretData = exposesSecretData;
        }

        @Override
        public String toString() {
            return "ExpectedDimension{" +
                    "dimension='" + dimension + '\'' +
                    ", isSecret=" + isSecret +
                    ", exposesSecretData=" + exposesSecretData +
                    '}';
        }
    }

}
