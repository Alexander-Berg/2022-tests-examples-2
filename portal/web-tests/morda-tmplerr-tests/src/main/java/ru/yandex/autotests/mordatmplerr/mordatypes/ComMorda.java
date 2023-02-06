package ru.yandex.autotests.mordatmplerr.mordatypes;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 24.04.14
 */
public class ComMorda extends MordaWithoutDomains {
    private static final String COM_URL_PATTERN = "https://%s.yandex.com/";

    @Override
    public String getUrl(String mordaEnv) {
        return super.getUrl(mordaEnv);
    }

    @Override
    protected String getUrlPattern() {
        return COM_URL_PATTERN;
    }

    public static ComMorda comMorda() {
        return new ComMorda();
    }

    @Override
    public String toString() {
        return "COM " + super.toString();
    }
}
