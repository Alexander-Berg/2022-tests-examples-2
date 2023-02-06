package ru.yandex.autotests.tune.tests;

import io.qameta.htmlelements.WebPage;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.data.validation.Validator;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.rules.base.MordaBaseWebDriverRule;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollectorRule;
import ru.yandex.autotests.tune.TuneTestsProperties;
import ru.yandex.autotests.tune.data.mordas.TouchTuneComTrMorda;
import ru.yandex.autotests.tune.data.mordas.TouchTuneMainMorda;
import ru.yandex.autotests.tune.data.mordas.TuneMorda;
import ru.yandex.autotests.tune.data.pages.SearchPage;
import ru.yandex.geobase.regions.Turkey;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.lang.Thread.sleep;
import static ru.yandex.autotests.morda.steps.TuneSteps.ypShouldContains;
import static ru.yandex.autotests.tune.data.mordas.TouchTuneComMorda.touchTuneCom;

/**
 * User: asamar
 * Date: 13.12.16
 */
@Aqua.Test(title = "Tune search page")
@Features({"Tune", "Touch"})
@RunWith(Parameterized.class)
public class SearchPageTest {
    private static TuneTestsProperties CONFIG = new TuneTestsProperties();
    private static final String FAMILY_SEARCH_SUBSTR = "sp.family:2";
    private static final String NEW_WINDOW_SUBSTR = "sp.tg:_self";

    @Parameterized.Parameters(name = "{0}")
    public static Collection<? super TuneMorda> data() {
        List<? super TuneMorda> mordas = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();
        String useragentTouch = CONFIG.getMordaUserAgentTouchIphone();

        mordas.addAll(TouchTuneMainMorda.getDefaultList(scheme, environment, useragentTouch));
        mordas.add(TouchTuneComTrMorda.touchTuneComTr(scheme, environment, useragentTouch, Turkey.ISTANBUL_11508));
        mordas.add(touchTuneCom(scheme, environment, useragentTouch, MordaLanguage.EN));

        return mordas;
    }

    @Rule
    public MordaBaseWebDriverRule rule;
    public HierarchicalErrorCollectorRule collectorRule;
    private WebDriver driver;
    private SearchPage page;
    private TuneMorda morda;

    public SearchPageTest(TuneMorda morda) {
        this.morda = morda;
        this.collectorRule = new HierarchicalErrorCollectorRule();
        this.rule = morda.getRule().around(collectorRule);
        this.driver = rule.getDriver();
    }

    @Before
    public void init() throws InterruptedException {
        WebPage webPage = morda.initialize(driver, SearchPage.class);
        this.page = (SearchPage) webPage;
    }

    @Test
    public void appearanceTest() {
        Validator<? extends TuneMorda> validator = new Validator<>(driver, morda);
        collectorRule.getCollector()
                .check(page.validate(validator));
    }

    @Test
    public void familySearchTest() throws InterruptedException {
        page.checkFamilySearch();
        sleep(500);
        ypShouldContains(driver, morda.getCookieDomain(), FAMILY_SEARCH_SUBSTR);
    }

    @Test
    public void newWindowTest() throws InterruptedException {
        page.unCheckNewWindow();
        sleep(500);
        ypShouldContains(driver, morda.getCookieDomain(), NEW_WINDOW_SUBSTR);
    }

//    @Test
    public void favouriteReqTest() throws InterruptedException {
        page.checkFavouriteReq();
        sleep(500);
        ypShouldContains(driver, morda.getCookieDomain(), FAMILY_SEARCH_SUBSTR);
    }

}
