package ru.yandex.autotests.mainmorda.data;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.glassfish.jersey.client.JerseyClient;
import org.glassfish.jersey.client.JerseyClientBuilder;
import org.hamcrest.Matcher;
import org.hamcrest.Matchers;
import ru.yandex.autotests.dictionary.TextID;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mordaexportsclient.beans.ThemesGroupV12Entry;
import ru.yandex.autotests.mordaexportsclient.beans.ThemesV12Entry;
import ru.yandex.autotests.utils.morda.url.Domain;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.index;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.THEMES_GROUP_V12;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.THEMES_V12;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.allExports;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SkinsList.ACCEPT;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SkinsList.CLOSE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SkinsList.DECLINE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SkinsList.NORMAL;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SkinsList.SHARE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SkinsList.SHARE_ALT;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SkinsList.SHARE_FRIENDS;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Local.SkinsList.LINK_LABEL;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.language.TankerManager.TRIM;

/**
 * User: alex89
 * Date: 31.07.12
 */
public class SkinsData {
    private static final Properties CONFIG = new Properties();

    private static final String HOME = "home";
    private static final String ALLSKINS = "allskins";
    private static final String SKINS_GROUP = "skinsGroup";

    public static final String THEME_URL_PART = "/themes/";
    public static final String SET_SK_URL_PART = "/set?sk=";
    public static final String SKIN_RESOURCES_PREFIX = "(.*//yastatic.net/www-skins/[0-9]\\.[0-9]{1,3}/|.*yandex.*/)";
    private static final String ICON_SRC_PATTERN =
            SKIN_RESOURCES_PREFIX + "skins/big/%s/preview\\.png";

    public static final String DEFAULT_SKIN_ID = "default";
    public static final String RANDOM_SKIN_ID = "random";

    private static String DOMAIN_TYPE = CONFIG.getBaseDomain().equals(Domain.UA) ? "ua" : "kubr-ua";

    public static List<String> ALL_SKINS =
            extract(exports(THEMES_V12,
                            having(on(ThemesV12Entry.class).getDomain(),
                                    anyOf(isEmptyOrNullString(), equalTo(DOMAIN_TYPE))),
                            having(on(ThemesV12Entry.class).getHidden(), equalTo(0))),
                    on(ThemesV12Entry.class).getId());

    static {
        ALL_SKINS.remove(DEFAULT_SKIN_ID);
        ALL_SKINS.remove(RANDOM_SKIN_ID);
    }

    public static Map<String, ThemesGroupV12Entry> ALL_SKIN_GROUPS =
            index(allExports(THEMES_GROUP_V12), on(ThemesGroupV12Entry.class).getId());
    public static final Map<String, Matcher<String>> SPEC_SRC_PROD = new HashMap<String, Matcher<String>>() {{
        put(DEFAULT_SKIN_ID,
                matches(SKIN_RESOURCES_PREFIX + "skins/big/default/preview\\.png"));
        put(RANDOM_SKIN_ID,
                matches(SKIN_RESOURCES_PREFIX + "skins/big/random/preview\\.png"));
    }};


    private static final int PARAMETRIZED_TEST_SIZE = 5;

    private static final List<String> SHUFFLED_LIST = new ArrayList<>(ALL_SKINS);

    static {
        Collections.shuffle(SHUFFLED_LIST);
    }

    public static final String SET_SKIN_URL = CONFIG.getBaseURL() + "/themes/?defskin=%s";
    public static final String SAVE_SKIN_URL = CONFIG.getBaseURL() + SkinsData.THEME_URL_PART + "%s" +
            SkinsData.SET_SK_URL_PART + "%s";

    public static final String RANDOM_SKIN = SHUFFLED_LIST.get(0);
    public static final String RANDOM_SKIN_2 = SHUFFLED_LIST.get(1);

    public static final List<String> PARAMETRIZED_SKINS =
            SHUFFLED_LIST.subList(0, Math.min(SHUFFLED_LIST.size(), PARAMETRIZED_TEST_SIZE));

    public static final String THEME_PAGE_URL = CONFIG.getBaseURL() + "/themes";

    public static final Matcher<String> SHARE_TITLE_MATCHER =
            equalTo(getTranslation(TRIM, SHARE_ALT, CONFIG.getLang()));
    public static final Matcher<String> SHARE_BUTTON_TEXT_MATCHER =
            equalTo(getTranslation(TRIM, SHARE, CONFIG.getLang()));
    public static final Matcher<String> SHARE_POPUP_LABEL_TEXT_MATCHER =
            equalTo(getTranslation(TRIM, LINK_LABEL, CONFIG.getLang()));
    public static final Matcher<String> SHARE_POPUP_TITLE_TEXT_MATCHER =
            equalTo(getTranslation(TRIM, SHARE_FRIENDS, CONFIG.getLang()));

    public static Matcher<String> getShareTextMatcher(String skinId) {
        return equalTo("http://www.yandex" + CONFIG.getBaseDomain() + THEME_URL_PART + skinId);
    }

    public static Matcher<String> getSkinHrefMatcher(String skinId) {
        return startsWith(CONFIG.getBaseURL() + THEME_URL_PART + skinId);
    }

    public static Matcher<String> getSkinTextMatcher(String skinId) {
        return equalTo(getTranslation(TRIM, HOME, ALLSKINS, skinId, CONFIG.getLang()));
    }

    public static Matcher<String> getSkinSrcMatcher(String skinId) {
        if (SPEC_SRC_PROD.containsKey(skinId)) {
            return SPEC_SRC_PROD.get(skinId);
        } else {
            return matches(String.format(ICON_SRC_PATTERN, skinId));
        }
    }

    public static final Matcher<String> CLOSE_BUTTON_TEXT_MATCHER =
            equalTo(getTranslation(TRIM, CLOSE, CONFIG.getLang()) + "\nx");
    public static final Matcher<String> SAVE_BUTTON_TEXT_MATCHER =
            equalTo(getTranslation(TRIM, ACCEPT, CONFIG.getLang()));
    public static final Matcher<String> CANCEL_BUTTON_TEXT_MATCHER =
            equalTo(getTranslation(TRIM, DECLINE, CONFIG.getLang()));
    public static final Matcher<String> RESET_BUTTON_TEXT_MATCHER =
            equalTo(getTranslation(TRIM, NORMAL, CONFIG.getLang()));
    public static final Matcher<String> DEFAULT_BUTTON_HREF_MATCHER = equalTo(CONFIG.getBaseURL() + "/");

    public static Matcher<String> getButtonHrefMatcher(String skinId, String secretKey) {
        return equalTo(CONFIG.getBaseURL() + THEME_URL_PART + skinId + SET_SK_URL_PART + secretKey);
    }

    public static Matcher<String> getTabTextMatcher(String groupId) {
        return Matchers.equalTo(getTranslation(HOME, SKINS_GROUP, groupId, CONFIG.getLang()));
    }


    public static class TabId {
        private TextID textID;

        public TabId(TextID textID) {
            this.textID = textID;
        }

        public String getTabId() {
            return textID.toString().substring(textID.toString().lastIndexOf(">>") + 2);
        }

        public TextID getTabTextId() {
            return textID;
        }

        @Override
        public String toString() {
            return this.getTabId();
        }
    }

    public static Map<String, List<String>> getSkinsMap(String skinsVersion) {
        try {
            JerseyClient client = JerseyClientBuilder.createClient();
            String result = client.target("https://yastatic.net/www-skins/")
                    .path(skinsVersion)
                    .path("/skins/freeze.json")
                    .request()
                    .get(String.class);
            return inverseMap(new ObjectMapper().readValue(result, HashMap.class));
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    private static <K, V> Map<V, List<K>> inverseMap(Map<K, V> map) {
        Map<V, List<K>> result = new HashMap<V, List<K>>();
        for (Map.Entry<K, V> entry : map.entrySet()) {
            List<K> toInsert = new ArrayList<>();
            if (result.containsKey(entry.getValue())) {
                toInsert = result.get(entry.getValue());
            }
            toInsert.add(entry.getKey());
            result.put(entry.getValue(), toInsert);
        }
        return result;
    }
}
