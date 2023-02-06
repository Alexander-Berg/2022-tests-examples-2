package ru.yandex.autotests.metrika.steps.report;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataClickGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataFormGETPOSTSchema;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataLinkGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataLinkMapGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.MapsV1DataScrollGETSchema;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.common.handles.RequestType;
import ru.yandex.autotests.metrika.data.common.handles.RequestTypes;
import ru.yandex.autotests.metrika.reportwrappers.InpageReport;
import ru.yandex.autotests.metrika.reportwrappers.InpageReportFactory;
import ru.yandex.qatools.allure.annotations.Step;

/**
 * Created by okunev on 22.12.2014.
 */
public class InpageSteps extends BaseReportSteps {

    @Step("Построить отчет {0}")
    public InpageReport getInpageReportAndExpectSuccess(RequestType<?> method, IFormParameters... parameters) {
        return InpageReportFactory.create(getJsonReportAndExpectSuccess(method, parameters));
    }

    @Step("Построить отчет {0} и ожидать ошибку {1}")
    public InpageReport getInpageReportAndExpectError(RequestType<?> method, IExpectedError error, IFormParameters... parameters) {
        return InpageReportFactory.create(getJsonReportAndExpectError(method, error, parameters));
    }

    @Step("Построить отчет аналитики форм")
    public MapsV1DataFormGETPOSTSchema getInpageFormDataAndExpectSuccess(IFormParameters... parameters) {
        return getJsonReportAndExpectSuccess(RequestTypes.INPAGE_FORM, parameters);
    }

    @Step("Построить отчет аналитики форм и ожидать ошибку {0}")
    public MapsV1DataFormGETPOSTSchema getInpageFormDataAndExpectError(IExpectedError error,
                                                                       IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.INPAGE_FORM, error, parameters);
    }

    @Step("Построить список адресов карты ссылок")
    public MapsV1DataLinkGETSchema getInpageLinkUrlsAndExpectSuccess(IFormParameters... parameters) {
        return getJsonReportAndExpectSuccess(RequestTypes.INPAGE_LINK_URLS, parameters);
    }

    @Step("Построить отчет карты ссылок")
    public MapsV1DataLinkMapGETSchema getInpageLinkDataAndExpectSuccess(IFormParameters... parameters) {
        return getJsonReportAndExpectSuccess(RequestTypes.INPAGE_LINK, parameters);
    }

    @Step("Построить отчет карты ссылок и ожадать ошибку {0}")
    public MapsV1DataLinkMapGETSchema getInpageLinkDataAndExpectError(IExpectedError error,
                                                                      IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.INPAGE_LINK, error, parameters);
    }

    @Step("Построить отчет карты кликов")
    public MapsV1DataClickGETSchema getInpageClickDataAndExpectSuccess(IFormParameters... parameters) {
        return getJsonReportAndExpectSuccess(RequestTypes.INPAGE_CLICK, parameters);
    }

    @Step("Построить отчет карты кликов и ожидать ошибку {0}")
    public MapsV1DataClickGETSchema getInpageClickDataAndExpectError(IExpectedError error,
                                                                     IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.INPAGE_CLICK, error, parameters);
    }

    @Step("Построить отчет карты скроллинга")
    public MapsV1DataScrollGETSchema getInpageScrollDataAndExpectSuccess(IFormParameters... parameters) {
        return getJsonReportAndExpectSuccess(RequestTypes.INPAGE_SCROLL, parameters);
    }

    @Step("Построить отчет карты скроллинга и ожидать ошибку {0}")
    public MapsV1DataScrollGETSchema getInpageScrollDataAndExpectError(IExpectedError error,
                                                                       IFormParameters... parameters) {
        return getJsonReportAndExpectError(RequestTypes.INPAGE_SCROLL, error, parameters);
    }
}
