package ru.yandex.autotests.morda.pages;

import ru.yandex.autotests.morda.tanker.Language;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.cookies.my.CookieMy;

import javax.ws.rs.client.Client;
import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Stream;

import static com.google.common.primitives.Ints.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 11/05/16
 */
public enum MordaLanguage {
    RU(Language.RU, "ru", 1),
    UK(Language.UK, "ua", 2),
    BE(Language.BE, "by", 5),
    KK(Language.KK, "kz", 4),
    TT(Language.TT, "tt", 6),
    EN(Language.EN, "en", 3),
    TR(Language.TR, "tr", 8),
    ID(Language.ID, "id", 13);

    private static final int MY_LANG_BLOCK = 39;
    private Language language;
    private String exportValue;
    private int intl;

    MordaLanguage(Language language, String exportValue, int intl) {
        this.language = language;
        this.exportValue = exportValue;
        this.intl = intl;
    }

    public static MordaLanguage fromValue(String value) {
       return Stream.of(values())
                .filter(e -> e.getValue().equals(value))
                .findFirst()
                .orElseThrow(() -> new RuntimeException("There is no lang with value " + value));
    }

    public static String setLanguageInMyCookie(String cookieMy, MordaLanguage language) {
        CookieMy cookieMyParsed = new CookieMy(cookieMy);
        cookieMyParsed.setBlock(MY_LANG_BLOCK, asList(0, language.getIntl()));
        return cookieMyParsed.toString();
    }

    public static boolean checkLanguage(String cookieMy, MordaLanguage language) {
        CookieMy cookieMyParsed = new CookieMy(cookieMy);
        List<Integer> langs = cookieMyParsed.getBlock(MY_LANG_BLOCK);
        return langs != null && langs.size() == 2 && langs.get(1) == language.getIntl();
    }

    @Step("Set language {2}")
    public static void setLanguage(Client client, Morda morda, MordaLanguage language) {
//        String sk = cookieUtils(client)
//                .getSecretKey(morda.getCookieDomain());
//        URI setLanguageUri = getSetLanguageUri(morda.getTuneHost(), language, sk);
//        Response response = client.target(setLanguageUri)
//                .request()
//                .buildGet()
//                .invoke();
    }

    private static URI getSetLanguageUri(URI tuneHost, MordaLanguage language, String sk) {
        return UriBuilder.fromUri(tuneHost)
                .path("api/lang/v1.1/save.xml")
                .queryParam("intl", language.getValue())
                .queryParam("sk", sk)
                .build();
    }

    public String setLanguageInMyCookie(String cookieMy) {
        return setLanguageInMyCookie(cookieMy, this);
    }

    public String getCookieMyValue() {
        CookieMy cookieMyParsed = new CookieMy();
        cookieMyParsed.setBlock(MY_LANG_BLOCK, asList(0, getIntl()));
        return cookieMyParsed.toString();
    }

    public static List<MordaLanguage> getKUBRLanguages() {
        return Arrays.asList(RU, UK, BE, TT);
    }

    public String getValue() {
        return language.getValue();
    }

    public Language getLanguage() {
        return language;
    }

    public String getExportValue() {
        return exportValue;
    }

    public int getIntl() {
        return intl;
    }


    @Override
    public String toString() {
        return language.getValue();
    }
}
