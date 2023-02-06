package ru.yandex.autotests.metrika.steps;

import ru.yandex.autotests.httpclient.lite.core.BackEndResponse;
import ru.yandex.qatools.allure.annotations.Step;

public class JspRequestSteps extends MetrikaBaseSteps {

    @Step("Бессмысленный запрос jsp")
    public int getServerResponseStatus() {
        BackEndResponse response = execute(getRequestBuilder("/not_existing.jsp").get());
        return response.getStatusLine().getStatusCode();
    }
}
