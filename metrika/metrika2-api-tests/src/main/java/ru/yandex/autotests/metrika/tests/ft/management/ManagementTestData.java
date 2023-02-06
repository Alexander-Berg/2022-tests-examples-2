package ru.yandex.autotests.metrika.tests.ft.management;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import javax.annotation.Nonnull;

import org.apache.commons.lang.StringUtils;

import ru.yandex.autotests.httpclient.lite.core.IFormParameters;
import ru.yandex.autotests.irt.testutils.RandomUtils;
import ru.yandex.autotests.metrika.beans.schemes.AddGrantRequestObjectWrapper;
import ru.yandex.autotests.metrika.beans.schemes.ClientSettingsObjectWrapper;
import ru.yandex.autotests.metrika.beans.schemes.CounterFullObjectWrapper;
import ru.yandex.autotests.metrika.beans.schemes.CounterGrantRequestObjectWrapper;
import ru.yandex.autotests.metrika.beans.schemes.NotificationObjectWrapper;
import ru.yandex.autotests.metrika.commons.response.IExpectedError;
import ru.yandex.autotests.metrika.data.common.actions.EditAction;
import ru.yandex.autotests.metrika.data.common.users.User;
import ru.yandex.autotests.metrika.data.common.users.Users;
import ru.yandex.autotests.metrika.data.parameters.FreeFormParameters;
import ru.yandex.autotests.metrika.errors.ManagementError;
import ru.yandex.metrika.api.management.client.AddGrantRequest;
import ru.yandex.metrika.api.management.client.AddGrantRequestInnerAddRequestType;
import ru.yandex.metrika.api.management.client.ClientSettings;
import ru.yandex.metrika.api.management.client.counter.CounterFlags;
import ru.yandex.metrika.api.management.client.external.CodeOptionsE;
import ru.yandex.metrika.api.management.client.external.CounterFull;
import ru.yandex.metrika.api.management.client.external.CounterGrantRequest;
import ru.yandex.metrika.api.management.client.external.CounterMirrorE;
import ru.yandex.metrika.api.management.client.external.CounterSource;
import ru.yandex.metrika.api.management.client.external.CounterType;
import ru.yandex.metrika.api.management.client.external.GrantE;
import ru.yandex.metrika.api.management.client.external.GrantType;
import ru.yandex.metrika.api.management.client.external.MonitoringOptionsE;
import ru.yandex.metrika.api.management.client.external.OfflineOptions;
import ru.yandex.metrika.api.management.client.external.PublisherOptions;
import ru.yandex.metrika.api.management.client.external.PublisherSchema;
import ru.yandex.metrika.api.management.client.external.WebvisorOptions;
import ru.yandex.metrika.api.management.client.external.goals.ActionGoal;
import ru.yandex.metrika.api.management.client.external.goals.ButtonGoal;
import ru.yandex.metrika.api.management.client.external.goals.CallGoal;
import ru.yandex.metrika.api.management.client.external.goals.CompositeGoal;
import ru.yandex.metrika.api.management.client.external.goals.ConditionalGoal;
import ru.yandex.metrika.api.management.client.external.goals.DepthGoal;
import ru.yandex.metrika.api.management.client.external.goals.EmailGoal;
import ru.yandex.metrika.api.management.client.external.goals.FileGoal;
import ru.yandex.metrika.api.management.client.external.goals.FormGoal;
import ru.yandex.metrika.api.management.client.external.goals.GoalCondition;
import ru.yandex.metrika.api.management.client.external.goals.GoalConditionOperator;
import ru.yandex.metrika.api.management.client.external.goals.GoalConditionType;
import ru.yandex.metrika.api.management.client.external.goals.GoalE;
import ru.yandex.metrika.api.management.client.external.goals.GoalType;
import ru.yandex.metrika.api.management.client.external.goals.MessengerGoal;
import ru.yandex.metrika.api.management.client.external.goals.PaymentSystemGoal;
import ru.yandex.metrika.api.management.client.external.goals.PhoneGoal;
import ru.yandex.metrika.api.management.client.external.goals.SiteSearchGoal;
import ru.yandex.metrika.api.management.client.external.goals.SocialNetworkGoal;
import ru.yandex.metrika.api.management.client.external.goals.UrlGoal;
import ru.yandex.metrika.api.management.client.external.goals.call.CallGoalCondition;
import ru.yandex.metrika.api.management.client.external.goals.call.CallGoalField;
import ru.yandex.metrika.api.management.client.external.goals.call.ConditionalCallGoal;
import ru.yandex.metrika.api.management.client.filter.FilterAction;
import ru.yandex.metrika.api.management.client.filter.FilterAttribute;
import ru.yandex.metrika.api.management.client.filter.FilterE;
import ru.yandex.metrika.api.management.client.filter.FilterStatus;
import ru.yandex.metrika.api.management.client.filter.FilterType;
import ru.yandex.metrika.api.management.client.label.Label;
import ru.yandex.metrika.api.management.client.notification.Notification;
import ru.yandex.metrika.api.management.client.operation.OperationAttribute;
import ru.yandex.metrika.api.management.client.operation.OperationE;
import ru.yandex.metrika.api.management.client.operation.OperationStatus;
import ru.yandex.metrika.api.management.client.operation.OperationType;
import ru.yandex.metrika.api.management.client.segments.Segment;
import ru.yandex.metrika.rbac.Permission;
import ru.yandex.metrika.util.wrappers.OperationWrapper;

import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.collection.LambdaCollections.with;
import static com.google.common.collect.ImmutableList.of;
import static java.lang.String.format;
import static java.util.Arrays.asList;
import static java.util.Collections.singletonList;
import static java.util.stream.Collectors.toList;
import static java.util.stream.Stream.generate;
import static org.apache.commons.lang3.ArrayUtils.toArray;
import static ru.yandex.autotests.irt.testutils.RandomUtils.getRandomInteger;
import static ru.yandex.autotests.irt.testutils.RandomUtils.getString;
import static ru.yandex.autotests.metrika.data.common.users.User.LOGIN;
import static ru.yandex.autotests.metrika.data.common.users.Users.SIMPLE_USER;
import static ru.yandex.autotests.metrika.data.common.users.Users.SUPER_USER;
import static ru.yandex.autotests.metrika.filters.Term.dimension;

/**
 * Created by omaz on 30.10.14.
 */
public class ManagementTestData {

    private static final String COUNTER_BASE_NAME = "Тестовый счётчик Метрики ";
    private static final String LABEL_BASE_NAME = "Тестовая метка Метрики ";
    private static final String BASE_DOMAIN = ".ru";
    private static final String BASE_MIRROR_DOMAIN = ".mirror";

    private static final String SEGMENT_BASE_NAME = "Тестовый сегмент ";
    private static final String GOAL_BASE_NAME = "Тестовая цель ";
    private static final String DEFAULT_SEGMENT_EXPRESSION =
            "ym:s:regionCityName=='Москва' OR ym:s:regionCityName=='Санкт-Петербург'";
    private static final String INTERNAL_DIMENSION_NAME = "ym:s:directBannerText";
    private static final String PRIVATE_DIMENSION_NAME = "ym:s:searchPhrase";

    private static final String DEFAULT_SELECTOR = ".ya-phone";
    private static final String DEFAULT_PHONE_TEMPLATE = "{full_phone}";
    private static final List<String> DEFAULT_DN_CODES = of("495", "498", "499", "800", "812", "831", "846");
    private static final String DEFAULT_COUNTRY_CODE = "7";

    private static final int RANDOM_STRING_LENGTH = 10;

    private static final int GOALS_LIMIT = 200;
    private static final int FILTERS_LIMIT = 30;
    private static final int OPERATIONS_LIMIT = 30;

    private static final int PARTNER_ID_BASE = 10_000_000;
    private static final int PARTNER_ID_RANGE = 10_000_000;

    private static final Map<String, Permission> permissionMap;
    public static final int MAX_COUNTERS_ON_UID = 100;

    static {
        permissionMap = new HashMap<>();
        permissionMap.put("RW", Permission.EDIT);
        permissionMap.put("RO", Permission.VIEW);
    }


    public static String getCounterName() {
        return getCounterName(COUNTER_BASE_NAME);
    }

    public static String getCounterName(String baseName) {
        return baseName + getString(RANDOM_STRING_LENGTH);
    }

    public static String getLabelName() {
        return LABEL_BASE_NAME + getString(RANDOM_STRING_LENGTH);
    }

    public static String getCounterSite() {
        return getString(RANDOM_STRING_LENGTH).toLowerCase() + BASE_DOMAIN;
    }

    public static String getCounterMirror() {
        return getString(RANDOM_STRING_LENGTH).toLowerCase() + BASE_MIRROR_DOMAIN;
    }

    public static String getCounterSiteWithPath() {
        return getCounterSite() + "/" + getString(RANDOM_STRING_LENGTH) + "/" + getString(RANDOM_STRING_LENGTH);
    }

    public static String getCounterSiteWithUnderscore() {
        return getString(RANDOM_STRING_LENGTH).toLowerCase() + "_" + getString(RANDOM_STRING_LENGTH).toLowerCase() + BASE_DOMAIN;
    }

    public static String getSegmentName() {
        return SEGMENT_BASE_NAME + getString(RANDOM_STRING_LENGTH);
    }

    public static String getSegmentName(int length) {
        return getString(length);
    }

    public static String getGoalName() {
        return GOAL_BASE_NAME + getString(RANDOM_STRING_LENGTH);
    }

    public static CounterFull getDefaultCounter() {
        return new CounterFull()
                .withName(getCounterName())
                .withSite(getCounterSite());
    }

    public static CounterFull getDefaultCounterWithMirror() {
        return new CounterFull()
                .withName(getCounterName())
                .withSite(getCounterSite())
                .withMirrors(singletonList(getCounterMirror()))
                .withMirrors2(null);
    }

    public static List<CounterFull> getDefaultCounters(int numberOfCounters) {
        List<CounterFull> result = new ArrayList<>();
        for (int i = 0; i < numberOfCounters; i++) {
            result.add(getDefaultCounter());
        }
        return result;
    }

    public static CounterFull getDefaultCounterWithPublicStatPermission() {
        return new CounterFull()
                .withName(getCounterName("счетчик с публичным доступом "))
                .withSite(getCounterSite())
                .withGrants(
                        asList(new GrantE()
                                .withPerm(GrantType.PUBLIC_STAT)
                        ));
    }

    public static CounterFull getDefaultCounterWithEditPermission(User user) {
        return new CounterFull()
                .withName(getCounterName(String.format("счетчик с доступом на редактирование пользователя %s ", user)))
                .withSite(getCounterSite())
                .withGrants(
                        asList(new GrantE()
                                .withUserLogin(user.get(LOGIN))
                                .withPerm(GrantType.EDIT)
                        )
                );
    }

    public static CounterFull getDefaultCounterWithViewPermission(User... user) {
        return new CounterFull()
                .withName(getCounterName(String.format("счетчик с доступом на просмотр пользователя %s ", Arrays.toString(user))))
                .withSite(getCounterSite())
                .withGrants(Arrays.stream(user).map(u ->
                        new GrantE().withUserLogin(u.get(LOGIN)).withPerm(GrantType.VIEW)).collect(toList()));
    }

    public static CounterFull getDefaultCounterWithPermissions(User userWithReadPermission, User userWithWritePermission) {
        return getDefaultCounterWithPermissions(of(userWithReadPermission), of(userWithWritePermission));
    }

    public static CounterFull getDefaultCounterWithPermissions(User userWithReadPermission, User userWithWritePermission, boolean partnerDataAccess) {
        return getDefaultCounterWithPermissions(of(userWithReadPermission), of(userWithWritePermission), partnerDataAccess);
    }

    public static CounterFull getDefaultCounterWithPermissions(List<User> userWithReadPermission, List<User> userWithWritePermission) {
        return getDefaultCounterWithPermissions(userWithReadPermission, userWithWritePermission, false);
    }

    public static CounterFull getDefaultCounterWithPermissions(List<User> userWithReadPermission, List<User> userWithWritePermission, boolean partnerDataAccess) {
        return getDefaultCounter().withGrants(Stream.concat(
                userWithReadPermission.stream()
                        .map(user -> new GrantE().withUserLogin(user.get(LOGIN)).withPerm(GrantType.VIEW).withPartnerDataAccess(partnerDataAccess)),
                userWithWritePermission.stream()
                        .map(user -> new GrantE().withUserLogin(user.get(LOGIN)).withPerm(GrantType.EDIT))
        ).collect(Collectors.toList()));
    }

    public static CounterFull getCounterWithBasicParameters() {
        return new CounterFull()
                .withName(getCounterName("Простой счетчик "))
                .withSite(getCounterSite())
                .withFilterRobots(1L)
                .withTimeZoneName("Asia/Yekaterinburg")
                .withVisitThreshold(2400L);
    }

    public static CounterFull getCounterWithWrongTimezone() {
        return getCounterWithBasicParameters()
                .withTimeZoneName("Asia/Kolkata");
    }

    public static CounterFull getPartnerCounter() {
        return getCounterWithBasicParameters()
                .withType(CounterType.PARTNER)
                .withName("Счетчик РСЯ")
                .withPartnerId(getPartnerId());
    }

    public static CounterFull getTurbodirectCounter() {
        return getCounterWithBasicParameters()
                .withName("Счетчик Турбодирект")
                .withSource(CounterSource.TURBODIRECT);
    }

    private static long getPartnerId() {
        return PARTNER_ID_BASE + RandomUtils.getNextInt(PARTNER_ID_RANGE);
    }

    public static CounterFull getCounterWithOperation() {
        return getCounterWithBasicParameters()
                .withOperations(asList(getDefaultOperation()))
                .withName((getCounterName("Счетчик c операцией ")));
    }

    public static CounterFull getCounterWithOperations(List<OperationE> operations) {
        return getCounterWithBasicParameters()
                .withOperations(operations)
                .withName((getCounterName("Счетчик c операцией ")));
    }

    public static CounterFull getCounterWithPathInSite() {
        String site = getCounterSiteWithPath();

        return getCounterWithBasicParameters()
                .withSite(site)
                .withName("Счетчик с доменом " + site);
    }

    public static CounterFull getCounterWithUnderscoreInSite() {
        String site = getCounterSiteWithUnderscore();

        return getCounterWithBasicParameters()
                .withSite(site)
                .withName("Счетчик с доменом c '_' " + site);
    }

    public static CounterFull getCounterWithPathInMirrors() {
        String site = getCounterSiteWithPath();

        return getCounterWithBasicParameters()
                .withMirrors(asList(site))
                .withMirrors2(null)
                .withName("Счетчик другим доменом " + site);
    }

    public static CounterFull getCounterWithUnderscoreInMirrors() {
        String site = getCounterSiteWithUnderscore();

        return getCounterWithBasicParameters()
                .withMirrors(asList(site))
                .withMirrors2(null)
                .withName("Счетчик другим доменом c '_' " + site);
    }

    public static CounterFull getCounterWithEmptySite() {
        return getCounterWithBasicParameters().withSite(StringUtils.EMPTY);
    }

    public static CounterFull getCounterWithOfflineConversionExtendedThresholdEnabled() {
        return getCounterWithBasicParameters()
                .withOfflineOptions(new OfflineOptions()
                        .withOfflineConversionExtendedThreshold(1L))
                .withName("Счетчик с увеличенным периодом учёта конверсий");
    }

    public static CounterFull getCounterWithOfflineCallsExtendedThresholdEnabled() {
        return getCounterWithBasicParameters()
                .withOfflineOptions(new OfflineOptions()
                        .withOfflineCallsExtendedThreshold(1L))
                .withName("Счетчик с увеличенным периодом учёта звонков");
    }

    public static CounterFull getCounterWithGdprAgreementAccepted(boolean gdprAgreementAccepted) {
        return getDefaultCounter()
                .withGdprAgreementAccepted(gdprAgreementAccepted ? 1L : 0L);
    }

    public static CounterFull getCounterWithExistsNameAndSite() {
        return getCounterWithBasicParameters()
                .withName("ExistsCountersName")
                .withSite("existscounterssite.com");
    }

    public static CounterFull getCounterWithExistsNameAndSiteAsMirror() {
        return getCounterWithBasicParameters()
                .withName("ExistsCountersName")
                .withMirrors(asList("anything.com", "existscounterssite.com"));
    }

    public static CounterFull getCounterWithSourceAndExistsNameAndSite(CounterSource counterSource) {
        return getCounterWithExistsNameAndSite()
                .withSource(counterSource);
    }

    public static CounterFull getCounterWithDirectAllowUseGoalsWithoutAccess() {
        return getDefaultCounter()
                .withCounterFlags(new CounterFlags().withDirectAllowUseGoalsWithoutAccess(true));
    }


    private static ConditionalGoal getConditionalGoal() {
        return new ConditionalGoal()
                .withConditions(asList(new GoalCondition()
                        .withType(GoalConditionType.CONTAIN)
                        .withUrl("basket"))).withType(GoalType.URL)
                .withName(getGoalName());
    }

    public static UrlGoal getURLGoal() {
        return getURLGoal(GoalConditionType.CONTAIN, "cart");
    }

    public static UrlGoal getURLGoal(GoalConditionType type, int urlLen) {
        return getURLGoal(type, RandomUtils.getString(urlLen));
    }

    public static UrlGoal getURLGoal(GoalConditionType type, String url) {
        return new UrlGoal()
                .withConditions(asList(
                        new GoalCondition()
                                .withType(type)
                                .withUrl(url)))
                .withName(format("Цель с условием типа %s длины %d", type, url.length()))
                .withType(GoalType.URL);
    }

    public static DepthGoal getNumberGoal() {
        return new DepthGoal()
                .withDepth(3L)
                .withName(getGoalName())
                .withType(GoalType.NUMBER);
    }

    public static CompositeGoal getStepGoal() {
        return new CompositeGoal()
                .withSteps(asList(getConditionalGoal(), getConditionalGoal()))
                .withName(getGoalName())
                .withType(GoalType.STEP);
    }

    public static ActionGoal getActionGoalWithDefaultPrice(double defaultPrice) {
        return getActionGoal()
                .withName(getGoalName() + "(со стоимостью по умолчанию)")
                .withDefaultPrice(defaultPrice);
    }

    public static ActionGoal getActionGoal() {
        return new ActionGoal()
                .withConditions(asList(
                        new GoalCondition()
                                .withType(GoalConditionType.EXACT)
                                .withUrl("cart")))
                .withName(getGoalName())
                .withType(GoalType.ACTION);
    }

    public static CallGoal getCallGoal() {
        return new CallGoal()
                .withType(GoalType.CALL)
                .withName(getGoalName());
    }

    public static EmailGoal getEmailGoal() {
        return new EmailGoal()
                .withType(GoalType.EMAIL)
                .withName(getGoalName());
    }

    public static FormGoal getFormGoal() {
        return new FormGoal()
                .withType(GoalType.FORM)
                .withName(getGoalName());
    }

    public static SiteSearchGoal getSiteSearchGoal() {
        return new SiteSearchGoal()
                .withType(GoalType.SEARCH)
                .withName(getGoalName());
    }

    public static SiteSearchGoal getSiteSearchGoal(int urlLen) {
        return getSiteSearchGoal(RandomUtils.getString(urlLen));
    }

    public static SiteSearchGoal getSiteSearchGoal(String url) {
        return getSiteSearchGoal().withConditions(
                asList(new GoalCondition().withType(GoalConditionType.SEARCH).withUrl(url))
        );
    }

    public static MessengerGoal getMessengerGoal() {
        return new MessengerGoal()
                .withType(GoalType.MESSENGER)
                .withName(getGoalName());
    }

    public static PaymentSystemGoal getPaymentSystemGoal() {
        return new PaymentSystemGoal()
                .withType(GoalType.PAYMENT_SYSTEM)
                .withName(getGoalName());
    }

    public static SocialNetworkGoal getSocialNetworkGoal() {
        return new SocialNetworkGoal()
                .withType(GoalType.SOCIAL)
                .withName(getGoalName());
    }

    public static FileGoal getFileGoal() {
        return new FileGoal()
                .withType(GoalType.FILE)
                .withName(getGoalName());
    }

    public static FileGoal getFileGoal(int urlLen) {
        return getFileGoal(RandomUtils.getString(urlLen));
    }

    public static FileGoal getFileGoal(String url) {
        return getFileGoal().withConditions(
                asList(new GoalCondition().withType(GoalConditionType.FILE).withUrl(url))
        );
    }

    public static ButtonGoal getButtonGoal() {
        return new ButtonGoal()
                .withType(GoalType.BUTTON)
                .withName(getGoalName());
    }

    public static MessengerGoal getMessengerGoalWithWrongConditionType() {
        return new MessengerGoal()
                .withType(GoalType.MESSENGER)
                .withName(getGoalName())
                .withConditions(
                        Arrays.asList(
                                new GoalCondition().withType(GoalConditionType.EXACT).withUrl("whatsapp")
                        )
                );
    }

    public static SocialNetworkGoal getSocialNetworkGoalWithWrongConditionType() {
        return new SocialNetworkGoal()
                .withType(GoalType.SOCIAL)
                .withName(getGoalName())
                .withConditions(
                        Arrays.asList(
                                new GoalCondition().withType(GoalConditionType.EXACT).withUrl("whatsapp")
                        )
                );
    }

    public static FileGoal getFileGoalWithWrongConditionType() {
        return new FileGoal()
                .withType(GoalType.FILE)
                .withName(getGoalName())
                .withConditions(
                        Arrays.asList(
                                new GoalCondition().withType(GoalConditionType.EXACT).withUrl("file.png")
                        )
                );
    }

    public static MessengerGoal getMessengerGoalWithWrongConditionValue() {
        return new MessengerGoal()
                .withType(GoalType.MESSENGER)
                .withName(getGoalName())
                .withConditions(
                        Arrays.asList(
                                new GoalCondition().withType(GoalConditionType.MESSENGER).withUrl("blablabla")
                        )
                );
    }

    public static SocialNetworkGoal getSocialNetworkGoalWithWrongConditionValue() {
        return new SocialNetworkGoal()
                .withType(GoalType.SOCIAL)
                .withName(getGoalName())
                .withConditions(
                        Arrays.asList(
                                new GoalCondition().withType(GoalConditionType.SOCIAL).withUrl("blablabla")
                        )
                );
    }

    public static PhoneGoal getPhoneGoal() {
        return new PhoneGoal()
                .withType(GoalType.PHONE)
                .withName(getGoalName());
    }

    public static EmailGoal getEmailGoalWithActionCondition() {
        return getEmailGoal()
                .withConditions(Collections.singletonList(new GoalCondition().withType(GoalConditionType.ACTION).withUrl("asd")));
    }

    public static UrlGoal getUrlGoallWithFormXpathCondition() {
        return getURLGoal()
                .withConditions(Collections.singletonList(new GoalCondition().withType(GoalConditionType.FORM_XPATH).withUrl("asd")));
    }

    public static UrlGoal getUrlGoalWithContainActionConditions() {
        return getURLGoal()
                .withConditions(
                        Collections.singletonList(
                                new GoalCondition().withType(GoalConditionType.CONTAIN_ACTION).withUrl("asd")
                        )
                );
    }

    public static UrlGoal getUrlGoalWithRegexpActionConditions() {
        return getURLGoal()
                .withConditions(
                        Collections.singletonList(
                                new GoalCondition().withType(GoalConditionType.REGEXP_ACTION).withUrl("asd")
                        )
                );
    }

    public static GoalE getGoalWithoutName() {
        return getURLGoal().withName(null);
    }

    public static GoalE getGoalWithEmptyName() {
        return getURLGoal().withName("");
    }

    public static GoalE getCompositeGoalWithStepWithoutName() {
        return new CompositeGoal()
                .withName(getGoalName())
                .withType(GoalType.STEP)
                .withSteps(singletonList(getURLGoal().withName(null)));
    }

    public static GoalE getCompositeGoalWithStepWithEmptyName() {
        return new CompositeGoal()
                .withName(getGoalName())
                .withType(GoalType.STEP)
                .withSteps(singletonList(getURLGoal().withName("")));
    }

    public static CounterFull getCounterWithGoals(GoalE firstGoal,
                                                  GoalE... optionalGoals) {
        List<GoalE> goals = new ArrayList<>();
        goals.add(firstGoal);
        String counterWithGoals = format("Счетчик с целью типа %s ", firstGoal.getType());

        if (optionalGoals.length > 0) {
            goals.addAll(asList(optionalGoals));
            counterWithGoals = format("Счетчик с целями типов %s ",
                    with(goals).extract(on(GoalE.class).getType()).join(", "));
        }

        return new CounterFull()
                .withName(getCounterName(counterWithGoals))
                .withSite(getCounterSite())
                .withGoals(goals);
    }

    public static CounterFull getCounterWithGoalsWithDefaultPrice(GoalE firstGoal,
                                                                  GoalE... optionalGoals) {
        CounterFull counter = getCounterWithGoals(firstGoal, optionalGoals);
        counter.withName(counter.getName() + "(Со стоимостью по умолчанию)");
        return counter;
    }

    public static CounterFull getCounterWithGoals(List<GoalE> goals) {
        return new CounterFull()
                .withName(getCounterName(format("Счетчик с %s целями", goals.size())))
                .withSite(getCounterSite())
                .withGoals(goals);
    }

    public static CounterFull getCounterWithFilters(List<FilterE> filters) {
        return new CounterFull()
                .withName(getCounterName(format("Счетчик с %s фильтрами", filters.size())))
                .withSite(getCounterSite())
                .withFilters(filters);
    }

    public static CounterFull getCounterWithClickMap(Long clickMap) {
        return new CounterFull()
                .withName(getCounterName(format("Счетчик с параметром click_map %s ", clickMap)))
                .withSite(getCounterSite())
                .withCodeOptions(new CodeOptionsE()
                        .withClickmap(clickMap));
    }

    public static CounterFull getCounterWithAlternativeCdn(Long alternativeCdn) {
        return new CounterFull()
                .withName(getCounterName(format("Счетчик с параметром alternative_cdn %s ", alternativeCdn)))
                .withSite(getCounterSite())
                .withCodeOptions(new CodeOptionsE()
                        .withAlternativeCdn(alternativeCdn));
    }

    public static CounterFull getCounterWithEcommerce(Long ecommerce) {
        return new CounterFull()
                .withName(getCounterName(format("Счетчик с параметром ecommerce %s ", ecommerce)))
                .withSite(getCounterSite())
                .withCodeOptions(new CodeOptionsE()
                        .withEcommerce(ecommerce));
    }

    public static CounterFull getCounterWithEcommerceObject(String ecommerceObject) {
        return new CounterFull()
                .withName(getCounterName(format("Счетчик с параметром ecommerce_object '%s' ", ecommerceObject)))
                .withSite(getCounterSite())
                .withCodeOptions(new CodeOptionsE()
                        .withEcommerce(1L)
                        .withEcommerceObject(ecommerceObject));
    }

    public static CounterFull getCounterWithEcommerceObject(int ecommerceObjectLength) {
        return new CounterFull()
                .withName(getCounterName(format("Счетчик с параметром ecommerce_object длиной %s ",
                        ecommerceObjectLength)))
                .withSite(getCounterSite())
                .withCodeOptions(new CodeOptionsE()
                        .withEcommerce(1L)
                        .withEcommerceObject(getString(ecommerceObjectLength)));
    }

    public static CounterFull getCounterWithOnePhone(Long enableMonitorings, Long enableSms) {
        return new CounterFull()
                .withName(getCounterName("счетчик с одним телефоном "))
                .withSite(getCounterSite())
                .withMonitoring(new MonitoringOptionsE()
                        .withEnableMonitoring(enableMonitorings)
                        .withEnableSms(enableSms)
                        // +78120344567
                        .withPossiblePhones(asList("+7000*****67"))
                        .withPossiblePhoneIds(asList(119189721L))
                        .withPhones(asList("+7000*****67"))
                        .withPhoneIds(asList(119189721L))
                        .withSmsTime("8-19;8-19;8-19;8-19;8-19;8-19;8-19"));
    }

    public static CounterFull getCounterWithTwoPhones(Long enableMonitorings, Long enableSms) {
        return new CounterFull()
                .withName(getCounterName("счетчик с двумя телефонами "))
                .withSite(getCounterSite())
                .withMonitoring(new MonitoringOptionsE()
                        .withEnableMonitoring(enableMonitorings)
                        .withEnableSms(enableSms)
                        // +78120344573 +78120344572
                        .withPossiblePhones(asList("+7000*****72", "+7000*****73"))
                        .withPossiblePhoneIds(asList(119356343L, 119356347L))
                        .withPhones(asList("+7000*****72", "+7000*****73"))
                        .withPhoneIds(asList(119356343L, 119356347L))
                        .withSmsTime("8-19;8-19;8-19;8-19;8-19;8-19;8-19"));
    }

    public static CounterFull getCounterWithOneOfTwoPhones(Long enableMonitorings, Long enableSms) {
        return new CounterFull()
                .withName(getCounterName("счетчик с двумя телефонами "))
                .withSite(getCounterSite())
                .withMonitoring(new MonitoringOptionsE()
                        .withEnableMonitoring(enableMonitorings)
                        .withEnableSms(enableSms)
                        // 78120344573  78120344572
                        .withPossiblePhones(asList("+7000*****72", "+7000*****73"))
                        .withPossiblePhoneIds(asList(119356343L, 119356347L))
                        .withPhones(asList("+7000*****72"))
                        .withPhoneIds(asList(119356343L))
                        .withSmsTime("8-19;8-19;8-19;8-19;8-19;8-19;8-19"));
    }

    public static CounterFull getCounterWithCurrency(Long currency) {
        return getDefaultCounter()
                .withCurrency(currency)
                .withName(getCounterName(format("счетчик с валютой %s ", currency)));
    }

    public static CounterFull getCounterWithTimeZone(String timeZoneName) {
        return getDefaultCounter()
                .withTimeZoneName(timeZoneName)
                .withName(getCounterName(format("счетчик с временной зоной %s ", timeZoneName)));
    }

    public static CounterFull getCounterWithWebVisorUrls(int urlsListStringLenght) {
        return getDefaultCounter()
                .withWebvisor(new WebvisorOptions()
                        .withUrls(getString(urlsListStringLenght)))
                .withName(getCounterName(format("Счетчик со списком URL для сохранения длиной %d ",
                        urlsListStringLenght)));
    }

    public static Label getDefaultLabel() {
        return new Label().withName(ManagementTestData.getLabelName());
    }

    public static List<Label> getDefaultLabels(int count) {
        return generate(ManagementTestData::getDefaultLabel).limit(count).collect(toList());
    }

    public static Segment getDefaultSegment() {
        return new Segment()
                .withName(getSegmentName())
                .withExpression(DEFAULT_SEGMENT_EXPRESSION);
    }

    public static List<Segment> getSegments(int count) {
        return generate(ManagementTestData::getDefaultSegment).limit(count).collect(toList());
    }

    public static Segment getSegmentWithInternalAttribute() {
        return new Segment()
                .withName(getSegmentName())
                .withExpression(dimension(INTERNAL_DIMENSION_NAME).defined().build());
    }

    public static Segment getSegmentWithPrivateAttribute() {
        return new Segment()
                .withName(getSegmentName())
                .withExpression(dimension(PRIVATE_DIMENSION_NAME).defined().build());
    }

    public static UrlGoal getUrlGoalWithConditions(int numberOfConditions) {
        UrlGoal goal = getUrlGoalWithoutConditions();
        goal.setConditions(getConditions(numberOfConditions));
        return goal;
    }

    public static UrlGoal getUrlGoalWithoutConditions() {
        UrlGoal goal = new UrlGoal();
        goal.setName(getGoalName());
        goal.setType(GoalType.URL);
        goal.setIsRetargeting(0L);
        return goal;
    }

    public static ConditionalCallGoal getConditionalCallGoal(CallGoalField field, GoalConditionOperator operator, String value) {
        CallGoalCondition condition = new CallGoalCondition();
        condition.setField(field);
        condition.setType(operator);
        condition.setUrl(value);

        ConditionalCallGoal goal = new ConditionalCallGoal();
        goal.setName(getGoalName());
        goal.setType(GoalType.CONDITIONAL_CALL);
        goal.setIsRetargeting(0L);
        goal.setConditions(singletonList(condition));

        return goal;
    }

    public static ConditionalCallGoal getConditionalCallGoalCallDurationWithoutOperator() {
        return getConditionalCallGoal(CallGoalField.CALL_DURATION, null, "30");
    }

    public static ConditionalCallGoal getConditionalCallGoalCallTagWithInvalidValue() {
        return getConditionalCallGoal(CallGoalField.CALL_DURATION, GoalConditionOperator.EXACT, "\n");
    }

    public static List<GoalE> getGoals(int count) {
        return generate(ManagementTestData::getGoal).limit(count).collect(toList());
    }

    public static List<GoalE> getMaximumGoals() {
        return getGoals(GOALS_LIMIT);
    }

    public static List<GoalE> getMoreThanMaximumGoals() {
        return getGoals(GOALS_LIMIT + 1);
    }

    public static GoalE getGoal() {
        return getUrlGoalWithoutConditions()
                .withConditions(asList(new GoalCondition()
                        .withType(GoalConditionType.CONTAIN)
                        .withUrl(getString(RANDOM_STRING_LENGTH))));
    }

    public static List<FilterE> getFilters(int count) {
        return generate(ManagementTestData::getFilter).limit(count).collect(toList());
    }

    public static List<FilterE> getFiltersWithUniqId(int count) {
        List<FilterE> filters = getFilters(count);
        filters.add(0, new FilterE()
                .withAttr(FilterAttribute.UNIQ_ID)
                .withType(FilterType.ME)
                .withAction(FilterAction.EXCLUDE)
                .withStatus(FilterStatus.ACTIVE));
        return filters;
    }

    public static List<FilterE> getMaximumFilters() {
        return getFiltersWithUniqId(FILTERS_LIMIT);
    }

    public static List<FilterE> getMoreThamMaximumFilters() {
        return getFiltersWithUniqId(FILTERS_LIMIT + 1);
    }

    public static FilterE getFilter() {
        return new FilterE()
                .withAttr(FilterAttribute.TITLE)
                .withType(FilterType.CONTAIN)
                .withValue(getString(RANDOM_STRING_LENGTH))
                .withAction(FilterAction.EXCLUDE)
                .withStatus(FilterStatus.ACTIVE);
    }

    public static OperationE getOperation() {
        return new OperationE()
                .withAttr(OperationAttribute.URL)
                .withValue(getString(RANDOM_STRING_LENGTH))
                .withAction(OperationType.CUT_ALL_PARAMETERS)
                .withStatus(OperationStatus.ACTIVE);
    }

    public static List<OperationE> getOperations(int count) {
        return generate(ManagementTestData::getOperation).limit(count).collect(toList());
    }

    public static List<OperationE> getMaximumOperations() {
        return getOperations(OPERATIONS_LIMIT);
    }

    public static List<OperationE> getMoreThanMaximumOperations() {
        return getOperations(OPERATIONS_LIMIT + 1);
    }

    public static List<GoalCondition> getConditions(int numberOfConditions) {
        List<GoalCondition> conditions = new ArrayList<>();

        for (int i = 0; i < numberOfConditions; i++) {
            conditions.add(new GoalCondition()
                    .withType(GoalConditionType.CONTAIN)
                    .withUrl(getString(6)));
        }

        return conditions;
    }

    public static GrantE getGrant(User grantee) {
        return new GrantE()
                .withUserLogin(grantee.get(LOGIN))
                .withPerm(GrantType.EDIT)
                .withComment(getString(20));
    }

    public static Object[] createAddParam(User user,
                                          CounterFull counterToAdd,
                                          CounterFull expectedCounter) {
        return toArray(user,
                new CounterFullObjectWrapper(counterToAdd),
                new CounterFullObjectWrapper(expectedCounter
                        .withName(counterToAdd.getName())
                        .withSite(counterToAdd.getSite())));
    }

    public static Object[] createAddParam(User user,
                                          CounterFull counterToAdd) {
        return createAddParam(user, counterToAdd, counterToAdd);
    }

    public static Object[] createAddParam(CounterFull counterToAdd, CounterFull expectedCounter) {
        return createAddParam(SIMPLE_USER, counterToAdd, expectedCounter);
    }

    public static Object[] createAddParam(CounterFull counterToAdd) {
        return createAddParam(SIMPLE_USER, counterToAdd);
    }

    public static Object[] createAddNegativeParam(User owner,
                                                  CounterFull counterToAdd,
                                                  IExpectedError expectedError) {
        return toArray(owner, new CounterFullObjectWrapper(counterToAdd), expectedError);
    }

    public static Object[] createAddNegativeParam(CounterFull counterToAdd,
                                                  IExpectedError expectedError) {
        return createAddNegativeParam(SIMPLE_USER, counterToAdd, expectedError);
    }

    public static Object[] createEditParam(User user, CounterFull counter,
                                           EditAction<CounterFull> editAction) {
        return toArray(user, new CounterFullObjectWrapper(counter), editAction);
    }

    public static Object[] createEditParam(CounterFull counter, EditAction<CounterFull> editAction) {
        return createEditParam(SIMPLE_USER, counter, editAction);
    }

    public static Object[] createEditNegativeParam(CounterFull counter,
                                                   EditAction<CounterFull> editAction,
                                                   IExpectedError expectedError) {
        return toArray(new CounterFullObjectWrapper(counter), editAction, expectedError);
    }

    public static Object[] createAddGrantParam(User grantee, GrantE expectedGrant) {
        return toArray(grantee, expectedGrant);
    }

    public static Object[] createAddGrantParam(User grantee) {
        return createAddGrantParam(grantee, getGrant(grantee));
    }

    public static EditAction<CounterFull> getAddOperation() {
        return new EditAction<CounterFull>("добавить операцию") {
            @Override
            public CounterFull edit(CounterFull source) {
                return source.withOperations(asList(getDefaultOperation()));
            }
        };
    }

    public static EditAction<CounterFull> getAddActionGoal() {
        return new EditAction<CounterFull>("добавить цель типа событие") {
            @Override
            public CounterFull edit(CounterFull source) {
                List<GoalE> goals = source.getGoals();
                goals.add(getActionGoal());
                return source.withGoals(goals);
            }
        };
    }

    public static EditAction<CounterFull> getAddNumberGoal() {
        return new EditAction<CounterFull>("добавить цель типа просмотр n страниц") {
            @Override
            public CounterFull edit(CounterFull source) {
                List<GoalE> goals = source.getGoals();
                goals.add(getActionGoal());
                return source.withGoals(goals);
            }
        };
    }

    public static EditAction<CounterFull> getAddStepGoal() {
        return new EditAction<CounterFull>("добавить составную цель") {
            @Override
            public CounterFull edit(CounterFull source) {
                List<GoalE> goals = source.getGoals();
                goals.add(getActionGoal());
                return source.withGoals(goals);
            }
        };
    }

    public static EditAction<CounterFull> getAddUrlGoal() {
        return new EditAction<CounterFull>("добавить цель типа url") {
            @Override
            public CounterFull edit(CounterFull source) {
                List<GoalE> goals = source.getGoals();
                goals.add(getActionGoal());
                return source.withGoals(goals);
            }
        };
    }

    public static EditAction<CounterFull> getAddMaximumGoals() {
        return new EditAction<CounterFull>("добавить максимальное количество целей") {
            @Override
            public CounterFull edit(CounterFull source) {
                List<GoalE> goals = source.getGoals();
                if (goals.size() == 0) {
                    return source.withGoals(getMaximumGoals());
                } else {
                    goals.addAll(getGoals(GOALS_LIMIT - goals.size()));
                    return source.withGoals(goals);
                }
            }
        };
    }

    public static EditAction<CounterFull> getAddMoreThanMaximumGoals() {
        return new EditAction<CounterFull>("добавить целей больше максимального") {
            @Override
            public CounterFull edit(CounterFull source) {
                List<GoalE> goals = source.getGoals();
                if (goals.size() == 0) {
                    return source.withGoals(getMoreThanMaximumGoals());
                } else {
                    goals.addAll(getGoals(GOALS_LIMIT - goals.size()));
                    return source.withGoals(goals);
                }
            }
        };
    }

    public static EditAction<CounterFull> getAddMaximumFilters() {
        return new EditAction<CounterFull>("добавить максимальное количество фильтров") {
            @Override
            public CounterFull edit(CounterFull source) {
                List<FilterE> filters = source.getFilters();
                if (filters.size() == 0) {
                    return source.withFilters(getMaximumFilters());
                } else {
                    filters.addAll(getFiltersWithUniqId(FILTERS_LIMIT - filters.size()));
                    return source.withFilters(filters);
                }
            }
        };
    }

    public static EditAction<CounterFull> getAddMoreThanMaximumFilters() {
        return new EditAction<CounterFull>("добавить фильтров больше максимального") {
            @Override
            public CounterFull edit(CounterFull source) {
                List<FilterE> filters = source.getFilters();
                if (filters.size() == 0) {
                    return source.withFilters(getFiltersWithUniqId(31));
                } else {
                    filters.addAll(getFiltersWithUniqId(31 - filters.size()));
                    return source.withFilters(filters);
                }
            }
        };
    }

    public static EditAction<CounterFull> getAddMaximumOperations() {
        return new EditAction<CounterFull>("добавить максимальное количество операций") {
            @Override
            public CounterFull edit(CounterFull source) {
                List<OperationE> operations = source.getOperations();
                if (operations.size() == 0) {
                    return source.withOperations(getOperations(30));
                } else {
                    operations.addAll(getOperations(30 - operations.size()));
                    return source.withOperations(operations);
                }
            }
        };
    }

    public static EditAction<CounterFull> getAddMoreThanMaximumOperations() {
        return new EditAction<CounterFull>("добавить операций больше максимального") {
            @Override
            public CounterFull edit(CounterFull source) {
                List<OperationE> operations = source.getOperations();
                if (operations.size() == 0) {
                    return source.withOperations(getOperations(31));
                } else {
                    operations.addAll(getOperations(31 - operations.size()));
                    return source.withOperations(operations);
                }
            }
        };
    }

    public static EditAction<CounterFull> getChangeName() {
        final String newName = getCounterName();

        return new EditAction<CounterFull>(format("Сменить наименование на %s", newName)) {
            @Override
            public CounterFull edit(CounterFull source) {
                return source.withName(newName);
            }
        };
    }

    public static EditAction<CounterFull> getChangeSite() {
        final String newSite = getCounterSite();

        return new EditAction<CounterFull>(format("Сменить сайт на %s", newSite)) {
            @Override
            public CounterFull edit(CounterFull source) {
                return source.withSite(newSite);
            }
        };
    }

    public static EditAction<CounterFull> getChangeSiteWithPath() {
        final String newSite = getCounterSiteWithPath();

        return new EditAction<CounterFull>(format("Сменить сайт на %s", newSite)) {
            @Override
            public CounterFull edit(CounterFull source) {
                return source.withSite(newSite);
            }
        };
    }

    public static EditAction<CounterFull> getChangeSiteWithUnderscore() {
        final String newSite = getCounterSiteWithUnderscore();

        return new EditAction<CounterFull>(format("Сменить сайт на %s", newSite)) {
            @Override
            public CounterFull edit(CounterFull source) {
                return source.withSite(newSite);
            }
        };
    }

    public static EditAction<CounterFull> getChangeMirrorsWithPath() {
        final String newMirrors = getCounterSiteWithPath();

        return new EditAction<CounterFull>(format("Сменить дополнительные домены на %s", newMirrors)) {
            @Override
            public CounterFull edit(CounterFull source) {
                return source.withMirrors(asList(newMirrors)).withMirrors2(null);
            }
        };
    }

    public static EditAction<CounterFull> getChangeMirrorsWithUnderscore() {
        final String newMirrors = getCounterSiteWithUnderscore();

        return new EditAction<CounterFull>(format("Сменить дополнительные домены на %s", newMirrors)) {
            @Override
            public CounterFull edit(CounterFull source) {
                return source.withMirrors(asList(newMirrors)).withMirrors2(null);
            }
        };
    }

    public static EditAction<CounterFull> getChangeClickMap(final Long value) {
        return new EditAction<CounterFull>(format("Сменить параметр click_map на %s", value)) {
            @Override
            public CounterFull edit(CounterFull source) {
                source.getCodeOptions().setClickmap(value);
                return source;
            }
        };
    }

    public static EditAction<CounterFull> getChangeEnableMonitoring(final Long value) {
        return new EditAction<CounterFull>(format("Сменить параметр enable_monitoring на %s", value)) {
            @Override
            public CounterFull edit(CounterFull source) {
                source.getMonitoring().setEnableMonitoring(value);
                return source;
            }
        };
    }

    public static EditAction<CounterFull> getChangeAlternativeCdn(final Long value) {
        return new EditAction<CounterFull>(format("Сменить параметр alternative_cdn на %s", value)) {
            @Override
            public CounterFull edit(CounterFull source) {
                source.getCodeOptions().setAlternativeCdn(value);
                return source;
            }
        };
    }

    public static EditAction<CounterFull> getChangeEnableSms(final Long value) {
        return new EditAction<CounterFull>(format("Сменить параметр enable_sms на %s", value)) {
            @Override
            public CounterFull edit(CounterFull source) {
                source.getMonitoring().setEnableSms(value);
                return source;
            }
        };
    }

    public static EditAction<CounterFull> getChangeSmsTime(final String value) {
        return new EditAction<CounterFull>(format("Сменить параметр sms_time на %s", value)) {
            @Override
            public CounterFull edit(CounterFull source) {
                source.getMonitoring().setSmsTime(value);
                return source;
            }
        };
    }

    public static EditAction<CounterFull> getChangePhone(final List<String> value, final List<Long> id) {
        return new EditAction<CounterFull>(format("Сменить параметр phones на %s", value)) {
            @Override
            public CounterFull edit(CounterFull source) {
                source.getMonitoring().setPhones(value);
                source.getMonitoring().setPhoneIds(id);
                return source;
            }
        };
    }

    public static EditAction<CounterFull> getChangeCurrency(final Long value) {
        return new EditAction<CounterFull>(format("Сменить параметр currency на %s", value)) {
            @Override
            public CounterFull edit(CounterFull source) {
                return source.withCurrency(value);
            }
        };
    }

    public static EditAction<CounterFull> getChangeTimeZone(final String value) {
        return new EditAction<CounterFull>(format("Сменить параметр time zone на %s", value)) {
            @Override
            public CounterFull edit(CounterFull source) {
                return source.withTimeZoneName(value);
            }
        };
    }

    public static EditAction<CounterFull> getChangeWebVisorUrls(final int urlsListStringLenght) {
        return new EditAction<CounterFull>(format("Сменить список URL для сохранения на строку длиной %d",
                urlsListStringLenght)) {
            @Override
            public CounterFull edit(CounterFull source) {
                source.setWebvisor(new WebvisorOptions().withUrls(getString(urlsListStringLenght)));
                return source;
            }
        };
    }

    public static EditAction<CounterFull> getChangeEcommerceEnabled(final Long enabled) {
        return new EditAction<CounterFull>(format("Сменить ecommerce_enabled на %d", enabled)) {
            @Override
            public CounterFull edit(CounterFull source) {
                return source.withCodeOptions(
                        (source.getCodeOptions() == null ? new CodeOptionsE() : source.getCodeOptions())
                                .withEcommerce(enabled));
            }
        };
    }

    public static EditAction<CounterFull> getChangeEcommerceObject(final String ecommerceObject) {
        return new EditAction<CounterFull>(format("Сменить ecommerce_object на %s", ecommerceObject)) {
            @Override
            public CounterFull edit(CounterFull source) {
                source.getCodeOptions().setEcommerceObject(ecommerceObject);
                return source;
            }
        };
    }

    public static EditAction<CounterFull> getChangeEcommerceObject(final int length) {
        String ecommerceObject = getString(length);
        return new EditAction<CounterFull>(format("Сменить ecommerce_object на строку длины %d", length)) {
            @Override
            public CounterFull edit(CounterFull source) {
                source.getCodeOptions().setEcommerceObject(ecommerceObject);
                return source;
            }
        };
    }

    public static EditAction<CounterFull> getChangeReverseGoalsOrder() {
        return new EditAction<CounterFull>("Инвертировать порядок целей") {
            @Override
            public CounterFull edit(CounterFull source) {
                List<GoalE> reversedList = new ArrayList<>();

                for (int i = source.getGoals().size() - 1; i >= 0; i--) {
                    reversedList.add(source.getGoals().get(i));
                }

                source.setGoals(reversedList);
                return source;
            }
        };
    }

    public static EditAction<CounterFull> getChangeFavoriteState(long state) {
        return new EditAction<CounterFull>(state == 0 ? "Удалить счетчик из избранных"
                : "Добавить счетчик в избранные") {
            @Override
            public CounterFull edit(CounterFull source) {
                source.setFavorite(state);
                return source;
            }
        };
    }

    public static EditAction<CounterFull> getDeleteGoal() {
        return new EditAction<CounterFull>("удалить цель") {
            @Override
            public CounterFull edit(CounterFull source) {
                List<GoalE> goals = source.getGoals();
                if (goals.size() > 0) {
                    goals.remove(0);
                }
                return source.withGoals(goals);
            }
        };
    }

    public static EditAction<CounterFull> getDeleteAllGoals() {
        return new EditAction<CounterFull>("удалить все цели") {
            @Override
            public CounterFull edit(CounterFull source) {
                return source.withGoals(asList());
            }
        };
    }

    public static EditAction<CounterFull> getRemoveGoalStep() {
        return new EditAction<CounterFull>("Удалить шаг составной цели") {
            @Override
            public CounterFull edit(CounterFull source) {
                List<GoalE> removedStepList = source.getGoals();
                removedStepList.stream().filter(g -> g.getType().equals(GoalType.STEP))
                        .forEach(g -> ((CompositeGoal) g).setSteps(((CompositeGoal) g)
                                .getSteps().stream().skip(1).collect(Collectors.toList())));
                source.setGoals(removedStepList);
                return source;
            }
        };
    }

    public static EditAction<CounterFull> getRemovePublicStatPermission() {
        return new EditAction<CounterFull>("Удалить публичную статистику") {
            @Override
            public CounterFull edit(CounterFull source) {
                source.setGrants(source.getGrants().stream()
                        .filter(g -> !g.getPerm().equals(GrantType.PUBLIC_STAT))
                        .collect(Collectors.toList()));
                return source;
            }
        };
    }

    public static EditAction<CounterFull> getAddPublicStatPermission() {
        return new EditAction<CounterFull>("Добавить публичную статистику") {
            @Override
            public CounterFull edit(CounterFull source) {
                List<GrantE> newGrants = source.getGrants().stream().collect(Collectors.toList());
                newGrants.add(new GrantE().withPerm(GrantType.PUBLIC_STAT));
                source.setGrants(newGrants);
                return source;
            }
        };
    }

    public static EditAction<CounterFull> getEnableOfflineConversionExtendedThreshold() {
        return new EditAction<CounterFull>("Включить увеличенный период учёта конверсий") {
            @Override
            public CounterFull edit(CounterFull source) {
                if (source.getOfflineOptions() == null) {
                    source.setOfflineOptions(new OfflineOptions());
                }
                source.getOfflineOptions().setOfflineConversionExtendedThreshold(1L);
                return source;
            }
        };
    }

    public static EditAction<CounterFull> getEnableOfflineCallsExtendedThreshold() {
        return new EditAction<CounterFull>("Включить увеличенный период учёта звонков") {
            @Override
            public CounterFull edit(CounterFull source) {
                if (source.getOfflineOptions() == null) {
                    source.setOfflineOptions(new OfflineOptions());
                }
                source.getOfflineOptions().setOfflineCallsExtendedThreshold(1L);
                return source;
            }
        };
    }

    public static EditAction<CounterFull> getDisableOfflineConversionExtendedThreshold() {
        return new EditAction<CounterFull>("Выключить увеличенный период учёта конверсий") {
            @Override
            public CounterFull edit(CounterFull source) {
                if (source.getOfflineOptions() == null) {
                    source.setOfflineOptions(new OfflineOptions());
                }
                source.getOfflineOptions().setOfflineConversionExtendedThreshold(0L);
                return source;
            }
        };
    }

    public static EditAction<CounterFull> getDisableOfflineCallsExtendedThreshold() {
        return new EditAction<CounterFull>("Выключить увеличенный период учёта звонков") {
            @Override
            public CounterFull edit(CounterFull source) {
                if (source.getOfflineOptions() == null) {
                    source.setOfflineOptions(new OfflineOptions());
                }
                source.getOfflineOptions().setOfflineCallsExtendedThreshold(0L);
                return source;
            }
        };
    }

    public static EditAction<CounterFull> getAcceptGdprAgreement() {
        return new EditAction<CounterFull>("Принять договор об обработке данных") {
            @Override
            public CounterFull edit(CounterFull source) {
                source.setGdprAgreementAccepted(1L);
                return source;
            }
        };
    }

    public static EditAction<CounterFull> getRejectGdprAgreement() {
        return new EditAction<CounterFull>("Отклонить договор об обработке данных") {
            @Override
            public CounterFull edit(CounterFull source) {
                source.setGdprAgreementAccepted(0L);
                return source;
            }
        };
    }

    public static Object[] createCounterMoveParam(CounterFull counter,
                                                  User mover,
                                                  User recipient,
                                                  String recepientExpectedLogin) {
        return toArray(new CounterFullObjectWrapper(counter), mover, recipient, recepientExpectedLogin);
    }

    public static Object[] createCounterMoveParam(CounterFull counter,
                                                  User mover,
                                                  User recipient) {
        return createCounterMoveParam(counter, mover, recipient, recipient.get(LOGIN));
    }

    public static Object[] createCounterMoveNegativeParamWithCounterLimitExceeded(ManagementError expectedError) {
        return createCounterMoveNegativeParam(getDefaultCounter(), SUPER_USER, Users.USER_WITH_COUNTERS_LIMIT_EXCEEDED, expectedError, FreeFormParameters.EMPTY);
    }

    public static Object[] createCounterMoveNegativeParam(CounterFull counter,
                                                          User mover,
                                                          User recipient,
                                                          ManagementError expectedError) {
        return createCounterMoveNegativeParam(counter, mover, recipient, expectedError, FreeFormParameters.EMPTY);
    }


    public static Object[] createCounterMoveNegativeParam(CounterFull counter,
                                                          User mover,
                                                          User recipient,
                                                          ManagementError expectedError,
                                                          IFormParameters additionalParameters) {
        return toArray(new CounterFullObjectWrapper(counter), mover, recipient, expectedError, additionalParameters);
    }

    public static OperationE getDefaultOperation() {
        return new OperationE()
                .withAction(OperationType.CUT_ALL_PARAMETERS)
                .withAttr(OperationAttribute.URL)
                .withStatus(OperationStatus.ACTIVE);
    }

    public static EditAction<OperationE> getChangeAction(OperationType action) {
        return new EditAction<OperationE>(String.format("сменить тип операции на %s", action)) {
            @Override
            public OperationE edit(OperationE source) {
                return source.withAction(action);
            }
        };
    }

    public static EditAction<OperationE> getChangeAttr(OperationAttribute attr) {
        return new EditAction<OperationE>(String.format("сменить поле для фильтрации на %s", attr)) {
            @Override
            public OperationE edit(OperationE source) {
                return source.withAttr(attr);
            }
        };
    }

    public static EditAction<OperationE> getChangeValue(String value) {
        return new EditAction<OperationE>(String.format("сменить значение для замены на %s", value)) {
            @Override
            public OperationE edit(OperationE source) {
                return source.withValue(value);
            }
        };
    }

    public static EditAction<OperationE> getChangeStatus(OperationStatus status) {
        return new EditAction<OperationE>(String.format("сменить статус операции на %s", status)) {
            @Override
            public OperationE edit(OperationE source) {
                return source.withStatus(status);
            }
        };
    }

    public static EditAction<CounterFull> getChangeSite2(final String site) {
        return new EditAction<CounterFull>(format("Сменить site2 адрес сайта на %s", site)) {
            @Override
            public CounterFull edit(CounterFull source) {
                return source.withSite2(new CounterMirrorE().withSite(site));
            }
        };
    }

    public static EditAction<CounterFull> getChangeMirrors2(final List<String> sites) {
        return new EditAction<CounterFull>(format("Сменить mirrors2 адреса сайтов на %s", sites)) {
            @Override
            public CounterFull edit(CounterFull source) {
                return source.withMirrors2(sites.stream().map(s -> new CounterMirrorE().withSite(s)).collect(toList()));
            }
        };
    }

    public static Object[] createEditParam(OperationE operation, EditAction<OperationE> editAction) {
        return toArray(new OperationWrapper().withOperation(operation), editAction);
    }

    public static Object[] createGrantRequestParam(User owner, User requestor,
                                                   String perimission, String userLogin, User decider) {
        return createGrantRequestParam(owner, requestor, perimission, userLogin, decider, FreeFormParameters.EMPTY);
    }

    public static Object[] createGrantRequestParam(User owner, User requestor,
                                                   String perimission, String userLogin, User decider,
                                                   IFormParameters additionalParameters) {

        AddGrantRequest grantRequest = new AddGrantRequest()
                .withObjectType(AddGrantRequestInnerAddRequestType.COUNTER)
                .withPermission(perimission)
                .withOwnerLogin(owner.get(LOGIN))
                .withRequestorLogin(requestor.get(LOGIN))
                .withComment(getString(RANDOM_STRING_LENGTH));

        return toArray(new AddGrantRequestObjectWrapper(grantRequest),
                getGrantRequestObject(grantRequest).withUserLogin(userLogin), decider,
                additionalParameters);
    }

    public static Object[] createGrantRequestNegativeParam(User owner, User requestor,
                                                           String userLogin, User decider,
                                                           IExpectedError expectedError) {

        AddGrantRequest grantRequest = new AddGrantRequest()
                .withObjectType(AddGrantRequestInnerAddRequestType.COUNTER)
                .withPermission("RW")
                .withOwnerLogin(owner.get(LOGIN))
                .withRequestorLogin(requestor.get(LOGIN))
                .withComment(getString(RANDOM_STRING_LENGTH));

        Object[] tmp = toArray(
                new AddGrantRequestObjectWrapper(grantRequest),
                new CounterGrantRequestObjectWrapper(getGrantRequestObject(grantRequest).withUserLogin(userLogin)),
                decider, expectedError);

        return tmp;
    }

    private static CounterGrantRequest getGrantRequestObject(AddGrantRequest grantRequestObject) {
        return new CounterGrantRequest()
                .withUserLogin(grantRequestObject.getRequestorLogin())
                .withPerm(permissionMap.get(grantRequestObject.getPermission()))
                .withComment(grantRequestObject.getComment());
    }

    public static Object[] createNotificationParam(Notification notification) {
        return toArray(new NotificationObjectWrapper(notification));
    }

    public static Object[] createNotificationParam(Notification notification, String language) {
        return toArray(new NotificationObjectWrapper(notification), language);
    }

    private static String getRandomPhone() {
        return String.valueOf(getRandomInteger(1000000, 10000000));
    }

    public static ClientSettings getDefaultClientSettings() {
        return new ClientSettings()
                .withSubscriptionEmails(0L)
                .withSubscriptionEmailsUnchecked(0L);
    }

    public static ClientSettings getClientSettingsTypeWithoutSubscriptionEmailsAndUnchecked() {
        return new ClientSettings()
                .withSubscriptionEmails(0L)
                .withSubscriptionEmailsUnchecked(1L);
    }

    public static ClientSettings getClientSettingsTypeWithSubscriptionEmails() {
        return new ClientSettings()
                .withSubscriptionEmails(1L)
                .withSubscriptionEmailsUnchecked(0L);
    }

    public static ClientSettings getClientSettingsTypeWithSubscriptionEmailsAndUnchecked() {
        return new ClientSettings()
                .withSubscriptionEmails(1L)
                .withSubscriptionEmailsUnchecked(1L);
    }

    public static Object[] createClientSittingsParam(ClientSettings initialClientSettings,
                                                     ClientSettings newClientSettings,
                                                     ClientSettings expectedClientSettings) {
        return toArray(new ClientSettingsObjectWrapper(initialClientSettings),
                new ClientSettingsObjectWrapper(newClientSettings),
                new ClientSettingsObjectWrapper(expectedClientSettings));
    }

    @Nonnull
    private static PublisherOptions getDefaultPublisherOptions() {
        return new PublisherOptions().withSchemaOptions(Arrays.asList(PublisherSchema.values()));
    }

    public static EditAction<CounterFull> getEnablePublishers() {
        return new EditAction<CounterFull>("Включить сбор данных паблишеров") {
            @Override
            public CounterFull edit(CounterFull source) {
                if (source.getPublisherOptions() == null) {
                    source.setPublisherOptions(getDefaultPublisherOptions());
                }
                source.getPublisherOptions().setEnabled(1L);
                return source;
            }
        };
    }

    public static EditAction<CounterFull> getSetPublishersSchema() {
        return new EditAction<CounterFull>("Выбрать схему сбора данных паблишеров") {
            @Override
            public CounterFull edit(CounterFull source) {
                if (source.getPublisherOptions() == null) {
                    source.setPublisherOptions(getDefaultPublisherOptions().withSchema(PublisherSchema.MICRODATA));
                }
                return source;
            }
        };
    }

    public static EditAction<CounterFull> getDisablePublishers() {
        return new EditAction<CounterFull>("Выключить сбор данных паблишеров") {
            @Override
            public CounterFull edit(CounterFull source) {
                if (source.getPublisherOptions() == null) {
                    source.setPublisherOptions(getDefaultPublisherOptions().withEnabled(0L));
                }
                return source;
            }
        };
    }

    public static EditAction<CounterFull> getSetGoalNullConditions() {
        return new EditAction<CounterFull>("Проставить null в условия цели") {
            @Override
            public CounterFull edit(CounterFull source) {
                ConditionalGoal goal = (ConditionalGoal) source.getGoals().get(0);
                goal.setConditions(null);
                return source;
            }
        };
    }

    public static CounterFull getCounterWithPublisherEnabled() {
        return getCounterWithBasicParameters()
                .withPublisherOptions(getDefaultPublisherOptions()
                        .withEnabled(1L))
                .withName("Счетчик с включенным сбором данных паблишеров");
    }

    public static CounterFull getCounterWithPublisherEnabledAndSchema() {
        return getCounterWithBasicParameters()
                .withPublisherOptions(getDefaultPublisherOptions()
                        .withEnabled(1L).withSchema(PublisherSchema.MICRODATA))
                .withName("Счетчик с включенным сбором данных паблишеров");
    }

}
