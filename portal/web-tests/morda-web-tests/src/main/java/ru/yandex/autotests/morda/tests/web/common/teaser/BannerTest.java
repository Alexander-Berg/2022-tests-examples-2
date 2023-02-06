package ru.yandex.autotests.morda.tests.web.common.teaser;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainPage;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.allure.annotations.Stories;

import static org.hamcrest.CoreMatchers.containsString;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.junit.Assert.fail;
import static org.junit.Assume.assumeFalse;
import static ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.VALUE;
import static ru.yandex.qatools.htmlelements.matchers.common.DoesElementExistMatcher.exists;

/**
 * User: alex89
 * Date: 09.04.12
 */
@Aqua.Test(title = "Появление баннера и параметры")
@Features({"Banner"})
public class BannerTest {
    private static final String AWAPS_HREF_PATTERN = ".*https?://awaps.yandex.net/.*";
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private CommonMordaSteps user;
    private DesktopMainMorda morda;
    private DesktopMainPage page;

    public BannerTest() {
        this.morda = desktopMain(CONFIG.getMordaScheme(), CONFIG.getMordaEnvironment(), Region.MOSCOW);
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.page = morda.getPage(driver);
    }

    @Before
    public void initLanguage() {
        morda.initialize(driver);
        user.opensPage("http://awaps.yandex.ru/?adt_id=82599");
        shouldSeeAdtIdOnAwapsPage("82599");
        user.opensPage(morda.getUrl().toASCIIString());
    }

    @Test
    public void banner() {
        triesToNoticeBanner();
        user.shouldSeeElementMatchingTo(page.getBanner().flashParam,
                hasAttribute(VALUE, matches(AWAPS_HREF_PATTERN)));
        user.shouldSeeElementMatchingTo(page.getBanner().movieParam,
                hasAttribute(VALUE, matches(AWAPS_HREF_PATTERN)));
    }

    @Step("Should see adt_id {0} on awaps page")
    public void shouldSeeAdtIdOnAwapsPage(String s) {
        assertThat("В ответе awaps нет id " + s, driver.getPageSource(), containsString(s));
    }

    @Step
    public void triesToNoticeBanner() {
        excludeDomain();
        for (int i = 0; i < 5; i++) {
            driver.get(driver.getCurrentUrl());
            if (exists().matches(page.getBanner())) {
                return;
            }
        }
        fail("Баннер не показался после 5 перезагрузок страницы");
    }

    private void excludeDomain() {
        String domain = morda.getDomain();
        assumeFalse("Для домена " + morda.getDomain() + " баннер может и не показываться",
                domain.equals(".ua") || domain.equals(".kz"));
    }
}