package ru.yandex.autotests.metrika.data.common.users;

import static ru.yandex.autotests.metrika.data.common.users.User.OAUTH_TOKEN;
import static ru.yandex.autotests.metrika.data.common.users.User.PASSWORD;
import static ru.yandex.autotests.metrika.data.common.users.User.UID;

/**
 * Created by vananos on 04.08.16.
 */
public final class Users {

    /**
     * Этот пользователь имеет роль super
     */
    public static final User SUPER_USER = new User("yndx-robot-metrika-test-super")
            .putSecret("SUPER_USER")
            .put(UID, 423930842L);
    /**
     * Этот пользователь имеет роль support и используется в тестах API отчетов, для
     * получения отчетов по различным счетчикам
     */
    public static final User SUPPORT = new User("at-metrika-tester")
            .putSecret("SUPPORT");
    /**
     * Этот пользователь имеет роль manager
     */
    public static final User MANAGER = new User("yndx-robot-metrika-test-952840")
            .putSecret("MANAGER");
    /**
     * Этот пользователь имеет роль manager_direct и используется в тестах API отчетов
     * для получения отчетов по различным счетчикам
     */
    public static final User MANAGER_DIRECT = new User("yndx-robot-metrika-test-931937")
            .putSecret("MANAGER_DIRECT");

    /**
     * Этот пользователь имеет роль yamanager и используется в тестах API отчетов
     * для получения отчетов по различным счетчикам и в API управления для проверки прав
     */
    public static final User YAMANAGER = new User("yndx-robot-metrika-test-352883")
            .putSecret("YAMANAGER");

    public static final User SIMPLE_USER = new User("at-metrika")
            .putSecret("SIMPLE_USER")
            .put(UID, 273197151L);

    public static final User SIMPLE_USER2 = new User("at-metrika-2")
            .putSecret("SIMPLE_USER2")
            .put(UID, 288933839L);

    public static final User SIMPLE_USER2_EMAIL = new User("at-metrika-2@yandex.ru")
            .putSecret("SIMPLE_USER2_EMAIL");

    public static final User SIMPLE_USER3 = new User("at-metrika-11")
            .putSecret("SIMPLE_USER3")
            .put(UID, 348348326L);

    public static final User SIMPLE_USER_PDD = new User("at-metrika-pdd-1@konkov.kida-lo-vo.name")
            .putSecret("SIMPLE_USER_PDD");
    /**
     * Используется в тесте на проверку количества счетчиков по группам
     */
    public static final User SIMPLE_USER_GROUP_COUNTERS = new User("api-metrika-test")
            .putSecret("SIMPLE_USER_GROUP_COUNTERS");
    /**
     * Используются в тестах целевого звонка, оферта не принята, балланс 0
     */
    public static final User SIMPLE_USER_WITHOUT_MONEY_1 = new User("at-metrika-31")
            .putSecret("SIMPLE_USER_WITHOUT_MONEY_1");

    public static final User SIMPLE_USER_WITHOUT_MONEY_2 = new User("at-metrika-41")
            .putSecret("SIMPLE_USER_WITHOUT_MONEY_2");
    /**
     * Используются в тестах целевого звонка, оферта принята, имеют положительный балланс
     */
    public static final User SIMPLE_USER_WITH_MONEY_1 = new User("at-metrika-33")
            .putSecret("SIMPLE_USER_WITH_MONEY_1");

    public static final User SIMPLE_USER_WITH_MONEY_2 = new User("at-metrika-32")
            .putSecret("SIMPLE_USER_WITH_MONEY_2");

    /**
     * Этот пользователь используется в тестах с представительским доступом как тот,
     * кто выдал представительский доступ пользователю "at-metrika-35" (USER_DELEGATE_PERMANENT)
     */
    public static final User USER_DELEGATOR = new User("at-metrika-3")
            .putSecret("USER_DELEGATOR");
    /**
     * Этот пользователь используется в AddDelegatesTest как пользователь, который назначает представителей,
     * а также в тестах с представительским доступом как тот,
     * кто выдал представительский доступ пользователю "at-metrika-35" (USER_DELEGATE_PERMANENT)
     */
    public static final User USER_DELEGATOR2 = new User("at-metrika-21")
            .putSecret("USER_DELEGATOR2");
    /**
     * Этот пользователь используется в DelegatesListTest как пользователь, который назначает представителей
     */
    public static final User USER_DELEGATOR3 = new User("at-metrika-22")
            .putSecret("USER_DELEGATOR3");
    /**
     * Этот пользователь используется в DeleteDelegatesTest как пользователь, который назначает представителей
     */
    public static final User USER_DELEGATOR4 = new User("at-metrika-23")
            .putSecret("USER_DELEGATOR4");
    /**
     * Этот пользователь используется в DelegateRequestTest как пользователь, который назначает представителей
     */
    public static final User USER_DELEGATOR5 = new User("at-metrika-20")
            .putSecret("USER_DELEGATOR5");

    /**
     * Этот пользователь используется в тестах привязки меток как пользовтаель которому выдают права
     */
    public static final User USER_GRANTEE = new User("at-metrika-4")
            .putSecret("USER_GRANTEE");
    /**
     * Этот пользователь используется в тестах на управиление представителями
     */
    public static final User USER_DELEGATE = new User("at-metrika-19")
            .putSecret("USER_DELEGATE");
    /**
     * Этот пользователь используется в тестах с представительским доступом,
     * как постоянный представитель пользователя "at-metrika-3" (USER_DELEGATOR), "at-metrika-21" (USER_DELEGATOR2),
     * и "at-metrika-33" (SIMPLE_USER_WITH_MONEY_1) для целевого звонка
     */
    public static final User USER_DELEGATE_PERMANENT = new User("at-metrika-35")
            .putSecret("USER_DELEGATE_PERMANENT");
    /**
     * Этот пользовтаель используется в CountersSortListTest
     * для того, что бы гарантировать размер его списка счетчиков.
     */
    public static final User USER_FOR_COUNTER_LIST = new User("at-metrika-9")
            .putSecret("USER_FOR_COUNTER_LIST");
    /**
     * Этот пользователь используется в SetLabelsOrderTest,
     * чтобы исключить попадание меток из других тестов.
     */
    public static final User USER_FOR_LABELS = new User("at-metrika-14")
            .putSecret("USER_FOR_LABELS");

    /**
     * Этот пользователь используется в GoalsExistenceTest
     * для того гарантированно получать пользователя, у которого нет доступа к каким-то счетчикам.
     */
    public static final User USER_FOR_CHECK_GOALS = new User("at-metrika-44")
            .putSecret("USER_FOR_CHECK_GOALS");

    /**
     * Этот пользователь используется в PermissionBasePositiveTest и PermissionBaseNegativeTest,
     * чтобы гарантировать ему представительский доступ к счетчику TEST_DELEGATE_COUNTER,
     * доступ к просмотру счетчика TEST_VIEW_PERMISSION_COUNTER и
     * доступ к редактированию счетчика TEST_EDIT_PERMISSION_COUNTER..
     */
    public static final User PERMISSION_TEST_USER = new User("at-metrika-24")
            .putSecret("PERMISSION_TEST_USER");

    /**
     * Этот пользователь используется в негативных тестах на nda,
     * используется для доступа на чтение и редактирование счетчика Melda
     */
    public static final User SIMPLE_USER5 = new User("at-metrika-38")
            .putSecret("SIMPLE_USER5");

    /**
     * Этот пользователь используется в негативных тестах на nda,
     * используется для доступа на чтение счетчика Melda
     */
    public static final User SIMPLE_USER6 = new User("at-metrika-43")
            .putSecret("SIMPLE_USER6");

    public static final User USER_WITH_EMPTY_TOKEN = new User("at-metrika-tester")
            .putSecret("USER_WITH_EMPTY_TOKEN")
            .put(OAUTH_TOKEN, "");

    public static final User USER_WITH_WRONG_TOKEN = new User("abc")
            .put(PASSWORD, "abc")
            .put(OAUTH_TOKEN, "AQAAAAAZRKvaAAIVavILczYy-ERVkcmvXyeYiHo");

    public static final User USER_WITH_ONE_PHONE = new User("yndx-at-metrika-4")
            .putSecret("USER_WITH_ONE_PHONE");

    public static final User USER_WITH_TWO_PHONES = new User("yandex-team-at-metr-6")
            .putSecret("USER_WITH_TWO_PHONES");

    public static final User USER_WITH_PHONE_LOGIN = new User("+78120028438@yandex.ru")
            .putSecret("USER_WITH_PHONE_LOGIN");

    public static final User USER_WITH_PHONE_ONLY_LOGIN = new User("+78120028438")
            .putSecret("USER_WITH_PHONE_ONLY_LOGIN");

    public static final User NONEXISTENT_USER = new User("at-metrika-non-existent-user");

    public static final User USER_WITH_INVALID_LOGIN = new User("sonick@");

    /**
     * Пользователи для тестирования связи метрики и директа
     */
    public static final User DIRECT_COMPANY_OWNER = new User("yndx-market-direct");
    public static final User DIRECT_CLIENT_DELEGATEE = new User("yndx-market-api");
    public static final User DIRECT_CLIENT_MANAGER = new User("yndx-pomytkina");
    public static final User DIRECT_CLIENT_AGENCY = new User("webit2005");
    public static final User DIRECT_AGENCY_DELEGATEE = new User("monica-liu");
    public static final User DIRECT_AGENCY_MANAGER = new User("u-belyaeva");

    /**
     * Этот пользователь используется только в тестах записи настроек рассылки или
     * проверке прав на чтение настроек рассылки как тот, кому записывают/считывают настройки рассылки
     */
    public static final User USER_FOR_EMAIL_SUBSCRIPTION1 = new User("at-metrika-36")
            .putSecret("USER_FOR_EMAIL_SUBSCRIPTION1")
            .put(UID, 479287676L);

    /**
     * Этот пользователь используется для тестирования перезаписи настроек рассылки как тот,
     * кому перезаписывают настройки рассылки
     */
    public static final User USER_FOR_EMAIL_SUBSCRIPTION2 = new User("at-metrika-37")
            .putSecret("USER_FOR_EMAIL_SUBSCRIPTION2")
            .put(UID, 479293972L);

    /**
     * Этот пользователь используется для тестирования прав записи настроек новостной рассылки как тот,
     * кому записывают настройки рассылки
     */
    public static final User USER_FOR_EMAIL_SUBSCRIPTION3 = new User("at-metrika-39")
            .putSecret("USER_FOR_EMAIL_SUBSCRIPTION3")
            .put(UID, 479294789L);

    /**
     * Этот пользователь используется для тестирования прав перезаписи настроек новостной рассылки как тот,
     * кому перезаписывают настройки рассылки
     */
    public static final User USER_FOR_EMAIL_SUBSCRIPTION4 = new User("at-metrika-40")
            .putSecret("USER_FOR_EMAIL_SUBSCRIPTION4")
            .put(UID, 479295517L);

    /**
     * Это обычный пользователь для создания счетчиков, которые будут статично использоваться в тестах.
     * Поэтому использовать самого пользователя в автотестах (создавать и удалять ему счетчики динамически) нельзя.
     */
    public static final User METRIKA_TEST_COUNTERS = new User("metrika.auto")
            .putSecret("METRIKA_TEST_COUNTERS");

    /**
     * Несуществующий пользователь, чей uid подставляется как uid человека, который аппрувит/реджектит запросы на стороне Вебмастера
     */
    public static final User WEBMASTER_NONEXISTENT_USER = new User("webmaster-approver")
            .put(UID, 37346674L);

    /**
     * Пользователь созданный специально для QuotasTest. У него дефолтная квота на запросы.
     * ВАЖНО: НЕ СТОИТ ЕГО ИСПОЛЬЗОВАТЬ ГДЕ ЛИБО, КРОМЕ QuotasTest!!!
     */
    public static final User USER_WITH_DEFAULT_QUOTA = new User("at-metrika-42")
            .putSecret("USER_WITH_DEFAULT_QUOTA");

    public static final User EMPTY_USER = new User("");

    /**
     * Пользователь без квоты
     */
    public static final User NO_QUOTA_USER = new User("yndx-metrika-no-quota")
            .put(UID, 1043631340L)
            .putSecret("NO_QUOTA_USER");

    public static final User YA_SERVICE_READ_SPRAV = new User("yndx-robot-metrika-test-989227")
            .putSecret("YA_SERVICE_READ_SPRAV");

    public static final User SIMPLE_USER_ONLY_FOR_QUOTAS = new User("at-metrika-quota-checker")
            .putSecret("SIMPLE_USER_ONLY_FOR_QUOTAS")
            .put(UID, 1130227802L);

    public static final User USER_WITH_COUNTERS_LIMIT_EXCEEDED = new User("yndx-metrika-counters-24")
            .put(UID, 1019949471L);

    /**
     * Пользователь с доступом на чтение счетчика Метрики, выданным через idm
     */
    public static final User USER_WITH_IDM_VIEW_PERMISSION = new User("yndx-robot-metrika-test-646004")
            .putSecret("USER_WITH_IDM_VIEW_PERMISSION");

    /**
     * Пользователь с доступом на чтение и редактирование счетчика Метрики, выданным через idm
     */
    public static final User USER_WITH_IDM_EDIT_PERMISSION = new User("yndx-robot-metrika-test-626298")
            .putSecret("USER_WITH_IDM_EDIT_PERMISSION");

    private Users() {
    }
}
