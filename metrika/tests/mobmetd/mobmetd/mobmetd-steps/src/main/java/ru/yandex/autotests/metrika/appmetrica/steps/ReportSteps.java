package ru.yandex.autotests.metrika.appmetrica.steps;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.*;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.mobmet.model.ApplicationActivity;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;
import java.util.List;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.RESTRICT;
import static ru.yandex.autotests.metrika.appmetrica.utils.Utils.aggregate;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;

/**
 * Created by konkov on 04.05.2016.
 */
public class ReportSteps extends AppMetricaBaseSteps {

    public ReportSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить отчет 'таблица'")
    @ParallelExecution(RESTRICT)
    public StatV1DataGETSchema getTableReport(IFormParameters... parameters) {
        return get(StatV1DataGETSchema.class, "stat/v1/data", parameters);
    }

    @Step("Получить отчет 'drill down'")
    @ParallelExecution(RESTRICT)
    public StatV1DataDrilldownGETSchema getDrillDownReport(IFormParameters... parameters) {
        return get(StatV1DataDrilldownGETSchema.class, "stat/v1/data/drilldown", parameters);
    }

    @Step("Получить отчет 'по времени'")
    @ParallelExecution(RESTRICT)
    public StatV1DataBytimeGETSchema getByTimeReport(IFormParameters... parameters) {
        return get(StatV1DataBytimeGETSchema.class, "stat/v1/data/bytime", parameters);
    }

    @Step("Получить данные по активности для приложений {0}")
    @ParallelExecution(RESTRICT)
    public List<ApplicationActivity> getActivities(IFormParameters... parameters) {
        return getActivities(SUCCESS_MESSAGE, expectSuccess(), parameters).getData();
    }

    @Step("Получить данные в виде дерева")
    @ParallelExecution(RESTRICT)
    public StatV1SegmentTreeGETSchema getTree(IFormParameters... parameters) {
        return getTree(SUCCESS_MESSAGE, expectSuccess(), parameters);
    }

    @Step("Получить данные в виде дерева")
    @ParallelExecution(RESTRICT)
    public StatV1SegmentTreeGETSchema getTreeAndExpectError(IFormParameters parameters, IExpectedError error) {
        return getTree(ERROR_MESSAGE, expectError(error), parameters);
    }

    private StatV1DataActivityRawGETSchema getActivities(String message, Matcher matcher, IFormParameters... parameters) {
        StatV1DataActivityRawGETSchema result = get(StatV1DataActivityRawGETSchema.class,
                "/stat/v1/data/activity_raw",
                aggregate(parameters));

        assertThat(message, result, matcher);

        return result;
    }

    private StatV1SegmentTreeGETSchema getTree(String message, Matcher matcher, IFormParameters... parameters) {
        StatV1SegmentTreeGETSchema result = get(StatV1SegmentTreeGETSchema.class,
                "/stat/v1/segment/tree",
                aggregate(parameters));

        assertThat(message, result, matcher);

        return result;
    }
}
