package ru.yandex.autotests.metrika.appmetrica.steps;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.*;
import ru.yandex.autotests.metrika.appmetrica.parameters.CommonFrontParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.PushCampaignsListParameters;
import ru.yandex.autotests.metrika.appmetrica.parameters.push.credentials.PushCampaignParameter;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.autotests.metrika.appmetrica.wrappers.PushCampaignWrapper;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.mobmet.push.common.campaigns.adapters.LaunchStatusAdapter;
import ru.yandex.metrika.mobmet.push.common.campaigns.adapters.PushCampaignAdapter;
import ru.yandex.metrika.mobmet.push.common.campaigns.adapters.PushCampaignsAdapter;
import ru.yandex.metrika.mobmet.push.common.campaigns.model.DeleteStatus;
import ru.yandex.metrika.mobmet.push.response.EstimationResponse;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters.makeParameters;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.RESTRICT;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.*;

/**
 * Created by graev on 23/09/16.
 */
public class PushCampaignSteps extends AppMetricaBaseSteps {
    public PushCampaignSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить информацию о кампании {0}")
    @ParallelExecution(RESTRICT)
    public PushCampaignAdapter getCampaign(Long id) {
        return getCampaign(SUCCESS_MESSAGE, expectSuccess(), id).getCampaign();
    }

    @Step("Получить список кампаний для приложения {0}")
    @ParallelExecution(RESTRICT)
    public PushCampaignsAdapter getCampaignList(PushCampaignsListParameters parameters) {
        return getCampaignList(SUCCESS_MESSAGE, expectSuccess(), parameters).getResponse();
    }

    @Step("Добавить кампанию {0}")
    @ParallelExecution(RESTRICT)
    public PushCampaignAdapter addCampaign(PushCampaignWrapper campaign) {
        return addCampaign(SUCCESS_MESSAGE, expectSuccess(), campaign.getCampaign()).getCampaign();
    }

    @Step("Добавить кампанию {0} и ожидать ошибку {1}")
    @ParallelExecution(ALLOW)
    public void addCampaignAndExpectError(PushCampaignWrapper campaign, IExpectedError error) {
        addCampaign(ERROR_MESSAGE, expectError(error), campaign.getCampaign());
    }

    @Step("Удалить кампанию {0}")
    @ParallelExecution(ALLOW)
    public DeleteStatus deleteCampaign(Long id) {
        return deleteCampaign(SUCCESS_MESSAGE, expectSuccess(), id).getDeleteStatus();
    }

    @Step("Удалить кампанию {0} и игнорировать результат")
    @ParallelExecution(ALLOW)
    public DeleteStatus deleteCampaignIgnoringStatus(Long campaignId) {
        if (campaignId == null) {
            return new DeleteStatus().withOk(true);
        }

        return deleteCampaign(ANYTHING_MESSAGE, expectAnything(), campaignId).getDeleteStatus();
    }

    @Step("Запустить кампанию {0}")
    @ParallelExecution(RESTRICT)
    public LaunchStatusAdapter launchCampaign(Long campaignId) {
        return launchCampaign(ANYTHING_MESSAGE, expectAnything(), campaignId).getLaunchStatus();
    }

    @Step("Оценить аудиторию кампании {0}")
    @ParallelExecution(RESTRICT)
    public EstimationResponse estimate(Long pushCampaignId, PushCampaignParameter... parameters) {
        ManagementV1PushCampaignCampaignIdEstimationGETSchema result = get(
                ManagementV1PushCampaignCampaignIdEstimationGETSchema.class,
                format("/management/v1/push/campaign/%s/estimation", pushCampaignId),
                makeParameters()
                        .append(new CommonFrontParameters())
                        .append(parameters));
        return result.getResponse();
    }

    private ManagementV1PushCampaignCampaignIdGETSchema getCampaign(String message, Matcher matcher, Long id) {
        ManagementV1PushCampaignCampaignIdGETSchema result = get(
                ManagementV1PushCampaignCampaignIdGETSchema.class,
                format("/management/v1/push/campaign/%s", id));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1PushCampaignsGETSchema getCampaignList(String message, Matcher matcher,
                                                               PushCampaignsListParameters parameters) {
        ManagementV1PushCampaignsGETSchema result = get(
                ManagementV1PushCampaignsGETSchema.class,
                "/management/v1/push/campaigns",
                parameters);

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1PushCampaignsPOSTSchema addCampaign(String message, Matcher matcher,
                                                            PushCampaignAdapter request) {
        ManagementV1PushCampaignsPOSTSchema result = post(
                ManagementV1PushCampaignsPOSTSchema.class,
                "/management/v1/push/campaigns",
                new ManagementV1PushCampaignsPOSTRequestSchema().withCampaign(request));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1PushCampaignCampaignIdLaunchPOSTSchema launchCampaign(String message, Matcher matcher, long campaignId) {
        ManagementV1PushCampaignCampaignIdLaunchPOSTSchema result = post(
                ManagementV1PushCampaignCampaignIdLaunchPOSTSchema.class,
                format("/management/v1/push/campaign/%s/launch", campaignId),
                new CommonFrontParameters());

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1PushCampaignCampaignIdDELETESchema deleteCampaign(String message, Matcher matcher, long id) {
        ManagementV1PushCampaignCampaignIdDELETESchema result = delete(
                ManagementV1PushCampaignCampaignIdDELETESchema.class,
                format("/management/v1/push/campaign/%s", id)
        );

        assertThat(message, result, matcher);

        return result;
    }

}
