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
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.matchers.LoginMatcher;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.lang.Thread.sleep;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.mordacommonsteps.matchers.WithWaitForMatcher.withWaitFor;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;

/**
 * User: asamar
 * Date: 17.12.2015.
 */
@Aqua.Test(title = "Main Authorization")
@Features("Authorization")
@Stories("Main Authorization")
@RunWith(Parameterized.class)
public class AutorizationTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();

        List<Morda<? extends PageWithHeader<? extends Validateable>>> data = new ArrayList<>();

        data.add(desktopMain(scheme, environment, Region.MOSCOW));
        data.add(desktopMain(scheme, environment, Region.KIEV));

        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }


    private WebDriver driver;
    private CommonMordaSteps user;
    private DesktopMainMorda morda;
    private PageWithHeader<? extends HeaderBlock> page;

    public AutorizationTest(DesktopMainMorda morda) {
        this.morda = morda;
        this.mordaAllureBaseRule = morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.page = morda.getPage(driver);
    }

    @Before
    public void init() {
        morda.initialize(driver);
        user.resizeWindow(1280, 1024);
    }

    @Test
    public void login() throws InterruptedException {
        tryLogin("widgetnew-test", "widget");
        isLogged(driver);
    }

    @Test
    public void loginWithoutLogin() throws InterruptedException {
        tryLogin("", "wrong-password");
        notLogged(driver);
    }

    @Test
    public void loginWithoutPassword() throws InterruptedException {
        tryLogin("widgetnew-test", "");
        notLogged(driver);
    }

    @Test
    public void loginWithWrongPassword() throws InterruptedException {
        tryLogin("widgetnew-test", "wrong-password");
        notLogged(driver);
    }

    @Test
    public void logout() throws InterruptedException {
        tryLogin("widgetnew-test", "widget");
        isLogged(driver);
        Thread.sleep(2000);
        user.opensPage(morda.getUrl().toString());
        Thread.sleep(5000);
        tryLogout();
        notLogged(driver);
    }

    @Test
    public void invalidLoginPopup() throws InterruptedException {
        user.shouldSeeElement(page.getHeaderBlock().headerDomik);
        user.entersTextInInput(page.getHeaderBlock().headerDomik.loginField, " ");
        user.shouldSeeElement(page.getHeaderBlock().headerDomik.wrongLogin);
    }

    @Test
    public void shareAppearance() throws InterruptedException {
        user.shouldSeeElement(page.getHeaderBlock().headerDomik);
        user.shouldSeeElement(page.getHeaderBlock().headerDomik.shareMore);
        user.clicksOn(page.getHeaderBlock().headerDomik.shareMore);
        user.shouldNotSeeElement(page.getHeaderBlock().headerDomik.loginButton);
        shouldSeeShareLinks(page.getHeaderBlock().headerDomik.shareLinks);
    }

    @Step("Should be logged in")
    public void isLogged(WebDriver driver) throws InterruptedException {
        assertThat(driver, withWaitFor(LoginMatcher.isLogged()));
    }

    @Step("Should be not logged in")
    public void notLogged(WebDriver driver) throws InterruptedException {
        assertThat(driver, withWaitFor(not(LoginMatcher.isLogged())));
    }

    @Step("Should see share links")
    public void shouldSeeShareLinks(List<HtmlElement> links) {
        links.forEach(user::shouldSeeElement);
    }

    @Step("Try logout")
    public void tryLogout() throws InterruptedException {
        user.clicksOn(page.getHeaderBlock().dropDownUserMenu);
        user.clicksOn(page.getHeaderBlock().logoutButton);
        sleep(1000);
        user.refreshPage();
    }

    @Step("Try login")
    public void tryLogin(String login, String password) throws InterruptedException {
        user.shouldSeeElement(page.getHeaderBlock().headerDomik);
        page.getHeaderBlock().headerDomik.tryLogin(driver, login, password);
    }

}
