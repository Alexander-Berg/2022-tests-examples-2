package ru.yandex.autotests.morda.tests.web.common.footer;

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
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithFooter;
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

import static ru.yandex.autotests.morda.pages.touch.comtr.TouchComTrMorda.touchComTr;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01/04/15
 */
@Aqua.Test(title = "Footer Block Appearance")
@Features("Footer")
@Stories("Footer Block Appearance")
@RunWith(Parameterized.class)
public class FooterBlockAppearanceTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private CommonMordaSteps user;
    private HierarchicalErrorCollectorRule collectorRule;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda<? extends PageWithFooter<? extends Validateable>>> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();
        String userAgentTouchIphone = CONFIG.getMordaUserAgentTouchIphone();
        String userAgentTouchWp = CONFIG.getMordaUserAgentTouchWp();
        String userAgentPda = CONFIG.getMordaUserAgentPda();

        data.addAll(DesktopMainMorda.getDefaultList(scheme, environment));

//        for (Region region : Arrays.asList(MOSCOW, KIEV, MINSK, ASTANA, ISTANBUL)) {
//            for (Language language : Arrays.asList(RU, UK, BE, KK, TT)) {
//                data.add(desktopFirefoxRu(scheme, environment, region, language));
//                data.add(desktopFirefoxUa(scheme, environment, region, language));
//
//            }
//            data.add(desktopFirefoxComTr(scheme, environment, region));
//        }

        data.addAll(DesktopFirefoxMorda.getDefaultList(scheme, environment));

        data.addAll(DesktopComMorda.getDefaultList(scheme, environment));
        data.addAll(Com404Morda.getDefaultList(scheme,environment));
        data.add(touchComTr(scheme, environment, Region.ISTANBUL, userAgentTouchIphone));
        data.addAll(TouchRuMorda.getDefaultList(scheme, environment, userAgentTouchIphone));

        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    private Morda<? extends PageWithFooter<? extends Validateable>> morda;
    private PageWithFooter<? extends Validateable> page;
    private String requestId;
    private Cleanvars cleanvars;

    public FooterBlockAppearanceTest(Morda<? extends PageWithFooter<? extends Validateable>> morda) {
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
    public void footerAppearance() {
        Client client = MordaClient.getJsonEnabledClient();
        if(morda instanceof Com404Morda){
            Validator validator = new Validator<>(driver, morda);
            collectorRule.getCollector()
                    .check(page.getFooterBlock().validate(validator));
        } else {

            requestId = (String) ((JavascriptExecutor) driver)
                    .executeScript("return document.getElementById('requestId').innerHTML");
            System.out.println(requestId);

            this.cleanvars = client.target("http://morda-mocks.wdevx.yandex.ru/api/v1/dumps/" + requestId + "/cleanvars")
                    .request()
                    .buildGet().invoke().readEntity(Cleanvars.class);

            Validator validator = new Validator<>(driver, morda).withCleanvars(cleanvars);
            collectorRule.getCollector()
                    .check(page.getFooterBlock().validate(validator));
        }
    }
}
