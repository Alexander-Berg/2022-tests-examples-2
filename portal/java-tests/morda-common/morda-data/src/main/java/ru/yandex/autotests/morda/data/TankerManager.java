package ru.yandex.autotests.morda.data;

import ru.yandex.autotests.dictionary.Tanker;
import ru.yandex.autotests.dictionary.TankerCleaner;
import ru.yandex.autotests.dictionary.TextID;
import ru.yandex.autotests.dictionary.cleaners.DefaultCleaner;
import ru.yandex.autotests.dictionary.cleaners.HomeCleaner;
import ru.yandex.autotests.dictionary.cleaners.HomeTrimCleaner;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.tanker.home.ApiSearch;

import static ru.yandex.autotests.morda.pages.MordaLanguage.RU;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 03.04.13
 */
public enum TankerManager {
    DEFAULT(new DefaultCleaner()),
    HOME(new HomeCleaner()),
    TRIM(new HomeTrimCleaner());


    private static final String HOME_FILE = "home.xml";
    private static final String ZEN_FILE = "zen.xml";
    private static final String LEGO_ISLANDS_USER_FILE = "legoislandsuser.xml";
    private static final String TRANSLATIONS_LOCAL_FILE = "local.xml";
    private static final String TRANSLATIONS_REGIONS_FILE = "regions.xml";
    private static final String MAPS_API_FILE = "mapsapi.xml";
    private static final String TUNE_FILE = "tune.xml";

    private Tanker tanker;

    private TankerManager(TankerCleaner cleaner) {
        this.tanker = new Tanker(cleaner,
                TankerManager.class.getClassLoader().getResource(HOME_FILE),
                TankerManager.class.getClassLoader().getResource(TUNE_FILE),
                TankerManager.class.getClassLoader().getResource(ZEN_FILE),
                TankerManager.class.getClassLoader().getResource(LEGO_ISLANDS_USER_FILE),
                TankerManager.class.getClassLoader().getResource(TRANSLATIONS_LOCAL_FILE),
                TankerManager.class.getClassLoader().getResource(TRANSLATIONS_REGIONS_FILE),
                TankerManager.class.getClassLoader().getResource(MAPS_API_FILE)
        );
    }

    public Tanker getTanker() {
        return tanker;
    }

    public static String get(String projectId, String keysetId, String keyId, ru.yandex.autotests.dictionary.Plural pluralForm, String lang) {
        return DEFAULT.tanker.get(new TextID(projectId, keysetId, keyId, pluralForm), lang);
    }

    public static String get(String projectId, String keysetId, String keyId, String lang) {
        return DEFAULT.tanker.get(new TextID(projectId, keysetId, keyId), lang);
    }

    public static String get(String projectId, String keysetId, String keyId, MordaLanguage lang) {
        return get(projectId, keysetId, keyId, lang.getValue());
    }

    public static String get(TextID ids, String lang) {
        return DEFAULT.tanker.get(ids, lang);
    }

    public static String get(ru.yandex.autotests.morda.tanker.TextID id, MordaLanguage lang) {
        return DEFAULT.tanker.get(id.getProject(), id.getKeyset(), id.getKey(), lang.getValue());
    }

    public static String getSafely(String projectId, String keysetId, String keyId, MordaLanguage lang) {
        String str = get(projectId, keysetId, keyId, lang);
        if (str == null || "".equals(str)) return get(projectId, keysetId, keyId, RU);
        return str;
    }

    public static String getSafely(ru.yandex.autotests.morda.tanker.TextID id, MordaLanguage lang) {
        return getSafely(id.getProject(), id.getKeyset(), id.getKey(), lang);
    }

    public static String getSafely(TextID id, MordaLanguage lang) {
        String str = get(id, lang.getValue());
        if (str == null || "".equals(str)) return get(id, "ru");
        return str;
    }

    public static void main(String[] args) {
        System.out.println(TankerManager.get(ApiSearch.TV_TITLE, MordaLanguage.BE));
    }
}
