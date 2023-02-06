package ru.yandex.autotests.audience.internal.api.steps;

import ru.yandex.audience.intapi.direct.RetargetingConditionsWrapper;
import ru.yandex.audience.intapi.direct.UsersGoalsServiceInnerRetargetingCondition;
import ru.yandex.audience.internal.GetUsersSketchedGETSchema;
import ru.yandex.autotests.audience.internal.api.schema.custom.DirectRetargetingConditionsCheckSchema;
import ru.yandex.autotests.audience.internal.api.schema.custom.DirectRetargetingConditionsSchema;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.commons.clients.http.HttpClientLiteFacade;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;
import java.util.List;
import java.util.Map;

/**
 * Created by apuzikov on 27.06.17.
 */
public class DirectSteps extends HttpClientLiteFacade {


    public DirectSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить список всех сегментов и условий для клиента")
    public Map<Long, List<UsersGoalsServiceInnerRetargetingCondition>> getRetargentingConditionsByUid(IFormParameters... parameters) {
        return get(DirectRetargetingConditionsSchema.class, "/direct/retargeting_conditions_by_uids.json", parameters);
    }

    @Step("Получить список всех сегментов и условий для клиента")
    public RetargetingConditionsWrapper getRetargentingConditionsByUid2(IFormParameters... parameters) {
        return get(RetargetingConditionsWrapper.class, "/direct/retargeting_conditions_by_uids2", parameters);
    }

    @Step("Проверить доступ uid к обьектам для retargeting_conditions")
    public Map<String, List<Long>> checkRetargetingConditionsByUid(IFormParameters... parameters) {
        return get(DirectRetargetingConditionsCheckSchema.class, "/direct/retargeting_conditions_check_access", parameters);
    }

    @Step("Получить охват по сегменту")
    public GetUsersSketchedGETSchema getUsersSegmentsSketched(IFormParameters... parameters) {
        return get(GetUsersSketchedGETSchema.class, "/get_users_sketched", parameters);
    }

}
