package ru.yandex.autotests.metrika.appmetrica.steps;

import java.net.URL;
import java.util.List;

import org.hamcrest.Matcher;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.httpclientlite.HttpClientLite;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.InternalManagementV1ApplicationProfileAttributesTypesGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationApiKeyProfileAttributeCustomAttributeIdDELETESchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationApiKeyProfileAttributeCustomAttributeIdRestorePOSTSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationApiKeyProfileAttributeCustomPUTRequestSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationApiKeyProfileAttributeCustomPUTSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationApiKeyProfileAttributesAllGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationApiKeyProfileAttributesCustomGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.ManagementV1ApplicationApiKeyProfileAttributesPredefinedGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1DataGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1ProfilesGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1ProfilesSessionsAllGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1ProfilesSessionsEventsAttributesGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1ProfilesSessionsEventsCrashesGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1ProfilesSessionsEventsDeeplinksGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1ProfilesSessionsEventsEcomGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1ProfilesSessionsEventsErrorsGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1ProfilesSessionsEventsGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1ProfilesSessionsEventsNamesGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1ProfilesSessionsEventsProtobufCrashesGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1ProfilesSessionsEventsProtobufErrorsGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1ProfilesSessionsEventsRevenueGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1ProfilesSessionsEventsUnwrapGETSchema;
import ru.yandex.autotests.metrika.appmetrica.beans.schemes.StatV1ProfilesSessionsGETSchema;
import ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution;
import ru.yandex.autotests.metrika.appmetrica.wrappers.ProfileCustomAttributeWrapper;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.metrika.mobmet.profiles.model.ProfileAttributesResponse;
import ru.yandex.metrika.mobmet.profiles.model.ProfileCustomAttribute;
import ru.yandex.metrika.mobmet.profiles.model.ProfileEventNamesList;
import ru.yandex.metrika.mobmet.profiles.model.ProfilePredefinedAttribute;
import ru.yandex.metrika.mobmet.profiles.model.ProfileSessionEvents;
import ru.yandex.metrika.mobmet.profiles.model.ProfileSessionsList;
import ru.yandex.metrika.mobmet.profiles.model.events.ProfileEvent;
import ru.yandex.metrika.segments.apps.misc.profile.ProfileAttributeType;
import ru.yandex.qatools.allure.annotations.Step;

import static java.lang.String.format;
import static ru.yandex.autotests.irt.testutils.allure.TestSteps.assertThat;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.ALLOW;
import static ru.yandex.autotests.metrika.appmetrica.steps.parallel.ParallelExecution.Permission.RESTRICT;
import static ru.yandex.autotests.metrika.appmetrica.utils.Utils.aggregate;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ANYTHING_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;

public class ProfileSteps extends AppMetricaBaseSteps {

    public ProfileSteps(URL baseUrl, HttpClientLite client) {
        super(baseUrl, client);
    }

    @Step("Получить все атрибуты типы профилей")
    @ParallelExecution(ALLOW)
    public List<ProfileAttributeType> getTypes(Long appId) {
        return types(SUCCESS_MESSAGE, expectSuccess()).getTypes();
    }

    @Step("Получить все атрибуты для приложения {0}")
    @ParallelExecution(RESTRICT)
    public ProfileAttributesResponse getAllAttributes(Long appId, IFormParameters... parameters) {
        return getAllAttributes(SUCCESS_MESSAGE, expectSuccess(), appId, parameters).getResponse();
    }

    @Step("Получить предопределённые атрибуты для приложения {0}")
    @ParallelExecution(RESTRICT)
    public List<ProfilePredefinedAttribute> getPredefinedAttributes(Long appId, IFormParameters... parameters) {
        return getPredefinedAttributes(SUCCESS_MESSAGE, expectSuccess(), appId, parameters).getAttributes();
    }

    @Step("Получить пользовательские атрибуты для приложения {0}")
    @ParallelExecution(RESTRICT)
    public List<ProfileCustomAttribute> getCustomAttributes(Long appId, IFormParameters... parameters) {
        return getCustomAttributes(SUCCESS_MESSAGE, expectSuccess(), appId, parameters).getAttributes();
    }

    @Step("Добавить атрибут {1} для приложения {0}")
    @ParallelExecution(ALLOW)
    public ProfileCustomAttribute createCustom(Long appId, ProfileCustomAttributeWrapper attribute) {
        return createCustom(SUCCESS_MESSAGE, expectSuccess(), appId, attribute.getAttribute()).getAttribute();
    }

    @Step("Добавить атрибут {1} для приложения {0} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public void createCustomAndExpectError(Long appId, ProfileCustomAttributeWrapper attribute, IExpectedError error) {
        createCustom(SUCCESS_MESSAGE, expectError(error), appId, attribute.getAttribute()).getAttribute();
    }

    @Step("Восстановить атрибут {1} для приложения {0}")
    @ParallelExecution(ALLOW)
    public void restoreCustom(Long appId, ProfileCustomAttributeWrapper attribute) {
        restoreCustom(SUCCESS_MESSAGE, expectSuccess(), appId, attribute.getAttribute().getId());
    }

    @Step("Восстановить атрибут {1} для приложения {0} и ожидать ошибку {2}")
    @ParallelExecution(ALLOW)
    public void restoreCustomAndExpectError(Long appId, ProfileCustomAttributeWrapper attribute, IExpectedError error) {
        restoreCustom(SUCCESS_MESSAGE, expectError(error), appId, attribute.getAttribute().getId());
    }

    @Step("Удалить атрибут {1} для приложения {0}")
    @ParallelExecution(ALLOW)
    public void deleteCustom(Long appId, ProfileCustomAttributeWrapper attribute) {
        deleteCustom(SUCCESS_MESSAGE, expectSuccess(), appId, attribute.getAttribute().getId());
    }

    @Step("Удалить атрибут {1} для приложения {0} и игнорировать результат")
    @ParallelExecution(ALLOW)
    public void deleteCustomAndIgnoreResult(Long appId, ProfileCustomAttributeWrapper attribute) {
        deleteCustom(ANYTHING_MESSAGE, expectSuccess(), appId, attribute.getAttribute().getId());
    }

    @Step("Запросить для профиля список с данными о сессиях")
    @ParallelExecution(RESTRICT)
    public ProfileSessionsList getSessions(IFormParameters... parameters) {
        return sessions(SUCCESS_MESSAGE, expectSuccess(), parameters).getSessionsList();
    }

    @Step("Запросить для профиля список с данными о сессиях и pos-api блоками")
    @ParallelExecution(RESTRICT)
    public ProfileSessionsList getSessionsAll(IFormParameters... parameters) {
        return sessionsAll(SUCCESS_MESSAGE, expectSuccess(), parameters).getSessionsList();
    }

    @Step("Запросить для профиля имена клиентских событий")
    @ParallelExecution(RESTRICT)
    public ProfileEventNamesList getClientEventNames(IFormParameters... parameters) {
        return eventNames(SUCCESS_MESSAGE, expectSuccess(), parameters).getClientEventNames();
    }

    @Step("Запросить события для сессий")
    @ParallelExecution(RESTRICT)
    public List<ProfileSessionEvents> getSessionsEvents(IFormParameters... parameters) {
        return sessionsEvents(SUCCESS_MESSAGE, expectSuccess(), parameters).getEventsPerSession();
    }

    @Step("Запросить значение для клиентского события")
    @ParallelExecution(RESTRICT)
    public String getClientEventValue(IFormParameters parameters) {
        return clientEventValue(SUCCESS_MESSAGE, expectSuccess(), parameters).getValue();
    }

    @Step("Запросить значение для события - крэша")
    @ParallelExecution(RESTRICT)
    public String getCrashEventValue(IFormParameters parameters) {
        return crashEventValue(SUCCESS_MESSAGE, expectSuccess(), parameters).getValue();
    }

    @Step("Запросить значение для события - открытия диплинка")
    @ParallelExecution(RESTRICT)
    public String getDeeplinkEventValue(IFormParameters parameters) {
        return deeplinkEventValue(SUCCESS_MESSAGE, expectSuccess(), parameters).getValue();
    }

    @Step("Запросить значение для события - ecommerce")
    @ParallelExecution(RESTRICT)
    public String getEcomEventValue(IFormParameters parameters) {
        return ecomEventValue(SUCCESS_MESSAGE, expectSuccess(), parameters).getValue();
    }

    @Step("Запросить значение для события - revenue")
    @ParallelExecution(RESTRICT)
    public String getRevenueEventValue(IFormParameters parameters) {
        return revenueRevenueValue(SUCCESS_MESSAGE, expectSuccess(), parameters).getValue();
    }

    @Step("Запросить значение для события - ошибки")
    @ParallelExecution(RESTRICT)
    public String getErrorEventValue(IFormParameters parameters) {
        return errorEventValue(SUCCESS_MESSAGE, expectSuccess(), parameters).getValue();
    }

    @Step("Запросить значение для события - крэша нового типа")
    @ParallelExecution(RESTRICT)
    public String getProtobufCrashEventValue(IFormParameters parameters) {
        return protobufCrashEventValue(SUCCESS_MESSAGE, expectSuccess(), parameters).getValue();
    }

    @Step("Запросить значение для события - ошибки нового типа")
    @ParallelExecution(RESTRICT)
    public String getProtobufErrorEventValue(IFormParameters parameters) {
        return protobufErrorEventValue(SUCCESS_MESSAGE, expectSuccess(), parameters).getValue();
    }

    @Step("Развернуть события в цепочке событий")
    @ParallelExecution(RESTRICT)
    public List<ProfileEvent> getUnwrappedEvents(IFormParameters parameters) {
        return unwrapEvents(SUCCESS_MESSAGE, expectSuccess(), parameters).getEvents();
    }

    @Step("Получить отчет по профилям")
    @ParallelExecution(RESTRICT)
    public StatV1ProfilesGETSchema getReport(IFormParameters parameters) {
        return get(StatV1ProfilesGETSchema.class, "/stat/v1/profiles", parameters);
    }

    @Step("Получить список профилей")
    @ParallelExecution(RESTRICT)
    public StatV1DataGETSchema getListReport(IFormParameters parameters) {
        return get(StatV1DataGETSchema.class, "/stat/v1/profiles/list", parameters);
    }

    private ManagementV1ApplicationApiKeyProfileAttributesCustomGETSchema getCustomAttributes(
            String message,
            Matcher matcher,
            Long appId,
            IFormParameters... parameters) {
        ManagementV1ApplicationApiKeyProfileAttributesCustomGETSchema result = get(
                ManagementV1ApplicationApiKeyProfileAttributesCustomGETSchema.class,
                format("/management/v1/application/%s/profile/attributes/custom", appId),
                aggregate(parameters)
        );

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1ApplicationApiKeyProfileAttributesPredefinedGETSchema getPredefinedAttributes(
            String message,
            Matcher matcher,
            Long appId,
            IFormParameters... parameters
    ) {
        ManagementV1ApplicationApiKeyProfileAttributesPredefinedGETSchema result = get(
                ManagementV1ApplicationApiKeyProfileAttributesPredefinedGETSchema.class,
                format("/management/v1/application/%s/profile/attributes/predefined", appId),
                aggregate(parameters)
        );

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1ApplicationApiKeyProfileAttributesAllGETSchema getAllAttributes(
            String message,
            Matcher matcher,
            Long appId,
            IFormParameters... parameters) {
        ManagementV1ApplicationApiKeyProfileAttributesAllGETSchema result = get(
                ManagementV1ApplicationApiKeyProfileAttributesAllGETSchema.class,
                format("/management/v1/application/%s/profile/attributes/all", appId),
                aggregate(parameters)
        );

        assertThat(message, result, matcher);

        return result;
    }

    private ManagementV1ApplicationApiKeyProfileAttributeCustomPUTSchema createCustom(
            String message,
            Matcher matcher,
            Long appId,
            ProfileCustomAttribute attribute) {
        ManagementV1ApplicationApiKeyProfileAttributeCustomPUTSchema result = put(
                ManagementV1ApplicationApiKeyProfileAttributeCustomPUTSchema.class,
                format("/management/v1/application/%s/profile/attribute/custom", appId),
                new ManagementV1ApplicationApiKeyProfileAttributeCustomPUTRequestSchema().withAttribute(attribute)
        );

        assertThat(message, result, matcher);

        return result;
    }

    private void restoreCustom(String message, Matcher matcher, Long appId, Long attributeId) {
        ManagementV1ApplicationApiKeyProfileAttributeCustomAttributeIdRestorePOSTSchema result = post(
                ManagementV1ApplicationApiKeyProfileAttributeCustomAttributeIdRestorePOSTSchema.class,
                format("/management/v1/application/%s/profile/attribute/custom/%s/restore", appId, attributeId),
                null
        );

        assertThat(message, result, matcher);
    }

    private void deleteCustom(String message, Matcher matcher, Long appId, Long attributeId) {
        ManagementV1ApplicationApiKeyProfileAttributeCustomAttributeIdDELETESchema result = delete(
                ManagementV1ApplicationApiKeyProfileAttributeCustomAttributeIdDELETESchema.class,
                format("/management/v1/application/%s/profile/attribute/custom/%s", appId, attributeId)
        );

        assertThat(message, result, matcher);
    }

    private InternalManagementV1ApplicationProfileAttributesTypesGETSchema types(String message, Matcher matcher) {
        InternalManagementV1ApplicationProfileAttributesTypesGETSchema result = get(
                InternalManagementV1ApplicationProfileAttributesTypesGETSchema.class,
                "/internal/management/v1/application/profile/attributes/types"
        );

        assertThat(message, result, matcher);

        return result;
    }

    private StatV1ProfilesSessionsGETSchema sessions(String message, Matcher matcher, IFormParameters... parameters) {
        StatV1ProfilesSessionsGETSchema result = get(
                StatV1ProfilesSessionsGETSchema.class,
                "/stat/v1/profiles/sessions",
                aggregate(parameters)
        );

        assertThat(message, result, matcher);

        return result;
    }

    private StatV1ProfilesSessionsAllGETSchema sessionsAll(String message,
                                                           Matcher matcher,
                                                           IFormParameters... parameters) {
        StatV1ProfilesSessionsAllGETSchema result = get(
                StatV1ProfilesSessionsAllGETSchema.class,
                "/stat/v1/profiles/sessions/all",
                aggregate(parameters)
        );

        assertThat(message, result, matcher);

        return result;
    }

    private StatV1ProfilesSessionsEventsNamesGETSchema eventNames(String message,
                                                                  Matcher matcher,
                                                                  IFormParameters... parameters) {
        StatV1ProfilesSessionsEventsNamesGETSchema result = get(
                StatV1ProfilesSessionsEventsNamesGETSchema.class,
                "/stat/v1/profiles/sessions/events/names",
                aggregate(parameters)
        );

        assertThat(message, result, matcher);

        return result;
    }

    private StatV1ProfilesSessionsEventsGETSchema sessionsEvents(String message,
                                                                 Matcher matcher,
                                                                 IFormParameters... parameters) {
        StatV1ProfilesSessionsEventsGETSchema result = get(
                StatV1ProfilesSessionsEventsGETSchema.class,
                "/stat/v1/profiles/sessions/events",
                aggregate(parameters)
        );

        assertThat(message, result, matcher);

        return result;
    }

    private StatV1ProfilesSessionsEventsAttributesGETSchema clientEventValue(String message,
                                                                             Matcher matcher,
                                                                             IFormParameters... parameters) {
        StatV1ProfilesSessionsEventsAttributesGETSchema result = get(
                StatV1ProfilesSessionsEventsAttributesGETSchema.class,
                "/stat/v1/profiles/sessions/events/attributes",
                aggregate(parameters)
        );

        assertThat(message, result, matcher);

        return result;
    }

    private StatV1ProfilesSessionsEventsCrashesGETSchema crashEventValue(String message,
                                                                         Matcher matcher,
                                                                         IFormParameters... parameters) {
        StatV1ProfilesSessionsEventsCrashesGETSchema result = get(
                StatV1ProfilesSessionsEventsCrashesGETSchema.class,
                "/stat/v1/profiles/sessions/events/crashes",
                aggregate(parameters)
        );

        assertThat(message, result, matcher);

        return result;
    }

    private StatV1ProfilesSessionsEventsDeeplinksGETSchema deeplinkEventValue(String message,
                                                                              Matcher matcher,
                                                                              IFormParameters... parameters) {
        StatV1ProfilesSessionsEventsDeeplinksGETSchema result = get(
                StatV1ProfilesSessionsEventsDeeplinksGETSchema.class,
                "/stat/v1/profiles/sessions/events/deeplinks",
                aggregate(parameters)
        );

        assertThat(message, result, matcher);

        return result;
    }

    private StatV1ProfilesSessionsEventsErrorsGETSchema errorEventValue(String message,
                                                                        Matcher matcher,
                                                                        IFormParameters... parameters) {
        StatV1ProfilesSessionsEventsErrorsGETSchema result = get(
                StatV1ProfilesSessionsEventsErrorsGETSchema.class,
                "/stat/v1/profiles/sessions/events/errors",
                aggregate(parameters)
        );

        assertThat(message, result, matcher);

        return result;
    }

    private StatV1ProfilesSessionsEventsProtobufCrashesGETSchema protobufCrashEventValue(
            String message,
            Matcher matcher,
            IFormParameters... parameters) {
        StatV1ProfilesSessionsEventsProtobufCrashesGETSchema result = get(
                StatV1ProfilesSessionsEventsProtobufCrashesGETSchema.class,
                "/stat/v1/profiles/sessions/events/protobuf/crashes",
                aggregate(parameters)
        );

        assertThat(message, result, matcher);

        return result;
    }

    private StatV1ProfilesSessionsEventsEcomGETSchema ecomEventValue(String message,
                                                                     Matcher matcher,
                                                                     IFormParameters... parameters) {
        StatV1ProfilesSessionsEventsEcomGETSchema result = get(
                StatV1ProfilesSessionsEventsEcomGETSchema.class,
                "/stat/v1/profiles/sessions/events/ecom",
                aggregate(parameters)
        );

        assertThat(message, result, matcher);

        return result;
    }

    private StatV1ProfilesSessionsEventsRevenueGETSchema revenueRevenueValue(String message,
                                                                             Matcher matcher,
                                                                             IFormParameters... parameters) {
        StatV1ProfilesSessionsEventsRevenueGETSchema result = get(
                StatV1ProfilesSessionsEventsRevenueGETSchema.class,
                "/stat/v1/profiles/sessions/events/revenue",
                aggregate(parameters)
        );

        assertThat(message, result, matcher);

        return result;
    }

    private StatV1ProfilesSessionsEventsProtobufErrorsGETSchema protobufErrorEventValue(String message,
                                                                                        Matcher matcher,
                                                                                        IFormParameters... parameters) {
        StatV1ProfilesSessionsEventsProtobufErrorsGETSchema result = get(
                StatV1ProfilesSessionsEventsProtobufErrorsGETSchema.class,
                "/stat/v1/profiles/sessions/events/protobuf/errors",
                aggregate(parameters)
        );

        assertThat(message, result, matcher);

        return result;
    }

    private StatV1ProfilesSessionsEventsUnwrapGETSchema unwrapEvents(String message,
                                                                     Matcher matcher,
                                                                     IFormParameters... parameters) {
        StatV1ProfilesSessionsEventsUnwrapGETSchema result = get(
                StatV1ProfilesSessionsEventsUnwrapGETSchema.class,
                "/stat/v1/profiles/sessions/events/unwrap",
                aggregate(parameters)
        );

        assertThat(message, result, matcher);

        return result;
    }
}
