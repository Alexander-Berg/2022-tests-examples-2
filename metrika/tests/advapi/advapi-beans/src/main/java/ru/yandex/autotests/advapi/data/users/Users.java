package ru.yandex.autotests.advapi.data.users;

/**
 * Created by vananos on 04.08.16.
 * Carefully copied by vfeduntsov on 15.02.19
 */
public final class Users {

    public static final User SUPER_USER = new User("yndx-robot-metrika-test-177610")
            .putSecret("SUPER_USER")
            .put(User.UID, 837114278L);

    public static final User SUPERVISOR = new User("yndx-robot-metrika-test-449387")
            .putSecret("SUPERVISOR")
            .put(User.UID, 837114298L);

    public static final User SIMPLE_USER_1 = new User("simple-admetrika-user-1")
            .putSecret("SIMPLE_USER_1")
            .put(User.UID, 837168521L);

    public static final User SIMPLE_USER_A = new User("simple-admetrika-user-a")
            .putSecret("SIMPLE_USER_A")
            .put(User.UID, 837170669L);

    public static final User READ_GUEST = new User("read-guest")
            .putSecret("READ_GUEST")
            .put(User.UID, 872475923L);

    public static final User WRITE_GUEST = new User("write-guest")
            .putSecret("WRITE_GUEST")
            .put(User.UID, 872478248L);

    public static final User WRITE_GUEST2 = new User("write-guest2")
            .putSecret("WRITE_GUEST2")
            .put(User.UID, 880202452L);

    public static final User EMPTY_USER = new User("");

    private Users() {
    }
}
