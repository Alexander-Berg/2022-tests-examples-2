package ru.yandex.autotests.morda.tests.web.common.region;

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
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithRegionBlock;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollectorRule;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.morda.pages.MordaType.D_HWLG;
import static ru.yandex.autotests.morda.pages.desktop.hwlgV2.DesktopHwLgV2Morda.desktopHwLgV2;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 01/04/15
 */
@Aqua.Test(title = "Region Block Appearance")
@Features("Region")
@Stories("Region Block Appearance")
@RunWith(Parameterized.class)
public class RegionBlockAppearanceTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private HierarchicalErrorCollectorRule collectorRule;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda<? extends PageWithRegionBlock<? extends Validateable>>> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();

        data.add(desktopHwLgV2(scheme, environment));
        data.addAll(DesktopMainMorda.getDefaultList(scheme, environment));

        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    private Morda<? extends PageWithRegionBlock<? extends Validateable>> morda;
    private PageWithRegionBlock<? extends Validateable> page;
    private String requestId;
    private Cleanvars cleanvars;

    public RegionBlockAppearanceTest(Morda<? extends PageWithRegionBlock<? extends Validateable>> morda) {
        this.morda = morda;
        this.collectorRule = new HierarchicalErrorCollectorRule();
        this.mordaAllureBaseRule = this.morda.getRule().withRule(collectorRule);
        this.driver = mordaAllureBaseRule.getDriver();
        this.page = morda.getPage(driver);
    }

    @Before
    public void init() {
        morda.initialize(driver);

    }

    @Test
    public void regionAppearance() {
        if (morda.getMordaType().equals(D_HWLG)) {
            Validator validator = new Validator<>(driver, morda);
            collectorRule.getCollector()
                    .check(page.getRegionBlock().validate(validator));
        } else {
            requestId = (String) ((JavascriptExecutor) driver)
                    .executeScript("return document.getElementById('requestId').innerHTML");
            System.out.println(requestId);
            Client client = MordaClient.getJsonEnabledClient();
            this.cleanvars = client.target("http://morda-mocks.wdevx.yandex.ru/api/v1/dumps/" + requestId + "/cleanvars")
                    .request()
                    .buildGet().invoke().readEntity(Cleanvars.class);

            Validator validator = new Validator<>(driver, morda).withCleanvars(cleanvars);
            collectorRule.getCollector()
                    .check(page.getRegionBlock().validate(validator));
        }
    }
}
