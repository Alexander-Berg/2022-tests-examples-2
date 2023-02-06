package ru.yandex.autotests.tuneapitests.language;

import java.util.Arrays;
import java.util.List;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 22/01/15
 */
public class LanguageData {
    public static final List<String> BAD_INTLS = Arrays.asList(
            null, "", "ua", "kz", "by", ".ru", "ruk", "ukr", "com"
    );

}
