package ru.yandex.autotests.metrika.appmetrica.data;

import static ru.yandex.autotests.metrika.appmetrica.data.User.*;


/**
 * Все изменения нужно согласовывать с
 * https://wiki.yandex-team.ru/testirovanie/functesting/advtechnologies/metrikadata/
 * и при необходимости с кодом тестов метрики.
 */
public class Users {

    /**
     * Пользователь с ролью саппорта, используется также в тестах метрики.
     * Имеет полный доступ ко всем приложениям и используется в случаях, когда нужен доступ к произвольным приложениям
     * (например, к Метро или Диску) к которым у обычных пользователей нет доступа. Сейчас это апи отчётов и
     * пуш кампаний. В других местах {@link Users#SIMPLE_USER} или {@link Users#SIMPLE_USER_2} создают пустое приложение
     * и тесты работают уже с ним.
     * Не следует использовать этого пользователя если можно обойтись обычными пользователями без специфичных ролей.
     */
    public static final User SUPER_LIMITED = new User("at-metrika-tester")
            .putSecret("SUPER_LIMITED")
            .put(UID, "282183929");

    /**
     * Обычный пользователь без специальных ролей
     */
    public static final User SIMPLE_USER = new User("at-appmetrica-user")
            .putSecret("SIMPLE_USER")
            .put(UID, "658542937");

    /**
     * Обычный пользователь без специальных ролей. Нужен для тестов где мы хотим
     * проверить взаимодействие двух обычных пользователей (например, выдача прав)
     */
    public static final User SIMPLE_USER_2 = new User("at-appmetrica-user-1")
            .putSecret("SIMPLE_USER_2")
            .put(UID, "658870432");

    /**
     * Обычный пользователь без специальных ролей, используемый в тестах, где данные
     * пользователя не должны изменяться параллельно
     */
    public static final User READ_USER = new User("at-appmetrica-user-2")
            .putSecret("READ_USER")
            .put(UID, "664494999");
}
