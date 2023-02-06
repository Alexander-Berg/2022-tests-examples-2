package ru.yandex.autotests.metrika.appmetrica.steps;

import java.net.URL;
import java.util.Collections;
import java.util.List;
import java.util.Objects;

import org.hamcrest.Matcher;
import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.*;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.autotests.metrika.appmetrica.wrappers.GrantWrapper;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.mobmet.model.MobmetGrantE;
import ru.yandex.qatools.allure.annotations.Step;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.parameters.UserLoginParameters.userLogin;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;
import static ru.yandex.autotests.metrika.appmetrica.utils.Utils.isAgency;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ANYTHING_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectAnything;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

/**
 * Created by graev on 01/12/2016.
 */
public class GrantSteps extends AppMetricaBaseSteps {
    public GrantSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить список грантов для приложения {0}")
    @ParallelExecution(ALLOW)
    public List<MobmetGrantE> getGrantList(long appId) {
        return getGrantList(SUCCESS_MESSAGE, expectSuccess(), appId).getGrants();
    }

    @Step("Получить грант для приложения {0} и пользователя {1}")
    @ParallelExecution(ALLOW)
    public MobmetGrantE getGrant(long appId, String login) {
        return getGrant(SUCCESS_MESSAGE, expectSuccess(), appId, login).getGrant();
    }

    @Step("Получить грант для приложения {0}, пользователя {1} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public void getGrantAndExpectError(long appId, String login, IExpectedError error) {
        getGrant(ERROR_MESSAGE, expectError(error), appId, login);
    }

    @Step("Создать грант для приложения {0} и партнера {2} если его еще нет")
    @ParallelExecution(ALLOW)
    public MobmetGrantE createGrantIfAny(long appId, GrantWrapper grant, Long partnerId) {
        if (grant.isNotEmpty() && isAgency(grant)) {
            grant.getGrant().setPartners(Collections.singletonList(partnerId));
        }
        return createGrantIfAny(appId, grant);
    }

    @Step("Создать грант для приложения {0} если его еще нет")
    @ParallelExecution(ALLOW)
    public MobmetGrantE createGrantIfAny(long appId, GrantWrapper grant) {
        if (grant.isNotEmpty()) {
            return createGrant(appId, grant);
        }
        return null;
    }

    @Step("Создать грант {1} для приложения {0} с параметрами {2}")
    @ParallelExecution(ALLOW)
    public MobmetGrantE createGrant(long appId, GrantWrapper grant, IFormParameters... parameters) {
        return createGrant(SUCCESS_MESSAGE, expectSuccess(), appId, grant.getGrant(), parameters).getGrant();
    }

    @Step("Создать грант {1} для приложения {0} если его не существует")
    @ParallelExecution(ALLOW)
    public MobmetGrantE createGrantIfNotExists(long appId, GrantWrapper grant) {
        final List<MobmetGrantE> existing = getGrantList(appId);
        return existing.stream()
                // Существуют гранты без логина связанные с социальной авторизацией,
                // поэтому учитываем возможность, того, что userLogin равен null
                .filter(g -> Objects.equals(g.getUserLogin(), grant.getGrant().getUserLogin()))
                .findFirst()
                .orElseGet(() -> createGrant(appId, grant));
    }

    @Step("Создать грант {1} для приложения {0} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public void createGrantAndExpectError(long appId, GrantWrapper grant, IExpectedError error) {
        createGrant(ERROR_MESSAGE, expectError(error), appId, grant.getGrant());
    }

    @Step("Отредактировать грант на {1} для приложения {0}")
    @ParallelExecution(ALLOW)
    public MobmetGrantE editGrant(long appId, GrantWrapper grant) {
        return editGrant(SUCCESS_MESSAGE, expectSuccess(), appId, grant.getGrant()).getGrant();
    }

    @Step("Отредактировать грант на {1} для приложения {0} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public MobmetGrantE editGrantAndExpectError(long appId, GrantWrapper grant, IExpectedError error) {
        return editGrant(ERROR_MESSAGE, expectError(error), appId, grant.getGrant()).getGrant();
    }

    @Step("Удалить грант для приложения {0}, пользователя {1}")
    @ParallelExecution(ALLOW)
    public void deleteGrant(long appId, String login) {
        deleteGrant(SUCCESS_MESSAGE, expectSuccess(), appId, login);
    }

    @Step("Удалить грант для приложения {0} и игнорировать результат")
    @ParallelExecution(ALLOW)
    public void deleteGrantIgnoringResult(long appId, GrantWrapper grant) {
        if (grant != null && grant.getGrant() != null) {
            deleteGrant(ANYTHING_MESSAGE, expectAnything(), appId, grant.getGrant().getUserLogin());
        }
    }

    @Step("Удалить грант для приложения {0}, пользователя {1} и игнорировать результат")
    @ParallelExecution(ALLOW)
    public void deleteGrantIgnoringResult(long appId, String login) {
        deleteGrant(ANYTHING_MESSAGE, expectAnything(), appId, login);
    }

    @Step("Получить роли для пользователя {0}")
    @ParallelExecution(ALLOW)
    public InternalRbacRolesGETSchema getRoles(@SuppressWarnings("unused") String login) {
        return getRoles(SUCCESS_MESSAGE, expectSuccess());
    }

    private ManagementV1ApplicationAppIdGrantsGETSchema getGrantList(String message, Matcher matcher, long appId) {
        ManagementV1ApplicationAppIdGrantsGETSchema result = get(ManagementV1ApplicationAppIdGrantsGETSchema.class,
                format("/management/v1/application/%s/grants", appId));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1ApplicationAppIdGrantGETSchema getGrant(String message, Matcher matcher, long appId, String login) {
        ManagementV1ApplicationAppIdGrantGETSchema result = get(ManagementV1ApplicationAppIdGrantGETSchema.class,
                format("/management/v1/application/%s/grant", appId),
                userLogin(login));

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1ApplicationAppIdGrantsPOSTSchema createGrant(String message,
                                                                     Matcher matcher,
                                                                     long appId,
                                                                     MobmetGrantE grant,
                                                                     IFormParameters... parameters) {
        ManagementV1ApplicationAppIdGrantsPOSTSchema result = post(ManagementV1ApplicationAppIdGrantsPOSTSchema.class,
                format("/management/v1/application/%s/grants", appId),
                new ManagementV1ApplicationAppIdGrantsPOSTRequestSchema().withGrant(grant),
                parameters);

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1ApplicationAppIdGrantPUTSchema editGrant(String message,
                                                                 Matcher matcher,
                                                                 long appId,
                                                                 MobmetGrantE grant) {
        ManagementV1ApplicationAppIdGrantPUTSchema result = put(
                ManagementV1ApplicationAppIdGrantPUTSchema.class,
                String.format("/management/v1/application/%s/grant", appId),
                new ManagementV1ApplicationAppIdGrantPUTRequestSchema().withGrant(grant));

        assertThat(message, result, matcher);

        return result;
    }

    private void deleteGrant(String message, Matcher matcher, long appId, String login) {
        ManagementV1ApplicationAppIdGrantDELETESchema result = delete(ManagementV1ApplicationAppIdGrantDELETESchema.class,
                String.format("/management/v1/application/%s/grant", appId),
                userLogin(login));

        assertThat(message, result, matcher);
    }

    private InternalRbacRolesGETSchema getRoles(String message, Matcher matcher) {
        InternalRbacRolesGETSchema result = get(InternalRbacRolesGETSchema.class, "/internal/rbac/roles");

        assertThat(message, result, matcher);

        return result;
    }
}
