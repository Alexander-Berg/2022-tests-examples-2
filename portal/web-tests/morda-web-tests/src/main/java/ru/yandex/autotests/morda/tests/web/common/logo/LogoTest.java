package ru.yandex.autotests.morda.tests.web.common.logo;

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
import ru.yandex.autotests.morda.pages.desktop.com404.Com404Morda;
import ru.yandex.autotests.morda.pages.desktop.firefox.DesktopFirefoxMorda;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithLogo;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollectorRule;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.morda.pages.desktop.comtr.DesktopComTrMorda.desktopComTr;
import static ru.yandex.autotests.morda.pages.desktop.comtr.DesktopComTrMorda.desktopFamilyComTr;
import static ru.yandex.autotests.morda.pages.desktop.comtrall.DesktopComTrAllMorda.desktopComTrAll;
import static ru.yandex.autotests.morda.pages.desktop.comtrall.DesktopComTrAllMorda.desktopFamilyComTrAll;
import static ru.yandex.autotests.morda.pages.desktop.comtrfootball.DesktopComTrFootballMorda.desktopComTrBjk;
import static ru.yandex.autotests.morda.pages.desktop.comtrfootball.DesktopComTrFootballMorda.desktopComTrGs;
import static ru.yandex.autotests.morda.pages.desktop.comtrfootball.DesktopComTrFootballMorda.desktopFamilyComTrBjk;
import static ru.yandex.autotests.morda.pages.desktop.comtrfootball.DesktopComTrFootballMorda.desktopFamilyComTrGs;
import static ru.yandex.autotests.morda.pages.desktop.hwbmw.DesktopHwBmwMorda.desktopHwBmw;
import static ru.yandex.autotests.morda.pages.desktop.hwlg.DesktopHwLgMorda.desktopHwLg;
import static ru.yandex.autotests.morda.pages.desktop.hwlgV2.DesktopHwLgV2Morda.desktopHwLgV2;
import static ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda.desktopFamilyMain;
import static ru.yandex.autotests.morda.pages.desktop.mainall.DesktopMainAllMorda.desktopFamilyMainAll;
import static ru.yandex.autotests.morda.pages.desktop.mainall.DesktopMainAllMorda.desktopMainAll;
import static ru.yandex.autotests.morda.pages.desktop.page404.Desktop404Morda.desktop404by;
import static ru.yandex.autotests.morda.pages.desktop.page404.Desktop404Morda.desktop404com;
import static ru.yandex.autotests.morda.pages.desktop.page404.Desktop404Morda.desktop404comTr;
import static ru.yandex.autotests.morda.pages.desktop.page404.Desktop404Morda.desktop404kz;
import static ru.yandex.autotests.morda.pages.desktop.page404.Desktop404Morda.desktop404ru;
import static ru.yandex.autotests.morda.pages.desktop.page404.Desktop404Morda.desktop404ua;
import static ru.yandex.autotests.morda.pages.desktop.yaru.DesktopYaruMorda.desktopYaru;
import static ru.yandex.autotests.morda.pages.pda.com.PdaComMorda.pdaCom;
import static ru.yandex.autotests.morda.pages.pda.comtr.PdaComTrMorda.pdaComTr;
import static ru.yandex.autotests.morda.pages.pda.comtrall.PdaComTrAllMorda.pdaComTrAll;
import static ru.yandex.autotests.morda.pages.pda.ru.PdaRuMorda.pdaRu;
import static ru.yandex.autotests.morda.pages.pda.ruall.PdaRuAllMorda.pdaRuAll;
import static ru.yandex.autotests.morda.pages.pda.yaru.PdaYaRuMorda.pdaYaRu;
import static ru.yandex.autotests.morda.pages.touch.com.TouchComMorda.touchCom;
import static ru.yandex.autotests.morda.pages.touch.comtr.TouchComTrMorda.touchComTr;
import static ru.yandex.autotests.morda.pages.touch.comtrall.TouchComTrAllMorda.touchComTrAll;
import static ru.yandex.autotests.morda.pages.touch.comtrwp.TouchComTrWpMorda.touchComTrWp;
import static ru.yandex.autotests.morda.pages.touch.ruall.TouchRuAllMorda.touchRuAll;
import static ru.yandex.autotests.morda.pages.touch.ruwp.TouchRuWpMorda.touchRuWp;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;

//import static ru.yandex.autotests.morda.pages.desktop.firefox.DesktopFirefoxMorda.desktopFirefoxComTr;
//import static ru.yandex.autotests.morda.pages.desktop.firefox.DesktopFirefoxMorda.desktopFirefoxRu;
//import static ru.yandex.autotests.morda.pages.desktop.firefox.DesktopFirefoxMorda.desktopFirefoxUa;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 28/02/15
 */
@Aqua.Test(title = "Logo")
@Features("Logo")
@Stories("Logo")
@RunWith(Parameterized.class)
public class LogoTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private CommonMordaSteps user;
    private HierarchicalErrorCollectorRule collectorRule;

    @Parameterized.Parameters(name = "{0}")
    @Stories("{0}")
    public static Collection<Object[]> data() {
        List<Morda<? extends PageWithLogo<? extends Validateable>>> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();
        String userAgentTouchIphone = CONFIG.getMordaUserAgentTouchIphone();
        String userAgentTouchWp = CONFIG.getMordaUserAgentTouchWp();
        String userAgentPda = CONFIG.getMordaUserAgentPda();

        data.addAll(DesktopMainMorda.getDefaultList(scheme, environment));
        data.add(desktopFamilyMain(scheme, environment, MOSCOW));

        data.addAll(Com404Morda.getDefaultList(scheme, environment));
        data.addAll(DesktopComMorda.getDefaultList(scheme, environment));
        data.add(desktopYaru(scheme, environment));


        data.addAll(DesktopFirefoxMorda.getDefaultList(scheme, environment));

        data.add(desktopComTr(scheme, environment));
        data.add(desktopFamilyComTr(scheme, environment));

        data.add(desktopComTrBjk(scheme, environment));
        data.add(desktopComTrGs(scheme, environment));
        data.add(desktopFamilyComTrGs(scheme, environment));
        data.add(desktopFamilyComTrBjk(scheme, environment));

        data.add(desktopHwLg(scheme, environment));
        data.add(desktopHwLgV2(scheme, environment));
        data.add(desktopHwBmw(scheme, environment));

        data.add(desktop404ru(scheme, environment));
        data.add(desktop404ua(scheme, environment));
        data.add(desktop404by(scheme, environment));
        data.add(desktop404kz(scheme, environment));
        data.add(desktop404com(scheme, environment));
        data.add(desktop404comTr(scheme, environment));

        data.add(desktopMainAll(scheme, environment, MOSCOW));
        data.add(desktopFamilyMainAll(scheme, environment, MOSCOW));
        data.add(desktopComTrAll(scheme, environment));
        data.add(desktopFamilyComTrAll(scheme, environment));

        data.addAll(TouchRuMorda.getDefaultList(scheme, environment, userAgentTouchIphone));
        data.add(touchCom(scheme, environment, userAgentTouchIphone));
        data.add(touchComTr(scheme, environment, Region.ISTANBUL, userAgentTouchIphone));
        data.add(touchRuAll(scheme, environment, userAgentTouchIphone));
        data.add(touchComTrAll(scheme, environment, Region.ISTANBUL, userAgentTouchIphone));
        data.add(touchRuWp(scheme, environment, userAgentTouchWp));
        data.add(touchComTrWp(scheme, environment, Region.ISTANBUL, userAgentTouchWp));

        data.add(pdaComTr(scheme, environment, userAgentPda));
        data.add(pdaCom(scheme, environment, userAgentPda));
        data.add(pdaRu(scheme, environment, userAgentPda));
        data.add(pdaRuAll(scheme, environment, userAgentPda));
        data.add(pdaComTrAll(scheme, environment, userAgentPda));
        data.add(pdaYaRu(scheme, environment, userAgentPda));


        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));//.subList(0,1);
    }

    private Morda<? extends PageWithLogo<? extends Validateable>> morda;
    private PageWithLogo<? extends Validateable> page;
    private String requestId;
    private Cleanvars cleanvars;

    public LogoTest(Morda<? extends PageWithLogo<? extends Validateable>> morda) {
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
    }

    @Test
    public void logo() throws InterruptedException {
        Client client = MordaClient.getJsonEnabledClient();
        if (!(morda instanceof DesktopFirefoxMorda)) {
            Validator<?> validator = new Validator<>(driver, morda);
            collectorRule.getCollector()
                    .check(page.getLogo().validate(validator));
        }else{
            requestId = (String) ((JavascriptExecutor) driver)
                    .executeScript("return document.getElementById('requestId').innerHTML");
            System.out.println(requestId);
            this.cleanvars = client.target("http://morda-mocks.wdevx.yandex.ru/api/v1/dumps/" + requestId + "/cleanvars")
                    .request()
                    .buildGet().invoke().readEntity(Cleanvars.class);

            Validator validator = new Validator<>(driver, morda).withCleanvars(cleanvars);

            collectorRule.getCollector()
                    .check(page.getLogo().validate(validator));
        }
    }
}
