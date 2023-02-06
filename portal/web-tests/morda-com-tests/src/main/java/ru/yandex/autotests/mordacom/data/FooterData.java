package ru.yandex.autotests.mordacom.data;

import org.hamcrest.Matcher;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.utils.morda.language.Language;

import static org.hamcrest.CoreMatchers.equalTo;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.FOOT_TERMS;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.FOOT_COMPANY;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.FOOT_API;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.FOOT_PRIVACY;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.SpokYes.FOOT_COPYRIGHT;

/**
 * User: leonsabr
 * Date: 18.08.2010
 */
public class FooterData {

    private static final String TECHNOLOGIES_HREF = "https://tech.yandex.com/";
    private static final String TECHNOLOGIES_URL = "https://tech.yandex.com/";

    private static final String ABOUT_HREF = "https://company.yandex.com/";

    private static final String TERMSOFSERVICE_HREF = "https://legal.yandex.com/termsofservice/";

    private static final String PRIVACY_HREF = "https://legal.yandex.com/privacy/";

    private static final String COPYRIGHT_HREF = "https://feedback2.yandex.com/copyright-complaint/";

    public static final Matcher<String> COPYRIGHT_TEXT_MATCHER = equalTo("© Yandex");

    public static final Matcher<String> TEXT_COMPLETE_MATCHER = equalTo("TechnologiesAbout YandexTerms of Service" +
            "Privacy PolicyCopyright Notice© Yandex");

    public static LinkInfo getTechnologiesLink(Language language) {
        return new LinkInfo(
                equalTo(getTranslation(FOOT_API, language)),
                equalTo(TECHNOLOGIES_URL),
                hasAttribute(HREF, equalTo(TECHNOLOGIES_HREF))
        );
    }

    public static LinkInfo getAboutLink(Language language) {
        return new LinkInfo(
                equalTo(getTranslation(FOOT_COMPANY, language)),
                equalTo(ABOUT_HREF)
        );
    }

    public static LinkInfo getLinkTermsOfService(Language language) {
        return new LinkInfo(
                equalTo(getTranslation(FOOT_TERMS, language)),
                equalTo(TERMSOFSERVICE_HREF)
        );
    }

    public static LinkInfo getLinkPrivacyPolicy(Language language) {
        return new LinkInfo(
                equalTo(getTranslation(FOOT_PRIVACY, language)),
                equalTo(PRIVACY_HREF)
        );
    }


    public static LinkInfo getLinkCopyrightNotice(Language language) {
        return new LinkInfo(
                equalTo(getTranslation(FOOT_COPYRIGHT, language)),
                equalTo(COPYRIGHT_HREF)
        );
    }

}
