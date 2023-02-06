package ru.yandex.autotests.mordatmplerr.mordatypes;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 24.04.14
 */
public class YaRuMorda extends MordaWithoutDomains {
    private static final String YA_RU_URL_PATTERN = "https://%s.ya.ru/";

    @Override
    public String getUrl(String mordaEnv) {
        return super.getUrl(mordaEnv);
    }

    @Override
    protected String getUrlPattern() {
        return YA_RU_URL_PATTERN;
    }

    public static YaRuMorda yaruMorda() {
        return new YaRuMorda();
    }

    @Override
    public String toString() {
        return "YARU " + super.toString();
    }
}
