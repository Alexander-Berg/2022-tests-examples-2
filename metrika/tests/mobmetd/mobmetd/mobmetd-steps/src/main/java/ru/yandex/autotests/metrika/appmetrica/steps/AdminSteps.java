package ru.yandex.autotests.metrika.appmetrica.steps;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1AdminApplicationsGETSchema;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.metrika.mobmet.management.ApplicationUnderCampaign;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URL;
import java.util.List;

import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.RESTRICT;
import static ru.yandex.autotests.metrika.appmetrica.utils.Utils.aggregate;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

public class AdminSteps extends AppMetricaBaseSteps {

    public AdminSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить список приложений")
    @ParallelExecution(RESTRICT)
    public List<ApplicationUnderCampaign> getApplications(IFormParameters... parameters) {
        return getApplications(SUCCESS_MESSAGE, expectSuccess(), parameters).getApplications();
    }

    private ManagementV1AdminApplicationsGETSchema getApplications(String message,
                                                                   Matcher matcher,
                                                                   IFormParameters... parameters) {
        ManagementV1AdminApplicationsGETSchema result = get(ManagementV1AdminApplicationsGETSchema.class,
                "management/v1/admin/applications",
                aggregate(parameters));

        assertThat(message, result, matcher);

        return result;
    }
}
