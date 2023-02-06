package ru.yandex.autotests.mainmorda.data;

import ch.lambdaj.Lambda;
import ch.lambdaj.function.convert.Converter;
import org.hamcrest.CoreMatchers;
import org.hamcrest.Matcher;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.mordaexportsclient.beans.DirectV12Entry;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.url.Domain;

import java.util.List;

import static ch.lambdaj.Lambda.on;
import static java.lang.String.format;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.Matchers.anyOf;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mainmorda.utils.LinkUtils.normalizeUrl;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.TITLE;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.DIRECT_V12;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.mordaexportslib.matchers.LangMatcher.lang;
import static ru.yandex.autotests.mordaexportslib.matchers.MordatypeMatcher.mordatype;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Business.DIRECT;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Foot.ADV;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Foot.ARTLEBEDEV_STUDIO;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Foot.BLOG;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Foot.COMPANY;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Foot.DESIGN;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Foot.FEEDBACK;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Foot.FOOT_VACANCIES;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Foot.HELP;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Services.SERVICE_METRIC;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.url.Domain.UA;

/**
 * User: leonsabr
 * Date: 21.03.12
 */
public class FooterData {
    private static final Properties CONFIG = new Properties();

    private static Matcher<String> getDirect(Object argument) {
        List<DirectV12Entry> direct = exports(DIRECT_V12, mordatype(CONFIG.getBaseDomain()), lang(CONFIG.getLang()));
        if (direct == null || direct.size() == 0) {
            return equalTo("");
        }
        return anyOf(Lambda.convert(Lambda.extract(direct, argument), new Converter<String, Matcher<String>>() {
            @Override
            public Matcher<String> convert(String from) {
                return equalTo(normalizeUrl(from, CONFIG.getProtocol()));
            }
        }).toArray(new Matcher[0]));
    }

    private static final Matcher<String> ABOUT_TEXT = CoreMatchers.equalTo("About");
    private static final Matcher<String> ABOUT_HREF = CoreMatchers.equalTo("https://company.yandex.com/");

    private static final Matcher<String> COMPANY_HREF = CoreMatchers.equalTo("https://yandex.ru/company/");

    private static final Matcher<String> BLOG_HREF;
    static {
        if (CONFIG.getBaseDomain().equals(UA)) {
            BLOG_HREF = CoreMatchers.equalTo("https://blog.yandex.ua/");
        } else {
            BLOG_HREF = CoreMatchers.equalTo("https://blog.yandex.ru/");
        }
    }

    private static final Matcher<String> ARTLEBEDEV_HREF = CoreMatchers.equalTo("http://www.artlebedev.ru/");

    private static final Matcher<String> DIRECT_HREF = getDirect(on(DirectV12Entry.class).getHref());

    private static final Matcher<String> DIRECT_COMMENT_URL = startsWith("http://welcome.advertising.yandex.ru/");
    private static final Matcher<String> DIRECT_COMMENT = getDirect(on(DirectV12Entry.class).getSubtitle());
    private static final Matcher<String> DIRECT_COMMENT_HREF = getDirect(on(DirectV12Entry.class).getSubhref());

    private static final String FEEDBACK_HREF_PATTERN = "https://feedback2.yandex%s/default/";
    private static final Matcher<String> FEEDBACK_HREF =
            CoreMatchers.equalTo(String.format(FEEDBACK_HREF_PATTERN, CONFIG.getBaseDomain()));
    private static final Matcher<String> FEEDBACK_TITLE =
            CoreMatchers.equalTo(getTranslation(FEEDBACK, CONFIG.getLang()));

    private static final String ADV_HREF_PATTERN = "https://advertising.yandex%s/?from=main_bottom";
    private static final Matcher<String> ADV_HREF = equalTo(String.format(ADV_HREF_PATTERN, CONFIG.getBaseDomain()));

    private static final String YANDEX_DEFAULT_HREF_PATTERN = "https://set.yandex%s";
    private static final String YANDEX_FIREFOX_HREF_PATTERN = "https://yandex%s/set";
    private static final Matcher<String> YANDEX_DEFAULT_HREF = anyOf(
            startsWith(format(YANDEX_DEFAULT_HREF_PATTERN, CONFIG.getBaseDomain())),
            startsWith(format(YANDEX_FIREFOX_HREF_PATTERN, CONFIG.getBaseDomain())));





    private static final String METRIKA_HREF_PATTERN;
    private static final String METRIKA_SECURE_HREF_PATTERN;

    static {
        if (CONFIG.domainIs(UA) && CONFIG.getLang().equals(Language.RU)) {
            METRIKA_HREF_PATTERN = String.format("https://metrika.yandex%s/", Domain.RU);
            METRIKA_SECURE_HREF_PATTERN = String.format("https://metrika.yandex%s/", Domain.RU);

        } else {
            METRIKA_HREF_PATTERN = String.format("https://metrika.yandex%s/", CONFIG.getBaseDomain());
            METRIKA_SECURE_HREF_PATTERN = String.format("https://metrika.yandex%s/", CONFIG.getBaseDomain());
        }
    }

    private static final Matcher<String> METRIKA_HREF =
            CoreMatchers.equalTo(String.format(METRIKA_HREF_PATTERN, CONFIG.getBaseDomain()));
    private static final Matcher<String> METRIKA_URL =
            startsWith(String.format(METRIKA_SECURE_HREF_PATTERN, CONFIG.getBaseDomain()));

    private static final Matcher<String> VACANCIES_HREF;
    static {
        if (CONFIG.getBaseDomain().equals(Domain.UA)) {
            VACANCIES_HREF = startsWith("https://yandex.ua/jobs");
        } else {
            VACANCIES_HREF = startsWith("https://yandex.ru/jobs");
        }
    }

    private static final String HELP_HREF_PATTERN = "https://yandex%s/support/";
    private static final Matcher<String> HELP_TITLE = CoreMatchers.equalTo(getTranslation(HELP, CONFIG.getLang()));
    private static final Matcher<String> HELP_HREF;

    static {
        if (CONFIG.getLang().equals(Language.UK)) {
            HELP_HREF = CoreMatchers.equalTo(String.format(HELP_HREF_PATTERN, UA));
        } else {
            HELP_HREF = CoreMatchers.equalTo(String.format(HELP_HREF_PATTERN, Domain.RU));
        }
    }

    public static final Matcher<String> COPYRIGHT_TEXT = CoreMatchers.equalTo("© Яндекс");

    public static final Matcher<String> DESIGN_LOGOFF_TEXT =
            CoreMatchers.equalTo(getTranslation(DESIGN, CONFIG.getLang()) + " — "
                    + getTranslation(ARTLEBEDEV_STUDIO, CONFIG.getLang()));

    public static final LinkInfo LINK_ABOUT = new LinkInfo(
            ABOUT_TEXT,
            ABOUT_HREF,
            hasAttribute(HREF, ABOUT_HREF),
            hasAttribute(TITLE, CoreMatchers.equalTo(""))
    );

    public static final LinkInfo LINK_COMPANY = new LinkInfo(
            CoreMatchers.equalTo(getTranslation(COMPANY, CONFIG.getLang())),
            COMPANY_HREF,
            hasAttribute(HREF, COMPANY_HREF),
            hasAttribute(TITLE, CoreMatchers.equalTo(""))
    );

    public static final LinkInfo LINK_ARTLEBEDEV = new LinkInfo(
            CoreMatchers.equalTo(getTranslation(ARTLEBEDEV_STUDIO, CONFIG.getLang())),
            ARTLEBEDEV_HREF
    );

    public static final LinkInfo LINK_DIRECT = new LinkInfo(
            CoreMatchers.equalTo(getTranslation(DIRECT, CONFIG.getLang())),
            DIRECT_HREF);

    public static final LinkInfo LINK_DIRECT_COMMENT = new LinkInfo(
            DIRECT_COMMENT,
            DIRECT_COMMENT_URL,
            hasAttribute(HREF, DIRECT_COMMENT_HREF)
    );

    public static final LinkInfo LINK_ADV = new LinkInfo(
            equalTo(getTranslation(ADV, CONFIG.getLang())),
            ADV_HREF,
            hasAttribute(HREF, ADV_HREF)
    );

    public static final LinkInfo LINK_FEEDBACK = new LinkInfo(
            CoreMatchers.equalTo(""),
            FEEDBACK_HREF,
            hasAttribute(HREF, FEEDBACK_HREF),
            hasAttribute(TITLE, FEEDBACK_TITLE)
    );

    public static final LinkInfo LINK_YANDEX_DEFAULT = new LinkInfo(
            CoreMatchers.equalTo(getTranslation("home","business","switchToYandex", CONFIG.getLang())),
            YANDEX_DEFAULT_HREF
    );

    public static final LinkInfo LINK_HELP = new LinkInfo(
            CoreMatchers.equalTo(""),
            HELP_HREF,
            hasAttribute(HREF, HELP_HREF),
            hasAttribute(TITLE, HELP_TITLE)
    );

    public static final LinkInfo LINK_METRIKA = new LinkInfo(
            CoreMatchers.equalTo(getTranslation(SERVICE_METRIC, CONFIG.getLang())),
            METRIKA_URL
    );

    public static final LinkInfo LINK_VACANCIES = new LinkInfo(
            equalTo(getTranslation(FOOT_VACANCIES, CONFIG.getLang())),
            VACANCIES_HREF,
            hasAttribute(HREF, VACANCIES_HREF)
    );

    public static final LinkInfo LINK_BLOG = new LinkInfo(
            CoreMatchers.equalTo(getTranslation(BLOG, CONFIG.getLang())),
            BLOG_HREF,
            hasAttribute(HREF, BLOG_HREF)
    );

}
