package ru.yandex.autotests.mordatmplerr.mordatypes;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 24.04.14
 */
public class ComTrMorda extends MordaWithoutDomains {
    private static final String COM_TR_URL_PATTERN = "https://%s.yandex.com.tr/";
    private boolean isFamily = false;

    @Override
    public String getUrl(String mordaEnv) {
        if (isFamily) {
            return super.getUrl(mordaEnv.replace("www", "aile"));
        } else {
            return super.getUrl(mordaEnv);
        }
    }

    @Override
    protected String getUrlPattern() {
        return COM_TR_URL_PATTERN;
    }

    public static ComTrMorda comTrMorda() {
        return new ComTrMorda();
    }

    public static ComTrMorda aileMorda() {
        ComTrMorda morda = new ComTrMorda();
        morda.isFamily = true;
        return morda;
    }

    @Override
    public String toString() {
        if (isFamily) {
            return "COM_TR FAMILY " + super.toString();
        }
        return "COM_TR " + super.toString();
    }

}
