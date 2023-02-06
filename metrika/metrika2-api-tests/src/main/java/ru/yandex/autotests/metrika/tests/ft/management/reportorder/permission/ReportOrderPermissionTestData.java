package ru.yandex.autotests.metrika.tests.ft.management.reportorder.permission;

import ru.yandex.autotests.metrika.data.common.users.User;

import static ru.yandex.autotests.metrika.data.common.users.Users.*;

/**
 * @author zgmnkv
 */
public class ReportOrderPermissionTestData {

    public static final User COUNTER_OWNER = USER_DELEGATOR;
    public static final User COUNTER_OWNER_DELEGATE = USER_DELEGATE_PERMANENT;

    public static final User REPORT_ORDER_OWNER = USER_DELEGATOR2;
    public static final User REPORT_ORDER_OWNER_DELEGATE = USER_DELEGATE_PERMANENT;

    public static final User GRANTEE_WRITE_ACCESS = USER_GRANTEE;
    public static final User GRANTEE_READ_ACCESS = SIMPLE_USER2;
    public static final User FOREIGN_USER = SIMPLE_USER;
    public static final User UNAUTHORIZED_USER = USER_WITH_EMPTY_TOKEN;
}
