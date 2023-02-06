package ru.yandex.autotests.audience.data.users;

import com.google.common.collect.ImmutableList;

import static ru.yandex.autotests.audience.data.users.User.*;

/**
 * Created by konkov on 23.03.2017.
 */
public final class Users {
    /**
     * Тестовый пользователь
     */
    public static final User SIMPLE_USER = new User("at-audi-1")
            .putSecret("SIMPLE_USER")
            .put(METRIKA_COUNTER_ID, 44686621L)
            .put(METRIKA_GOAL_ID, 31436437L)
            .put(METRIKA_SEGMENT_ID, 1000930744L)
            .put(METRIKA_GOALS_IDS, ImmutableList.of(31837009L, 31837012L, 32366010L))
            .put(APPMETRICA_APLICATION_ID, 640726L)
            .put(APPMETRICA_API_KEY, "896c6cd7-f871-40c4-99ce-5649dafa32fc")
            .put(APPMETRICA_SEGMENT_ID, 130385L)
            .put(ANOTHER_METRIKA_COUNTER, 44928991L)
            .put(ANOTHER_COUNTER_GOAL_IDS, ImmutableList.of(31837054L));

    /**
     * Тестовый пользователь для lookalike
     */
    public static final User USER_FOR_LOOKALIKE = new User("at-audi-2")
            .putSecret("USER_FOR_LOOKALIKE")
            .put(APPMETRICA_APLICATION_ID, 137715L)
            .put(APPMETRICA_API_KEY, "b9c82556-17bf-4146-9881-fa737137daeb")
            .put(APPMETRICA_SEGMENT_ID, 132171L);

    /**
     * Тестовый пользователь для негативные проверкок на права для Lookalike для Metrika и AppMetrica
     */
    public static final User USER_LOOKALIKE_NEGATIVE = new User("at-audi-3")
            .putSecret("USER_LOOKALIKE_NEGATIVE")
            .put(AUDIENCE_METRIKA_SEGMENT_ID, 1220463L)
            .put(AUDIENCE_APPMETRICA_SEGMENT_ID, 1220466L)
            .put(METRIKA_SEGMENT_ID, 1000870129L);

    /**
     * Тестовый пользователь для проверки заливки сегментов внутренними сервисами
     */
    public static final User USER_FOR_INTERNAL_DMP = new User("at-audi-4")
            .putSecret("USER_FOR_INTERNAL_DMP")
            .put(GEO_SEGMENT_ID, 1225605L);

    /**
     * Тестовый пользователь с правами InternalDmp
     */
    public static final User INTERNAL_DMP_UPLOADER = new User("yndx-robot-metrika-test-970492")
            .putSecret("INTERNAL_DMP_UPLOADER");

    /**
     * Тестовый пользователь с правами InternalDmp
     */
    public static final User INTERNAL_DMP_UPLOADER_2 = new User("yndx-robot-metrika-test-813778")
            .putSecret("INTERNAL_DMP_UPLOADER_2");

    /**
     * Тестовый пользователь для проверки выдачи доступа на сегмент и представительского доступа в тестах
     * удаление представителя
     */
    public static final User USER_GRANTEE = new User("at-audi-5")
            .putSecret("USER_GRANTEE");
    /**
     * Тестовый пользователь используется в тестах редактирования представительского доступа
     */
    public static final User USER_GRANTEE2 = new User("at-audi-12")
            .putSecret("USER_GRANTEE2");

    /**
     * Тестовый пользователь с правом на чтение для аккаунта USER_DELEGATOR
     */
    public static final User USER_WITH_PERM_VIEW = new User("at-audi-6")
            .putSecret("USER_WITH_PERM_VIEW");

    /**
     * Тестовый пользователь с правом на редактирование для аккаунта USER_DELEGATOR
     */
    public static final User USER_WITH_PERM_EDIT = new User("at-audi-7")
            .putSecret("USER_WITH_PERM_EDIT");

    /**
     * Тестовый аккаунт для тестирования ролей и доступов
     */
    public static final User USER_DELEGATOR = new User("at-audi-8")
            .putSecret("USER_DELEGATOR")
            .put(METRIKA_COUNTER_ID, 45117855L)
            .put(GEO_SEGMENT_ID, 1220952L);

    /**
     * Тестовый аккаунт для проверки смены уровня представительсокого доступа
     */
    public static final User USER_DELEGATOR_2 = new User("at-audi-9")
            .putSecret("USER_DELEGATOR_2");

    /**
     * Тестовый аккаунт для тестов на роли
     */
    public static final User USER_DELEGATOR_3 = new User("at-audi-10")
            .putSecret("USER_DELEGATOR_3")
            .put(METRIKA_COUNTER_ID, 45370071L);

    /**
     * Тестовый пользователь 2
     */
    public static final User SIMPLE_USER_2 = new User("at-audi-11")
            .putSecret("SIMPLE_USER_2");

    public static final User USER_FOR_UPLOADING_MODIFY = new User("at-audi-13")
            .putSecret("USER_FOR_UPLOADING_MODIFY");

    /**
     * Пользователь с ролью Manager
     */
    public static final User MANAGER = new User("yndx-robot-metrika-test-457972")
            .putSecret("MANAGER");

    /**
     * Пользователь с ролью SUPER_USER
     */
    public static final User SUPER_USER = new User("yndx-robot-metrika-test-801693")
            .putSecret("SUPER_USER");

    /**
     * Пользователь с для тестирования audience-crypta-sender
     */
    public static final User AUDIENCE_CRYPTA_SENDER_CREATOR = new User("yndx-robot-metrika-test-724884")
            .putSecret("AUDIENCE_CRYPTA_SENDER_CREATOR")
            .put(METRIKA_COUNTER_ID, 24226447L)
            .put(METRIKA_GOAL_ID, 6630902L)
            .put(METRIKA_SEGMENT_ID, 1000870129L)
            .put(APPMETRICA_APLICATION_ID, 137715L)
            .put(APPMETRICA_SEGMENT_ID, 133242L);
}
