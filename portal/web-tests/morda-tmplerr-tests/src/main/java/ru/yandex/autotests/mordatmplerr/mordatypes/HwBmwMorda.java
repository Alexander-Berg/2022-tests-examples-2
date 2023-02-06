package ru.yandex.autotests.mordatmplerr.mordatypes;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 24.04.14
 */
public class HwBmwMorda extends MordaWithoutDomains {
    private static final String HW_BMW_URL_PATTERN = "http://%s.yandex.ru/bmw";

    @Override
    public String getUrl(String mordaEnv) {
        return super.getUrl(mordaEnv.replace("www", "hw"));
    }

    @Override
    protected String getUrlPattern() {
        return HW_BMW_URL_PATTERN;
    }

    public static HwBmwMorda hwBmwMorda() {
        return new HwBmwMorda();
    }

    @Override
    public String toString() {
        return "HW_BMW " + super.toString();
    }
}
