package ru.yandex.autotests.audience.internal.api.steps;

import ru.yandex.audience.dmp.DmpExternalSegment;
import ru.yandex.audience.intapi.direct.UsersGoalsServiceInnerDmpCondition;
import ru.yandex.audience.internal.DirectDmpSegmentsGETSchema;
import ru.yandex.autotests.audience.internal.api.schema.custom.DirectDmpConditionsSchema;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.commons.clients.http.HttpClientLiteFacade;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;
import java.util.List;
import java.util.Map;

/**
 * Created by apuzikov on 12.07.17.
 */
public class DisplaySteps extends HttpClientLiteFacade {

    protected DisplaySteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }


    @Step("Получить охват по сегменту")
    public List<DmpExternalSegment> getDmpSegments(IFormParameters... parameters) {
        return get(DirectDmpSegmentsGETSchema.class, "/direct/dmp_segments", parameters).getResponse();
    }

    @Step("Получить список всех dmp сегментов для клиента")
    public Map<Long, List<UsersGoalsServiceInnerDmpCondition>> getConditionsByUid(IFormParameters... parameters) {
        return get(DirectDmpConditionsSchema.class, "/direct/dmp_conditions_by_uids", parameters);
    }
}