package ru.yandex.autotests.mainmorda.utils;

import org.hamcrest.Matcher;
import ru.yandex.autotests.dictionary.TextID;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.utils.morda.language.Dictionary;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.url.Domain;
import ru.yandex.autotests.utils.morda.url.UrlManager;

import static org.hamcrest.Matchers.not;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SkinsList.SHARE_TITLE;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SkinsList.SHARE_TITLE_TWITTER;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.language.TankerManager.TRIM;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 22.04.13
 */
public enum SocialIcon {

    FACEBOOK("facebook", Dictionary.Home.MySites.FACEBOOK, SHARE_TITLE),
    TWITTER("twitter", Dictionary.Home.MySites.TWITTER, SHARE_TITLE_TWITTER),
    YARU("yaru", Dictionary.Local.SkinShare.SKINSHARE_YARU, SHARE_TITLE),
    VK("vkontakte", Dictionary.Home.Mail.PREFERENCES_VK, SHARE_TITLE),
    ODNOKL("odnoklassniki", SHARE_TITLE),
    MOIMIR("moimir", Dictionary.Home.MySites.MOIMIR, SHARE_TITLE),
    LJ("lj", "LiveJournal", SHARE_TITLE);

    private static final Properties CONFIG = new Properties();
    public String name;
    public Matcher<String> text;
    private String titlePattern;

    private static final String IMAGE_PARAM =
            "&image=%2F%2Fyastatic.net%2Fwww-skins%2F[0-9].[0-9]{1,3}%2Fskins%2Fbig%2F";

    private static final String IMAGE_PARAM_EXP =
            "&image=%2F%2Fyastatic.net%2Fwww-skins%2F[0-9].[0-9]{1,3}%2Fskins%2Fbig%2F";

    private static final String YANDEX_URL_REQUEST =
            UrlManager.encodeRequest("http://www.yandex" + CONFIG.getBaseDomain());
    private static final String SHARE_URL_PATTERN = "http://share.yandex.ru/go.xml?service=%s&url=%s";

    private SocialIcon(String name, String titlePattern) {
        this.name = name;
        this.titlePattern = titlePattern;
    }

    private SocialIcon(String name, TextID title) {
        this.name = name;
        this.text = not("");
        this.titlePattern = getTranslation(TRIM, title, new Properties().getLang());
    }


    private SocialIcon(String name, String text, TextID title) {
        this.name = name;
        this.text = startsWith(text);
        this.titlePattern = getTranslation(TRIM, title, new Properties().getLang());
    }


    private SocialIcon(String name, TextID text, TextID title) {
        this.name = name;
        this.text = startsWith(getTranslation(text, new Properties().getLang()));
        this.titlePattern = getTranslation(title, new Properties().getLang());
    }

    public Matcher<String> getHrefMatcher(String skinId) {
        String notationRequest = UrlManager.encodeRequest(skinId);
        String titleRequest = UrlManager.encodeRequest(
                titlePattern.replace("%1$s", getTranslation("home", "allskins", skinId, new Properties().getLang()))
//                        .replace("%21", "!")
        );
        if (CONFIG.getLang().equals(Language.TT)) {
            titleRequest = titleRequest.replace("%0A", "%0D%0A");
        }
        String imageParam;
        if (CONFIG.getBaseDomain().equals(Domain.RU)) {
            imageParam = IMAGE_PARAM;
        } else {
            imageParam = IMAGE_PARAM_EXP;
        }

        return matches((String.format(SHARE_URL_PATTERN, name, YANDEX_URL_REQUEST) + "%2Fthemes%2F" + notationRequest +
                "&title=" + titleRequest + imageParam + notationRequest + "%2Fpreview.png")
                .replace(".", "\\.").replace("?", "\\?"));
    }
}
