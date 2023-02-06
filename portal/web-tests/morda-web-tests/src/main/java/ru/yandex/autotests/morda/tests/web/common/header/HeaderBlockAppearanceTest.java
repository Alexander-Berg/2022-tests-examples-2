package ru.yandex.autotests.morda.tests.web.common.header;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.desktop.com.DesktopComMorda;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithHeader;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollectorRule;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.users.User;
import ru.yandex.autotests.utils.morda.users.UserType;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.net.MalformedURLException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.junit.Assume.assumeFalse;
import static ru.yandex.autotests.morda.pages.desktop.yaru.DesktopYaruMorda.desktopYaru;
import static ru.yandex.autotests.morda.pages.touch.comtr.TouchComTrMorda.touchComTr;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 09/04/15
 */
@Aqua.Test(title = "Header Block Appearance")
@Features("Header")
@Stories("Header Block Appearance")
@RunWith(Parameterized.class)
public class HeaderBlockAppearanceTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private CommonMordaSteps user;
    private HierarchicalErrorCollectorRule collectorRule;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda<? extends PageWithHeader<? extends Validateable>>> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();
        String userAgentTouch = CONFIG.getMordaUserAgentTouchIphone();

        data.addAll(DesktopMainMorda.getDefaultList(scheme, environment));
        data.addAll(DesktopComMorda.getDefaultList(scheme, environment));
        data.add(desktopYaru(scheme, environment));
        data.add(touchComTr(scheme, environment, Region.ISTANBUL, userAgentTouch));
        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    private Morda<? extends PageWithHeader<? extends Validateable>> morda;
    private PageWithHeader<? extends Validateable> page;
    private Cleanvars cleanvars;

    public HeaderBlockAppearanceTest(Morda<? extends PageWithHeader<? extends Validateable>> morda) {
        this.morda = morda;
        this.collectorRule = new HierarchicalErrorCollectorRule();
        this.mordaAllureBaseRule = this.morda.getRule().withRule(collectorRule);
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
    public void headerBlockAppearanceAuthorized() throws InterruptedException, MalformedURLException {
        assumeFalse(morda.getMordaType().equals(MordaType.D_MAIN));

        User login = mordaAllureBaseRule.getUser(UserType.DEFAULT);

        user.logsInAs(login, morda.getPassportUrl().toURL());
//        new PassportRule(driver)
//                .onHost(morda.getPassportUrl().toURL())
//                .withLoginPassword(login.getLogin(), login.getPassword())
//                .login();

        user.opensPage(morda.getUrl().toString());

        String requestId = (String) ((JavascriptExecutor) driver)
                .executeScript("return document.getElementById('requestId').innerHTML");
        Client client = MordaClient.getJsonEnabledClient();
        cleanvars = client.target("http://morda-mocks.wdevx.yandex.ru/api/v1/dumps/" + requestId + "/cleanvars")
                .request()
                .buildGet().invoke().readEntity(Cleanvars.class);

        Validator<?> validator = new Validator<>(driver, morda);
        validator.setUser(login);
        validator.setCleanvars(cleanvars);

        collectorRule.getCollector()
                .check(page.getHeaderBlock().validate(validator));
    }

    @Test
    public void headerBlockAppearance() throws InterruptedException {
        user.opensPage(morda.getUrl().toString());
        String requestId = (String) ((JavascriptExecutor) driver)
                .executeScript("return document.getElementById('requestId').innerHTML");
        Client client = MordaClient.getJsonEnabledClient();
        cleanvars = client.target("http://morda-mocks.wdevx.yandex.ru/api/v1/dumps/" + requestId + "/cleanvars")
                .request()
                .buildGet().invoke().readEntity(Cleanvars.class);

        Validator<?> validator = new Validator<>(driver, morda);

        validator.setCleanvars(cleanvars);
        collectorRule.getCollector()
                .check(page.getHeaderBlock().validate(validator));
    }
}
