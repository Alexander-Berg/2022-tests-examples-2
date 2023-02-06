package ru.yandex.autotests.metrika.appmetrica.steps;

import java.net.URL;
import java.util.List;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationApiKeyDELETESchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationApiKeyGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationApiKeyPUTRequestSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationApiKeyPUTSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationsGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationsPOSTRequestSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationsPOSTSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1MetadataApplicationCategoriesGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV2ApplicationsGETSchema;
import ru.yandex.autotests.metrika.appmetrica.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.mobmet.management.Application;
import ru.yandex.metrika.mobmet.management.ApplicationCreationInfo;
import ru.yandex.metrika.mobmet.management.ApplicationUpdateInfo;
import ru.yandex.metrika.mobmet.model.ApplicationCategory;
import ru.yandex.metrika.mobmet.model.ApplicationsPage;
import ru.yandex.qatools.allure.annotations.Step;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.RESTRICT;
import static ru.yandex.autotests.metrika.appmetrica.utils.Utils.aggregate;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ANYTHING_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectAnything;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

/**
 * Created by konkov on 12.09.2016.
 */
public class ApplicationSteps extends AppMetricaBaseSteps {
    public ApplicationSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить информацию о приложении {0}")
    @ParallelExecution(ALLOW)
    public Application getApplication(Long id) {
        return getApplication(SUCCESS_MESSAGE, expectSuccess(), id).getApplication();
    }

    @Step("Получить информацию о приложении {1} и ожидать ошибку {0}")
    @ParallelExecution(ALLOW)
    public Application getApplicationAndExpectError(IExpectedError error, Long id) {
        return getApplication(ERROR_MESSAGE, expectError(error), id).getApplication();
    }

    @Step("Получить список приложений")
    @ParallelExecution(RESTRICT)
    public List<Application> getApplications(IFormParameters... parameters) {
        return getApplications(SUCCESS_MESSAGE, expectSuccess(), parameters).getApplications();
    }

    @Step("Получить список приложений (v2)")
    @ParallelExecution(RESTRICT)
    public ApplicationsPage getApplicationsV2(IFormParameters... parameters) {
        return getApplicationsV2(SUCCESS_MESSAGE, expectSuccess(), parameters).getData();
    }

    @Step("Получить приложение {0} из списка")
    @ParallelExecution(ALLOW)
    public Application getApplicationFromList(long id, IFormParameters... parameters) {
        final List<Application> applications = getApplications(parameters);
        return applications.stream()
                .filter(a -> a.getId().equals(id))
                .findFirst()
                .orElseThrow(() -> new AssertionError("Application with given ID was not found in list"));
    }

    @Step("Получить список приложений и ожидать ошибку {0}")
    @ParallelExecution(ALLOW)
    public List<Application> getApplicationsAndExpectError(IExpectedError error, IFormParameters... parameters) {
        return getApplications(ERROR_MESSAGE, expectError(error), parameters).getApplications();
    }

    @Step("Добавить приложение")
    @ParallelExecution(ALLOW)
    public Application addApplication(ApplicationCreationInfo application) {
        return addApplication(SUCCESS_MESSAGE, expectSuccess(), application).getApplication();
    }

    @Step("Добавить приложение и ожидать ошибку {0}")
    @ParallelExecution(ALLOW)
    public Application addApplicationAndExpectError(IExpectedError error, ApplicationCreationInfo application) {
        return addApplication(ERROR_MESSAGE, expectError(error), application).getApplication();
    }

    @Step("Изменить приложение {0}")
    @ParallelExecution(ALLOW)
    public Application editApplication(Long id, ApplicationUpdateInfo application) {
        return editApplication(SUCCESS_MESSAGE, expectSuccess(), id, application).getApplication();
    }

    @Step("Изменить приложение {0} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public Application editApplicationAndExpectError(Long id, ApplicationUpdateInfo application, IExpectedError error) {
        return editApplication(ERROR_MESSAGE, expectError(error), id, application).getApplication();
    }

    @Step("Удалить приложение {0}")
    @ParallelExecution(ALLOW)
    public Boolean deleteApplication(Long id) {
        return deleteApplication(SUCCESS_MESSAGE, expectSuccess(), id).getSuccess();
    }

    @Step("Удалить приложение {0} и игнорировать результат")
    @ParallelExecution(ALLOW)
    public Boolean deleteApplicationAndIgnoreResult(Long id) {
        if (id == null) {
            return false;
        }
        return deleteApplication(ANYTHING_MESSAGE, expectAnything(), id).getSuccess();
    }

    @Step("Удалить приложение {1} и ожидать ошибку {0}")
    @ParallelExecution(ALLOW)
    public Boolean deleteApplicationAndExpectError(IExpectedError error, Long id) {
        return deleteApplication(ERROR_MESSAGE, expectError(error), id).getSuccess();
    }

    @Step("Получить список категорий приложений")
    @ParallelExecution(ALLOW)
    public List<ApplicationCategory> getApplicationCategories(String lang) {
        return applicationCategories(SUCCESS_MESSAGE, expectSuccess(), lang).getData();
    }

    private ManagementV1ApplicationApiKeyGETSchema getApplication(String message, Matcher matcher, Long id) {
        ManagementV1ApplicationApiKeyGETSchema result = get(ManagementV1ApplicationApiKeyGETSchema.class,
                format("management/v1/application/%s", id));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1ApplicationsGETSchema getApplications(String message, Matcher matcher, IFormParameters... parameters) {
        ManagementV1ApplicationsGETSchema result = get(ManagementV1ApplicationsGETSchema.class,
                "management/v1/applications",
                aggregate(parameters));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV2ApplicationsGETSchema getApplicationsV2(String message, Matcher matcher, IFormParameters... parameters) {
        ManagementV2ApplicationsGETSchema result = get(ManagementV2ApplicationsGETSchema.class,
                "management/v2/applications",
                aggregate(parameters));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1ApplicationsPOSTSchema addApplication(String message, Matcher matcher,
                                                              ApplicationCreationInfo application) {
        ManagementV1ApplicationsPOSTSchema result = post(ManagementV1ApplicationsPOSTSchema.class,
                "management/v1/applications",
                new ManagementV1ApplicationsPOSTRequestSchema().withApplication(application));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1ApplicationApiKeyPUTSchema editApplication(String message, Matcher matcher,
                                                                   Long id, ApplicationUpdateInfo application) {
        ManagementV1ApplicationApiKeyPUTSchema result = put(ManagementV1ApplicationApiKeyPUTSchema.class,
                format("management/v1/application/%s", id),
                new ManagementV1ApplicationApiKeyPUTRequestSchema().withApplication(application));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1ApplicationApiKeyDELETESchema deleteApplication(String message, Matcher matcher, Long id) {
        ManagementV1ApplicationApiKeyDELETESchema result = delete(ManagementV1ApplicationApiKeyDELETESchema.class,
                format("management/v1/application/%s", id));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1MetadataApplicationCategoriesGETSchema applicationCategories(String message, Matcher matcher, String lang) {
        ManagementV1MetadataApplicationCategoriesGETSchema result = get(ManagementV1MetadataApplicationCategoriesGETSchema.class,
                "management/v1/metadata/application/categories",
                new FreeFormParameters().append("lang", lang));

        assertThat(message, result, matcher);

        return result;
    }
}
