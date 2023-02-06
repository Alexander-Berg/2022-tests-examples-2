package ru.yandex.autotests.metrika.appmetrica.steps;

import java.net.URL;

import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1OrganizationsIdDELETESchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1OrganizationsIdGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1OrganizationsIdPUTRequestSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1OrganizationsIdPUTSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1OrganizationsPOSTRequestSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1OrganizationsPOSTSchema;
import ru.yandex.autotests.metrika.appmetrica.errors.ManagementError;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.metrika.mobmet.organization.model.Organization;
import ru.yandex.qatools.allure.annotations.Step;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

public class OrganizationSteps extends AppMetricaBaseSteps {

    public OrganizationSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить информацию об организации")
    @ParallelExecution(ALLOW)
    public Organization get(long id) {
        ManagementV1OrganizationsIdGETSchema result = get(
                ManagementV1OrganizationsIdGETSchema.class,
                format("/management/v1/organizations/%s", id));
        assertThat(SUCCESS_MESSAGE, result, expectSuccess());
        return result.getOrganization();
    }

    @Step("Создать организацию")
    @ParallelExecution(ALLOW)
    public Organization addOrganization(Organization organization) {
        ManagementV1OrganizationsPOSTSchema result = post(
                ManagementV1OrganizationsPOSTSchema.class,
                "/management/v1/organizations",
                new ManagementV1OrganizationsPOSTRequestSchema().withOrganization(organization)
        );

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getOrganization();
    }

    @Step("Создать организацию  и ожидать ошибку")
    @ParallelExecution(ALLOW)
    public void addOrganizationAndExpectError(Organization organization, ManagementError error) {
        ManagementV1OrganizationsPOSTSchema result = post(
                ManagementV1OrganizationsPOSTSchema.class,
                "/management/v1/organizations",
                new ManagementV1OrganizationsPOSTRequestSchema().withOrganization(organization)
        );

        assertThat(ERROR_MESSAGE, result, expectError(error));
    }

    @Step("Изменить организацию")
    @ParallelExecution(ALLOW)
    public Organization editOrganization(Organization organization) {
        ManagementV1OrganizationsIdPUTSchema result = put(
                ManagementV1OrganizationsIdPUTSchema.class,
                format("/management/v1/organizations/%s", organization.getId()),
                new ManagementV1OrganizationsIdPUTRequestSchema().withOrganization(organization)
        );

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getOrganization();
    }

    @Step("Изменить организацию  и ожидать ошибку")
    @ParallelExecution(ALLOW)
    public void editOrganizationAndExpectError(Organization organization, ManagementError error) {
        ManagementV1OrganizationsIdPUTSchema result = put(
                ManagementV1OrganizationsIdPUTSchema.class,
                format("/management/v1/organizations/%s", organization.getId()),
                new ManagementV1OrganizationsIdPUTRequestSchema().withOrganization(organization)
        );

        assertThat(ERROR_MESSAGE, result, expectError(error));
    }

    @Step("Удалить организацию")
    @ParallelExecution(ALLOW)
    public void delete(Long id) {
        ManagementV1OrganizationsIdDELETESchema result = delete(
                ManagementV1OrganizationsIdDELETESchema.class,
                format("/management/v1/organizations/%s", id)
        );

        assertThat(SUCCESS_MESSAGE, result, expectSuccess());
    }

    @Step("Удалить организацию и ожидать ошибку")
    @ParallelExecution(ALLOW)
    public void deleteAndExpectError(Long id, ManagementError error) {
        ManagementV1OrganizationsIdDELETESchema result = delete(
                ManagementV1OrganizationsIdDELETESchema.class,
                format("/management/v1/organizations/%s", id)
        );

        assertThat(ERROR_MESSAGE, result, expectError(error));
    }
}
