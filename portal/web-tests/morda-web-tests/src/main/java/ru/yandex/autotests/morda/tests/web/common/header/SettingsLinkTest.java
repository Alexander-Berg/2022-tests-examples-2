package ru.yandex.autotests.morda.tests.web.common.header;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.desktop.main.blocks.HeaderBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithHeader;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.morda.utils.matchers.UrlMatcher;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.morda.utils.matchers.AllOfDetailedMatcher.allOfDetailed;
import static ru.yandex.autotests.morda.utils.matchers.UrlMatcher.ParamMatcher.urlParam;
import static ru.yandex.autotests.morda.utils.matchers.UrlMatcher.urlMatcher;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.autotests.utils.morda.url.UrlManager.encode;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.hasText;

/**
 * User: asamar
 * Date: 17.12.2015.
 */
@Aqua.Test(title = "Header Block Settings Link")
@Features("Header")
@Stories("Header Block Settings")
@RunWith(Parameterized.class)
public class SettingsLinkTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();

        List<Morda<? extends PageWithHeader<? extends Validateable>>> data = new ArrayList<>();

        data.add(desktopMain(scheme, environment,MOSCOW));
        data.add(desktopMain(scheme,environment, Region.KIEV));

        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }


    private WebDriver driver;
    private CommonMordaSteps user;
    private DesktopMainMorda morda;
    private PageWithHeader<? extends HeaderBlock> page;

    public SettingsLinkTest(DesktopMainMorda morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.page = morda.getPage(driver);
    }

    @Before
    public void init() {
        morda.initialize(driver);
    }

    @Test
    public void skinsLinkTest() {
        UrlMatcher setSkinMatcher = urlMatcher(morda.getUrl() + "themes")
                .build();
        user.clicksOn(page.getHeaderBlock().settings);
        user.shouldSeeElement(page.getHeaderBlock().settingsPopup);
        user.shouldSeeElement(page.getHeaderBlock().settingsPopup.setSkin);
        user.shouldSeeElementMatchingTo(page.getHeaderBlock().settingsPopup.setSkin, allOfDetailed(
                hasAttribute(HREF, setSkinMatcher),
                hasText(getTranslation("home", "head", "theme", morda.getLanguage()))
        ));
    }

    @Test
    public void settingsLinkTest() {
        UrlMatcher settingsLinkMatcher = urlMatcher(morda.getUrl())
                .urlParams(
                        urlParam("edit", "1")
                )
                .build();
        user.clicksOn(page.getHeaderBlock().settings);
        user.shouldSeeElement(page.getHeaderBlock().settingsPopup);
        user.shouldSeeElement(page.getHeaderBlock().settingsPopup.tuneYandex);
        user.shouldSeeElementMatchingTo(page.getHeaderBlock().settingsPopup.tuneYandex, allOfDetailed(
                hasAttribute(HREF, settingsLinkMatcher),
                hasText(getTranslation("home", "head", "ya", morda.getLanguage()))
        ));
    }


    @Test
    public void citiesLinkTest() {
        UrlMatcher citiesLinkMatcher = urlMatcher(morda.getTuneUrl())
                .path("/tune/geo/")
                .urlParams(
                        urlParam("retpath", encode(morda.getUrl() + "?domredir=1"))
                )
                .build();
        user.clicksOn(page.getHeaderBlock().settings);
        user.shouldSeeElement(page.getHeaderBlock().settingsPopup);
        user.shouldSeeElement(page.getHeaderBlock().settingsPopup.setCity);
        user.shouldSeeElementMatchingTo(page.getHeaderBlock().settingsPopup.setCity, allOfDetailed(
                hasAttribute(HREF, citiesLinkMatcher),
                hasText(getTranslation("home", "head", "region", morda.getLanguage()))
        ));
    }

    @Test
    public void otherSettingsLinkTest() {
        UrlMatcher otherSettingsLinkMatcher = urlMatcher(morda.getTuneUrl())
                .path("/tune/search/")
                .urlParams(
                        urlParam("retpath", encode(morda.getUrl() + "?domredir=1"))
                )
                .build();

        user.clicksOn(page.getHeaderBlock().settings);
        user.shouldSeeElement(page.getHeaderBlock().settingsPopup);
        user.shouldSeeElement(page.getHeaderBlock().settingsPopup.otherSettings);
        user.shouldSeeElementMatchingTo(page.getHeaderBlock().settingsPopup.otherSettings, allOfDetailed(
                hasAttribute(HREF, otherSettingsLinkMatcher),
                hasText(getTranslation("home", "head", "otherSettings", morda.getLanguage()))
        ));
    }
}
