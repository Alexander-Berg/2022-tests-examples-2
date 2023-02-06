package ru.yandex.autotests.mordatmplerr.mordatypes;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 24.04.14
 */
public class HwLgMorda extends MordaWithoutDomains {
    private static final String HW_LG_URL_PATTERN = "http://%s.yandex.ru/lg";

    @Override
    public String getUrl(String mordaEnv) {
        return super.getUrl(mordaEnv.replace("www", "hw"));
    }

    @Override
    protected String getUrlPattern() {
        return HW_LG_URL_PATTERN;
    }

    public static HwLgMorda hwLgMorda() {
        return new HwLgMorda();
    }

    @Override
    public String toString() {
        return "HW_LG " + super.toString();
    }
}
