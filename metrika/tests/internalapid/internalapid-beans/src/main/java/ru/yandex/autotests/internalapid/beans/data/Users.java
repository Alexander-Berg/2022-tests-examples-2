package ru.yandex.autotests.internalapid.beans.data;

public class Users {
    public static final User METRIKA_INTAPI_AUTO = new User("metrika-intapi.auto")
            .put(User.UID, 1003525280L);

    public static final User METRIKA_INTAPI_DELEGATE = new User("metrika-intapi.delegate")
            .put(User.UID, 1004779446L);

    public static final User METRIKA_INTAPI_GRANTEE = new User("metrika-intapi.grantee")
            .put(User.UID, 1004836273L);

    public static final User MANAGER = new User("metrika-intapi.manager")
            .put(User.UID, 1010322562L);

    public static final User MANAGER_2 = new User("metrika-intapi.manager2")
            .put(User.UID, 1104671583L);

    public static final User PINCODE_TARGET_USER = new User("at-metrika-37")
            .put(User.UID, 479293972L);

    public static final User PINCODE_DELEGATE_USER = new User("at-metrika-39")
            .put(User.UID, 479294789L);

    public static final User PINCODE_DELEGATE_USER2 = new User("at-metrika-46")
            .put(User.UID, 1467822513L);

    /**
     * Этот пользователь имеет роль super
     */
    public static final User SUPER_USER = new User("yndx-robot-metrika-test-super")
            .putSecret("SUPER_USER")
            .put(User.UID, 423930842L);

    public static final User SIMPLE_USER2 = new User("at-metrika-2")
            .putSecret("SIMPLE_USER2")
            .put(User.UID, 288933839L);
}
