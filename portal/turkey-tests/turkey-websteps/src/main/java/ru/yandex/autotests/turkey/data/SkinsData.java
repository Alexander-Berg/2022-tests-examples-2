package ru.yandex.autotests.turkey.data;

import org.hamcrest.Matcher;
import org.hamcrest.Matchers;
import ru.yandex.autotests.dictionary.TextID;
import ru.yandex.autotests.mordaexportsclient.beans.ThemesComtrEntry;
import ru.yandex.autotests.mordaexportsclient.beans.ThemesGroupComtrEntry;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.utils.morda.language.Dictionary;
import ru.yandex.autotests.utils.morda.url.UrlManager;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static ch.lambdaj.Lambda.extract;
import static ch.lambdaj.Lambda.index;
import static ch.lambdaj.Lambda.on;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.THEMES_COMTR;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.THEMES_GROUP_COMTR;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.allExports;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SkinsList.ACCEPT;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SkinsList.CLOSE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SkinsList.DECLINE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SkinsList.NORMAL;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SkinsList.SHARE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SkinsList.SHARE_ALT;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SkinsList.SHARE_FRIENDS;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SkinsList.SHARE_TITLE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SkinsList.SHARE_TITLE_TWITTER;
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
    private static final String ICON_SRC_PATTERN =
            "http://yastatic\\.net/www/[0-9]\\.[0-9]{1,3}/v12/skins/turkey/%s/preview\\.png";

    public static final String DEFAULT_SKIN_ID = "default";
    public static final String RANDOM_SKIN_ID = "random";

    public static List<String> ALL_SKINS = extract(allExports(THEMES_COMTR), on(ThemesComtrEntry.class).getId());
    static {
        ALL_SKINS.remove(DEFAULT_SKIN_ID);
        ALL_SKINS.remove(RANDOM_SKIN_ID);
    }

    public static Map<String, ThemesGroupComtrEntry> ALL_SKIN_GROUPS =
            index(allExports(THEMES_GROUP_COMTR), on(ThemesGroupComtrEntry.class).getId());

    private static final Map<String, Matcher<String>> SPEC_SRC_PROD =
            new HashMap<String, Matcher<String>>() {{
        put(DEFAULT_SKIN_ID, matches("http://yastatic\\.net/www/[0-9]\\.[0-9]{1,3}/v12/skins/turkey/default\\.png"));
        put(RANDOM_SKIN_ID, matches("http://yastatic\\.net/www/[0-9]\\.[0-9]{1,3}/v12/skins/turkey/random\\.png"));
    }};

    private static final Map<String, Matcher<String>> SPEC_SRC_DEV =
            new HashMap<String, Matcher<String>>() {{
        put(DEFAULT_SKIN_ID, equalTo("/v12/skins/turkey/default.png"));
        put(RANDOM_SKIN_ID, equalTo("/v12/skins/turkey/random.png"));
    }};


    private static final int PARAMETRIZED_TEST_SIZE = 5;

    private static final List<String> SHUFFLED_ID_LIST = new ArrayList<>(ALL_SKINS);

    static {
        Collections.shuffle(SHUFFLED_ID_LIST);
    }

    public static final String SET_SKIN_URL = CONFIG.getBaseURL() + "/themes/%s";

    public static final String RANDOM_SKIN = SHUFFLED_ID_LIST.get(0);
    public static final String RANDOM_SKIN_2 = SHUFFLED_ID_LIST.get(1);

    public static final List<String> PARAMETRIZED_SKIN_IDS =
            SHUFFLED_ID_LIST.subList(0, Math.min(SHUFFLED_ID_LIST.size(), PARAMETRIZED_TEST_SIZE));

    public static final String YBF_INNER_COOKIE = "ybf";

    public static final String GALATASARAY_COOKIE_VALUE = "gs";
    public static final String BESIKTAS_COOKIE_VALUE = "bjk";
    public static final String FENERBAHCE_COOKIE_VALUE = "fb";

    public static final List<Object[]> FOOTBALL_SKINS = Arrays.asList(
            new Object[]{"galatasaray", GALATASARAY_COOKIE_VALUE},
            new Object[]{"besiktas", BESIKTAS_COOKIE_VALUE},
            new Object[]{"fenerbahce", FENERBAHCE_COOKIE_VALUE}
    );

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
        return equalTo(getTranslation(TRIM,  HOME, ALLSKINS, skinId, CONFIG.getLang()));
    }

    private static Matcher<String> getDevSkinSrc(String skinId) {
        if (SPEC_SRC_DEV.containsKey(skinId)) {
            return SPEC_SRC_DEV.get(skinId);
        } else {
            return containsString("/v12/skins/turkey/" + skinId + "/preview.png");
        }
    }

    private static Matcher<String> getProdSkinSrc(String skinId) {
        if (SPEC_SRC_PROD.containsKey(skinId)) {
            return SPEC_SRC_PROD.get(skinId);
        } else {
            return matches(String.format(ICON_SRC_PATTERN, skinId));
        }
    }

    public static Matcher<String> getSkinSrcMatcher(String skinId) {
        if (CONFIG.getMordaEnv().isDev()) {
            return getDevSkinSrc(skinId);
        } else {
            return getProdSkinSrc(skinId);
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
    public static final Matcher<String> DEFAULT_BUTTON_HREF_MATCHER =
            equalTo(CONFIG.getBaseURL() + "/");

    public static Matcher<String> getButtonHrefMatcher(String skinId, String secretKey) {
        return equalTo(CONFIG.getBaseURL() + THEME_URL_PART + skinId + SET_SK_URL_PART + secretKey);
    }

    public static Matcher<String> getTabTextMatcher(String groupId) {
        return Matchers.equalTo(getTranslation(HOME, SKINS_GROUP, groupId, CONFIG.getLang()));
    }

    public static enum SocialIcon {
        FACEBOOK("facebook", startsWith(getTranslation(TRIM, Dictionary.Home.MySites.FACEBOOK, CONFIG.getLang())),
                SHARE_TITLE),
        TWITTER("twitter", startsWith(getTranslation(TRIM, Dictionary.Home.MySites.TWITTER, CONFIG.getLang())),
                SHARE_TITLE_TWITTER),
        FRIEND_FEED("friendfeed", startsWith(getTranslation(TRIM, Dictionary.Local.SkinShare.SKINSHARE_FRIEND_FEED,
                CONFIG.getLang())), SHARE_TITLE);

        public String name;
        public Matcher<String> text;
        private String titlePattern;

        private static final String IMAGE_PARAM;

        static {
            if (CONFIG.getMordaEnv().isDev()) {
                IMAGE_PARAM = "&image=%2Fv12%2Fskins%2Fturkey%2F";
            } else {
                IMAGE_PARAM = "&image=http%3A%2F%2Fyastatic.net%2Fwww%2F[0-9].[0-9]{1,3}%2Fv12%2Fskins%2Fturkey%2F";
            }
        }

        private static final String YANDEX_URL_REQUEST =
                UrlManager.encodeRequest("http://www.yandex" + CONFIG.getBaseDomain());
        private static final String SHARE_URL_PATTERN = "http://share.yandex.ru/go.xml?service=%s&url=%s";

        private SocialIcon(String name, Matcher<String> text, TextID title) {
            this.name = name;
            this.text = text;
            this.titlePattern = getTranslation(TRIM, title, CONFIG.getLang());
        }

        public Matcher<String> getHrefMatcher(String skinId) {
            String notationRequest = UrlManager.encodeRequest(skinId);
            String titleRequest = UrlManager.encodeRequest(
                    titlePattern.replace("%1$s",
                            getTranslation(HOME, ALLSKINS, skinId, CONFIG.getLang())).replace("%21", "!")
            );

            return matches((String.format(SHARE_URL_PATTERN, name, YANDEX_URL_REQUEST) +
                    "%2Fthemes%2F" + notationRequest +
                    "&title=" + titleRequest + IMAGE_PARAM + notationRequest + "%2Fpreview.png")
                    .replace(".", "\\.").replace("?", "\\?"));
        }
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

}
