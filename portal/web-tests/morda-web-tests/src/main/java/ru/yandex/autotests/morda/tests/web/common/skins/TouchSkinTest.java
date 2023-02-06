package ru.yandex.autotests.morda.tests.web.common.skins;

import org.glassfish.jersey.apache.connector.ApacheConnectorProvider;
import org.hamcrest.Matchers;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuPage;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.morda.tests.web.utils.SkinSteps;
import ru.yandex.autotests.morda.utils.cookie.WebDriverCookieUtils;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.client.ClientUtils;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordaexportsclient.beans.ThemesEntry;
import ru.yandex.autotests.utils.morda.cookie.CookieManager;
import ru.yandex.autotests.utils.morda.users.User;
import ru.yandex.junitextensions.rules.passportrule.PassportRule;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.net.MalformedURLException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.Optional;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static java.lang.String.format;
import static java.util.stream.Collectors.toList;
import static org.hamcrest.CoreMatchers.anyOf;
import static org.hamcrest.CoreMatchers.containsString;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.is;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda.touchRu;
import static ru.yandex.autotests.mordacommonsteps.rules.proxy.actions.HarAction.addHar;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.WIDGET;
import static ru.yandex.autotests.mordaexportsclient.MordaExports.THEMES;
import static ru.yandex.autotests.mordaexportslib.ExportProvider.exports;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.autotests.utils.morda.users.UserType.DEFAULT;

/**
 * User: asamar
 * Date: 08.06.16
 */
@Aqua.Test(title = "Touch Skins")
@Features("Skins")
@Stories("Touch Skins")
@RunWith(Parameterized.class)
public class TouchSkinTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> getThemes() {

        List<Object[]> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String env = CONFIG.getMordaEnvironment();
        String userAgent = CONFIG.getMordaUserAgentTouchIphone();

        List<String> skinIds = exports(THEMES,
                having(on(ThemesEntry.class).getTouch(), equalTo(1)))
                .stream()
                .map(ThemesEntry::getId)
                .collect(toList());

        skinIds.forEach(id ->
                data.add(new Object[]{id, touchRu(scheme, env, userAgent, MOSCOW, RU)}));

        return data;
    }

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private TouchRuMorda touchRuMorda;
    private TouchRuPage touchRuPage;
    private CommonMordaSteps userSteps;
    private SkinSteps skinSteps;
    private User user;
    private String skinId;

    public TouchSkinTest(String skinId, TouchRuMorda morda) {
        this.skinId = skinId;
        this.touchRuMorda = morda;
        this.mordaAllureBaseRule = touchRuMorda.getRule().withProxyAction(addHar("skins_har"));
        this.user = mordaAllureBaseRule.getUser(DEFAULT, WIDGET);
        this.driver = mordaAllureBaseRule.getDriver();
        this.touchRuPage = touchRuMorda.getPage(driver);
        this.userSteps = new CommonMordaSteps(driver);
        this.skinSteps = new SkinSteps(driver);
    }

    @Before
    public void init() throws MalformedURLException {
        assumeThat("На девах не гоняем", CONFIG.getMordaEnvironment(),
                anyOf(containsString("rc"), containsString("production")));

        loginAndSetSkin(skinId);
        touchRuMorda.initialize(driver);
        userSteps.logsInAs(
                user,
                touchRuMorda.getPassportUrl().toURL(),
                touchRuMorda.getUrl().toString()
        );
    }

    @Test
    public void themeInDump() {
        String requestId = (String) ((JavascriptExecutor) driver)
                .executeScript("return document.getElementById('requestId').innerHTML");
        System.out.println(requestId);

        Client client = MordaClient.getJsonEnabledClient();
        Cleanvars cleanvars = client.target("http://morda-mocks.wdevx.yandex.ru/api/v1/dumps/" + requestId + "/cleanvars")
                .request()
                .buildGet().invoke().readEntity(Cleanvars.class);

        assertThat("Темы " + skinId + " нет в дампе", cleanvars.getThemes().getCurrent().getId(), equalTo(skinId));
    }

    //    @Test
    public void switchOffSkin() throws InterruptedException {
        skinSteps.disableSkinOnTouch(touchRuPage);

        Optional<String> mtdCookie = Arrays.stream(new WebDriverCookieUtils(driver)
                .getCookieNamed("yp", touchRuMorda.getCookieDomain())
                .getValue().split("#"))
                .filter(e -> e.contains("mtd.1"))
                .findFirst();

        assertThat("Параметр mtd не поставился в yp", mtdCookie.isPresent(), is(true));
        skinSteps.shouldNotSeeSkin(touchRuPage);
    }


    @Test
    public void skinCss() {
        skinSteps.shouldSeeSkinInTouch(touchRuPage, skinId, mordaAllureBaseRule.getCaps().getBrowserName());
    }

    @Test
    public void skinBackground() {
        userSteps.shouldSeeStaticIsDownloaded(mordaAllureBaseRule.getProxyServer().getHar());
        userSteps.shouldSeeElement(touchRuPage.getLogo());
    }

    @Test
    public void skinPromo() {
        userSteps.shouldSeeElement(touchRuPage.getSkinGreetingBlock());
        String flag = (String) ((JavascriptExecutor) driver).executeScript(
                format("return window.localStorage.getItem('%s');", "doNotShowSkinGreeting"));
        assertThat("Показ промо не записался в localStorage", flag, Matchers.equalTo("1"));
    }

//    @After
    public void resetSkin() {
        MordaClient.getJsonEnabledClient().target(
                touchRuMorda.getUrl() + "themes/default/set?sk=" + CookieManager.getSecretKey(driver))
                .request()
                .buildGet()
                .invoke();
    }

    @Step("Login and set skin \"{0}\"")
    public void loginAndSetSkin(String skinId){
        Client client = MordaClient.getJsonEnabledClient();

        new PassportRule(ApacheConnectorProvider.getHttpClient(client))
                .withLoginPassword(user.getLogin(), user.getPassword())
                .login();
        client.target(touchRuMorda.getUrl() + "themes/" + skinId + "/set?sk=" + CookieManager.getSecretKey(ClientUtils.getCookieStore(client)))
                .request()
                .buildGet()
                .invoke();
    }
}
