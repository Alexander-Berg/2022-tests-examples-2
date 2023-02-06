package ru.yandex.autotests.metrika.steps.management;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.TimeUnit;

import com.hazelcast.core.ILock;
import org.hamcrest.Matcher;

import ru.yandex.autotests.metrika.beans.schemes.InternalManagementV1SubscriptionsEmailsGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalManagementV1SubscriptionsListGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalManagementV1SubscriptionsSubscriptionPOSTRequestSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalManagementV1SubscriptionsSubscriptionPOSTSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalManagementV1SubscriptionsUserDELETESchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalManagementV1SubscriptionsUserGETSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalManagementV1SubscriptionsUserPOSTRequestSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalManagementV1SubscriptionsUserPOSTSchema;
import ru.yandex.autotests.metrika.beans.schemes.InternalManagementV1SubscriptionsUserPUTRequestSchema;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.steps.MetrikaBaseSteps;
import ru.yandex.metrika.api.management.client.subscriptions.Subscription;
import ru.yandex.metrika.api.management.client.subscriptions.SubscriptionAcceptFrom;
import ru.yandex.metrika.api.management.client.subscriptions.SubscriptionListType;
import ru.yandex.metrika.api.management.client.subscriptions.SubscriptionType;
import ru.yandex.metrika.api.management.client.subscriptions.SubscriptionUser;
import ru.yandex.metrika.api.management.client.wrappers.AddSubscriptionWrapperInnerAddSubscription;
import ru.yandex.metrika.api.management.client.wrappers.SubscriptionAddUserWrapperInnerAddUser;
import ru.yandex.qatools.allure.annotations.Step;

import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.ERROR_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.SUCCESS_MESSAGE;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectError;
import static ru.yandex.autotests.metrika.commons.response.ResponseMatchers.expectSuccess;
import static ru.yandex.autotests.metrika.utils.AllureUtils.assumeThat;

public class SubscriptionsSteps extends MetrikaBaseSteps {

    private static final String USER_PATH = "/internal/management/v1/subscriptions/user";
    private static final String ALL_EMAILS_PATH = "/internal/management/v1/subscriptions/emails";
    private static final String SUBSCRIPTIONS_LIST = "/internal/management/v1/subscriptions/list";
    private static final String SUBSCRIPTION_CHANGE = "/internal/management/v1/subscriptions/subscription";
    private static final String TEST_USER_AGENT = "test-user-agent Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36";
    private static final List<SubscriptionType> SUBSCRIPTION_TYPES = Arrays.asList(SubscriptionType.COUNTER_ADVICES,
            SubscriptionType.API_NEWS, SubscriptionType.PROMO, SubscriptionType.API_NEWS);

    /**
     * В связи с тем что стендов у нас много, а Postgres один, поэтому мы в кажом тесте захватываем hazelcast lock.
     * Но мы точно не знаем в каком состоянии нам приходят настройки пользователя, поэтому мы их "обнуляем" при этом игнорируя все проблемы, что пользователь уже подписан-отписан.
     */
    @Step("Создать глобальную подписку для пользователя, предварительно удалив его")
    public SubscriptionUser addClearUserWithDeleteBefore(String email) {

        InternalManagementV1SubscriptionsUserDELETESchema result1 = executeAsJson(
                getRequestBuilder(USER_PATH)
                        .delete(Collections.emptyList())
        ).readResponse(InternalManagementV1SubscriptionsUserDELETESchema.class);

        assumeThat(SUCCESS_MESSAGE, result1, expectSuccess());

        InternalManagementV1SubscriptionsUserPOSTSchema result = executeAsJson(
                getRequestBuilder(USER_PATH)
                        .post(new InternalManagementV1SubscriptionsUserPOSTRequestSchema()
                                .withUser(new SubscriptionAddUserWrapperInnerAddUser()
                                        .withEmail(email)
                                        .withUserAgent(TEST_USER_AGENT)
                                        .withAcceptFrom(SubscriptionAcceptFrom.USER_SETTINGS))
                        )).readResponse(InternalManagementV1SubscriptionsUserPOSTSchema.class);

        assumeThat(SUCCESS_MESSAGE, result, expectSuccess());

        for (SubscriptionType type : SUBSCRIPTION_TYPES) {
            executeAsJson(getRequestBuilder(SUBSCRIPTION_CHANGE).post(new InternalManagementV1SubscriptionsSubscriptionPOSTRequestSchema()
                    .withSubscription(new AddSubscriptionWrapperInnerAddSubscription()
                            .withType(type)
                            .withEnabled(false)
                            .withSubscriptionListType(type == SubscriptionType.COUNTER_ADVICES ? SubscriptionListType.OWNER : SubscriptionListType.ALL)
                            .withUserAgent(TEST_USER_AGENT)
                            .withCounterIds(Collections.emptyList())
                    )))
                    .readResponse(InternalManagementV1SubscriptionsSubscriptionPOSTSchema.class);
        }

        return result.getUser();
    }

    @Step("Создать глобальную подписку для пользователя")
    public SubscriptionUser addUser(String email) {
        InternalManagementV1SubscriptionsUserPOSTSchema result = executeAsJson(
                getRequestBuilder(USER_PATH)
                        .post(new InternalManagementV1SubscriptionsUserPOSTRequestSchema()
                                .withUser(new SubscriptionAddUserWrapperInnerAddUser()
                                        .withEmail(email)
                                        .withUserAgent(TEST_USER_AGENT)
                                        .withAcceptFrom(SubscriptionAcceptFrom.USER_SETTINGS))
                        )).readResponse(InternalManagementV1SubscriptionsUserPOSTSchema.class);

        assumeThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getUser();
    }

    @Step("Создать глобальную подписку для пользователя")
    public SubscriptionUser changeEmail(String newEmail) {
        InternalManagementV1SubscriptionsUserPOSTSchema result = executeAsJson(
                getRequestBuilder(USER_PATH)
                        .put(new InternalManagementV1SubscriptionsUserPUTRequestSchema()
                                .withUser(new SubscriptionAddUserWrapperInnerAddUser()
                                        .withEmail(newEmail)
                                        .withUserAgent(TEST_USER_AGENT)
                                        .withAcceptFrom(SubscriptionAcceptFrom.USER_SETTINGS))
                        )).readResponse(InternalManagementV1SubscriptionsUserPOSTSchema.class);

        assumeThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getUser();
    }

    @Step("Создать глобальную подписку для пользователя из под другого пользователя")
    public SubscriptionUser addUser(String email, long targetUid) {
        InternalManagementV1SubscriptionsUserPOSTSchema result = executeAsJson(
                getRequestBuilder(USER_PATH)
                        .post(new InternalManagementV1SubscriptionsUserPOSTRequestSchema()
                                .withUser(new SubscriptionAddUserWrapperInnerAddUser()
                                        .withEmail(email)
                                        .withUserAgent(TEST_USER_AGENT)
                                        .withAcceptFrom(SubscriptionAcceptFrom.USER_SETTINGS)),
                                new FreeFormParameters().append("uid", targetUid)
                        )).readResponse(InternalManagementV1SubscriptionsUserPOSTSchema.class);

        assumeThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getUser();
    }

    @Step("Создать глобальную подписку для пользователя из под другого пользователя")
    public SubscriptionUser addUserAndExpectError(IExpectedError error, String email, long targetUid) {
        InternalManagementV1SubscriptionsUserPOSTSchema result = executeAsJson(
                getRequestBuilder(USER_PATH)
                        .post(new InternalManagementV1SubscriptionsUserPOSTRequestSchema()
                                .withUser(new SubscriptionAddUserWrapperInnerAddUser()
                                        .withEmail(email)
                                        .withUserAgent(TEST_USER_AGENT)
                                        .withAcceptFrom(SubscriptionAcceptFrom.USER_SETTINGS)),
                                new FreeFormParameters().append("uid", targetUid)
                        )).readResponse(InternalManagementV1SubscriptionsUserPOSTSchema.class);

        assumeThat(ERROR_MESSAGE, result, expectError(error));

        return result.getUser();
    }

    @Step("Получить пользователя")
    public SubscriptionUser getUser(long targetUid) {
        InternalManagementV1SubscriptionsUserGETSchema result = executeAsJson(
                getRequestBuilder(USER_PATH)
                        .get(new FreeFormParameters().append("uid", targetUid))
        ).readResponse(InternalManagementV1SubscriptionsUserGETSchema.class);

        assumeThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getUser();
    }

    @Step("Получить пользователя")
    public SubscriptionUser getUserAndExpectError(IExpectedError error, long targetUid) {
        InternalManagementV1SubscriptionsUserGETSchema result = executeAsJson(
                getRequestBuilder(USER_PATH)
                        .get(new FreeFormParameters().append("uid", targetUid))
        ).readResponse(InternalManagementV1SubscriptionsUserGETSchema.class);

        assumeThat(ERROR_MESSAGE, result, expectError(error));

        return result.getUser();
    }
    @Step("Получить пользователя")
    public SubscriptionUser getUser() {
        InternalManagementV1SubscriptionsUserGETSchema result = executeAsJson(
                getRequestBuilder(USER_PATH)
                        .get()
        ).readResponse(InternalManagementV1SubscriptionsUserGETSchema.class);

        assumeThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getUser();
    }

    @Step("Удалить пользователя")
    public SubscriptionUser deleteUser() {
        InternalManagementV1SubscriptionsUserDELETESchema result = executeAsJson(
                getRequestBuilder(USER_PATH)
                        .delete(Collections.emptyList())
        ).readResponse(InternalManagementV1SubscriptionsUserDELETESchema.class);

        assumeThat(SUCCESS_MESSAGE, result, expectSuccess());

        return result.getUser();
    }

    /**
     * В связи с тем что стендов у нас много, а Postgres один, поэтому мы в кажом тесте захватываем hazelcast lock.
     * Но мы точно не знаем в каком состоянии нам приходят настройки пользователя, поэтому мы их "обнуляем" при этом игнорируя все проблемы, что пользователь уже подписан-отписан.
     */
    @Step("Тихо Удалить пользователя")
    public void deleteUserSilent() {
        try {
            executeAsJson(
                    getRequestBuilder(USER_PATH)
                            .delete(Collections.emptyList())
            ).readResponse(InternalManagementV1SubscriptionsUserDELETESchema.class);
        } catch (Exception ignore){}
    }

    @Step("Список почтовых адресов текущего пользователя")
    public List<String> getEmails() {
        InternalManagementV1SubscriptionsEmailsGETSchema result =
                executeAsJson(getRequestBuilder(ALL_EMAILS_PATH).get()).readResponse(InternalManagementV1SubscriptionsEmailsGETSchema.class);
        assumeThat(SUCCESS_MESSAGE, result, expectSuccess());
        return result.getResponse();
    }

    @Step("Получить список подписок")
    public List<Subscription> getSubscriptions() {
        InternalManagementV1SubscriptionsListGETSchema result =
                executeAsJson(getRequestBuilder(SUBSCRIPTIONS_LIST).get()).readResponse(InternalManagementV1SubscriptionsListGETSchema.class);
        assumeThat(SUCCESS_MESSAGE, result, expectSuccess());
        return result.getSubscriptions();
    }

    @Step("Получить список подписок для другого пользователя")
    public List<Subscription> getSubscriptions(long targetUid) {
        InternalManagementV1SubscriptionsListGETSchema result =
                executeAsJson(getRequestBuilder(SUBSCRIPTIONS_LIST).get(new FreeFormParameters().append("uid", targetUid))).readResponse(InternalManagementV1SubscriptionsListGETSchema.class);
        assumeThat(SUCCESS_MESSAGE, result, expectSuccess());
        return result.getSubscriptions();
    }

    @Step("Получить список подписок для другого пользователя")
    public List<Subscription> getSubscriptionsAndExpectError(long targetUid, IExpectedError error) {
        InternalManagementV1SubscriptionsListGETSchema result =
                executeAsJson(getRequestBuilder(SUBSCRIPTIONS_LIST).get(new FreeFormParameters().append("uid", targetUid))).readResponse(InternalManagementV1SubscriptionsListGETSchema.class);
        assumeThat(ERROR_MESSAGE, result, expectError(error));
        return result.getSubscriptions();
    }

    @Step("Изменить подписку")
    public Subscription changeSubscription(SubscriptionType type, boolean enabled,
                                           SubscriptionListType listType, List<Long> counterIds) {
        return changeSubscription(type, enabled, listType, counterIds, Optional.empty(), SUCCESS_MESSAGE, expectSuccess());
    }
    @Step("Изменить подписку и ожидать ошибку")
    public Subscription changeSubscriptionAndExpectError(SubscriptionType type, boolean enabled,
                                           SubscriptionListType listType, List<Long> counterIds, IExpectedError error) {
        return changeSubscription(type, enabled, listType, counterIds, Optional.empty(), ERROR_MESSAGE, expectError(error));
    }
    @Step("Изменить подписку для другого пользователя")
    public Subscription changeSubscription(long targetUid, SubscriptionType type, boolean enabled,
                                           SubscriptionListType listType, List<Long> counterIds) {
        return changeSubscription(type, enabled, listType, counterIds, Optional.of(targetUid), SUCCESS_MESSAGE, expectSuccess());
    }
    @Step("Изменить подписку и ожидать ошибку для другого пользователя")
    public Subscription changeSubscriptionAndExpectError(long targetUid, SubscriptionType type, boolean enabled,
                                           SubscriptionListType listType, List<Long> counterIds, IExpectedError error) {
        return changeSubscription(type, enabled, listType, counterIds, Optional.of(targetUid), ERROR_MESSAGE, expectError(error));
    }

    private Subscription changeSubscription(SubscriptionType type, boolean enabled,
                                           SubscriptionListType listType, List<Long> counterIds, Optional<Long> targetUid, String message, Matcher matcher) {
        final InternalManagementV1SubscriptionsSubscriptionPOSTRequestSchema schema =
                new InternalManagementV1SubscriptionsSubscriptionPOSTRequestSchema()
                .withSubscription(new AddSubscriptionWrapperInnerAddSubscription()
                        .withType(type)
                        .withEnabled(enabled)
                        .withSubscriptionListType(listType)
                        .withUserAgent(TEST_USER_AGENT)
                        .withCounterIds(counterIds)
                );
        final FreeFormParameters[] uids =
                targetUid.map(u -> new FreeFormParameters[]{new FreeFormParameters().append("uid", u)}).orElse(new FreeFormParameters[0]);
        InternalManagementV1SubscriptionsSubscriptionPOSTSchema result = executeAsJson(getRequestBuilder(SUBSCRIPTION_CHANGE).post(schema, uids))
                        .readResponse(InternalManagementV1SubscriptionsSubscriptionPOSTSchema.class);
        assumeThat(message, result, matcher);
        return result.getSubscription();
    }

    public Optional<ILock> getLock() {
        return hazelcastInstance.map(h -> {
            final ILock lock = h.getLock("subscription");
            lock.lock(1, TimeUnit.MINUTES);
            return lock;
        });
    }
}
