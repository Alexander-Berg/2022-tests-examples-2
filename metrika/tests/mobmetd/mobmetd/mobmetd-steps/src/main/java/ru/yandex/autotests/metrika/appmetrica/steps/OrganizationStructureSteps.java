package ru.yandex.autotests.metrika.appmetrica.steps;

import java.net.URL;
import java.util.List;

import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1OrganizationsIdStructureApplicationAppIdDELETESchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1OrganizationsIdStructureApplicationAppIdPUTSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1OrganizationsStructureGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1OrganizationsStructureIdGETSchema;
import ru.yandex.autotests.metrika.appmetrica.errors.ManagementError;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.metrika.mobmet.organization.model.OrganizationStructure;
import ru.yandex.qatools.allure.annotations.Step;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

public class OrganizationStructureSteps extends AppMetricaBaseSteps {

    public OrganizationStructureSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить информацию о составе организации")
    @ParallelExecution(ALLOW)
    public OrganizationStructure get(long id) {
        ManagementV1OrganizationsStructureIdGETSchema result = get(
                ManagementV1OrganizationsStructureIdGETSchema.class,
                format("/management/v1/organizations/structure/%s", id));
        assertThat(SUCCESS_MESSAGE, result, expectSuccess());
        return result.getOrganizationStructure();
    }

    @Step("Получить список организаций доступных пользователю")
    @ParallelExecution(ALLOW)
    public List<OrganizationStructure> getList() {
        ManagementV1OrganizationsStructureGETSchema result = get(
                ManagementV1OrganizationsStructureGETSchema.class,
                "/management/v1/organizations/structure");
        assertThat(SUCCESS_MESSAGE, result, expectSuccess());
        return result.getOrganizations();
    }

    @Step("Добавить приложение в организацию")
    @ParallelExecution(ALLOW)
    public void addToOrganization(long organizationId, long appId) {
        ManagementV1OrganizationsIdStructureApplicationAppIdPUTSchema result = put(
                ManagementV1OrganizationsIdStructureApplicationAppIdPUTSchema.class,
                format("/management/v1/organizations/%s/structure/application/%s", organizationId, appId)
        );

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());
    }


    @Step("Добавить приложение в организацию и ожидать ошибку")
    @ParallelExecution(ALLOW)
    public void addToOrganizationAndExpectError(long organizationId, long appId, ManagementError error) {
        ManagementV1OrganizationsIdStructureApplicationAppIdPUTSchema result = put(
                ManagementV1OrganizationsIdStructureApplicationAppIdPUTSchema.class,
                format("/management/v1/organizations/%s/structure/application/%s", organizationId, appId)
        );

        assertThat(ERROR_MESSAGE, result, expectError(error));
    }

    @Step("Удалить приложение из организации")
    @ParallelExecution(ALLOW)
    public void removeFromOrganization(long organizationId, long appId) {
        ManagementV1OrganizationsIdStructureApplicationAppIdDELETESchema result = delete(
                ManagementV1OrganizationsIdStructureApplicationAppIdDELETESchema.class,
                format("/management/v1/organizations/%s/structure/application/%s", organizationId, appId)
        );

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());
    }

    @Step("Удалить приложение из организации и ожидать ошибку")
    @ParallelExecution(ALLOW)
    public void deleteFromOrganizationAndExpectError(long organizationId, long appId, ManagementError error) {
        ManagementV1OrganizationsIdStructureApplicationAppIdDELETESchema result = delete(
                ManagementV1OrganizationsIdStructureApplicationAppIdDELETESchema.class,
                format("/management/v1/organizations/%s/structure/application/%s", organizationId, appId)
        );

        assertThat(ERROR_MESSAGE, result, expectError(error));
    }
}
