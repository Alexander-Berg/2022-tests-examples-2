package ru.yandex.autotests.metrika.steps.internal;

import ru.yandex.autotests.metrika.beans.schemes.InternalAdminDebugAbExpConditionGETSchema;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.qatools.allure.annotations.Step;

import static org.junit.Assert.assertTrue;

public class AbExperimentsSteps extends MetrikaBaseSteps {

    @Step("Проверить условие {0} для счетчика {1}, паспортного uid {2} и yandexuid {3}")
    public InternalAdminDebugAbExpConditionGETSchema checkConditionAndExpectSuccess(String condition, Integer counterId,
                                                                                    Long puid, String yuid) {
        InternalAdminDebugAbExpConditionGETSchema response = checkCondition(condition, counterId, puid, yuid);
        assertTrue(response.getCode() == null || response.getCode() == 200L);
        return response;
    }

    private InternalAdminDebugAbExpConditionGETSchema checkCondition(String condition,
                                                                     Integer counterId,
                                                                     Long puid,
                                                                     String yuid) {
        return executeAsJson(getRequestBuilder("/internal/admin/debug_ab_exp_condition").get(
                FreeFormParameters.makeParameters()
                        .append("condition", condition)
                        .append("counter_id", counterId)
                        .append("puid", puid)
                        .append("yuid", yuid))).readResponse(InternalAdminDebugAbExpConditionGETSchema.class);
    }
}
