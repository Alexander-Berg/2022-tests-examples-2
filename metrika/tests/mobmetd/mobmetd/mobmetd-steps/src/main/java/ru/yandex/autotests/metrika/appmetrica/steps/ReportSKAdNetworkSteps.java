package ru.yandex.autotests.metrika.appmetrica.steps;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.SkadnetworkV1DataBytimeGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.SkadnetworkV1DataGETSchema;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;

import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.RESTRICT;

/**
 * Created by konkov on 04.05.2016.
 */
public class ReportSKAdNetworkSteps extends AppMetricaBaseSteps {

    public ReportSKAdNetworkSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить отчет 'таблица'")
    @ParallelExecution(RESTRICT)
    public SkadnetworkV1DataGETSchema getTableReport(IFormParameters... parameters) {
        return get(SkadnetworkV1DataGETSchema.class, "skadnetwork/v1/data", parameters);
    }

    @Step("Получить отчет 'по времени'")
    @ParallelExecution(RESTRICT)
    public SkadnetworkV1DataBytimeGETSchema getByTimeReport(IFormParameters... parameters) {
        return get(SkadnetworkV1DataBytimeGETSchema.class, "skadnetwork/v1/data/bytime", parameters);
    }
}
