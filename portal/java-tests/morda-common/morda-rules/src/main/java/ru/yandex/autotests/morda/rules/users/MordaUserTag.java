package ru.yandex.autotests.morda.rules.users;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 28/05/16
 */
public enum MordaUserTag {
    DEFAULT("default"),
    WIDGET("widget"),
    LONG("long"),
    NO_MAIL("no_mail"),
    MAIL_0("mail_0"),
    MAIL_1("mail_1"),
    MAIL_2("mail_2"),
    MAIL_5("mail_5");

    public static final String MORDA_TAG = "morda";
    String value;

    MordaUserTag(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }
}
