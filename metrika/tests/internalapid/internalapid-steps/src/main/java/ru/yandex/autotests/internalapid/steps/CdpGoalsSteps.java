package ru.yandex.autotests.internalapid.steps;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.internalapid.beans.schemes.CdpGoalsGETSchema;
import ru.yandex.autotests.irt.testutils.allure.TestSteps;
import ru.yandex.autotests.metrika.commons.clients.http.FreeFormParameters;
import ru.yandex.autotests.metrika.commons.clients.http.HttpClientLiteFacade;
import ru.yandex.metrika.util.wrappers.CdpGoalsWrapper;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;

import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

public class CdpGoalsSteps extends HttpClientLiteFacade {

    private final UserSteps userSteps;

    protected CdpGoalsSteps(URL baseUrl, HttpClientLite client,  UserSteps steps) {
        super(baseUrl, client);
        this.userSteps = steps;
    }

    @Step("Успешно получить cdp цели")
    public CdpGoalsWrapper getCdpGoalsAndExpectSuccess(long counterId) {
        CdpGoalsGETSchema schema = getCdpGoals(counterId, SUCCESS_MESSAGE, expectSuccess());
        return new CdpGoalsWrapper()
                .withCdpOrderInProgressGoalId(schema.getCdpOrderInProgressGoalId())
                .withCdpOrderPaidGoalId(schema.getCdpOrderPaidGoalId());
    }

    public CdpGoalsGETSchema getCdpGoals(long counterId, String message, Matcher matcher, IFormParameters... parameters) {
        CdpGoalsGETSchema result = get(CdpGoalsGETSchema.class, "/cdp_goals",
                new FreeFormParameters().append("counter_id", counterId));

        TestSteps.assertThat(message, result, matcher);

        return result;
    }
}
