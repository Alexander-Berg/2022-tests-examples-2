package ru.yandex.autotests.tune.tests;

import com.fasterxml.jackson.core.JsonProcessingException;
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
import ru.yandex.autotests.morda.steps.TuneSteps;
import ru.yandex.autotests.tune.TuneTestsProperties;
import ru.yandex.autotests.tune.data.mordas.TouchTuneMainMorda;
import ru.yandex.autotests.tune.data.mordas.TuneMorda;
import ru.yandex.autotests.tune.data.pages.AdvPage;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.lang.Thread.sleep;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.junit.Assume.assumeThat;
import static ru.yandex.autotests.morda.pages.MordaType.TOUCH_TUNE;
import static ru.yandex.autotests.tune.data.mordas.TouchTuneComMorda.touchTuneCom;

/**
 * User: asamar
 * Date: 12.12.16
 */
@Aqua.Test(title = "Tune adv page")
@Features({"Tune", "Touch"})
@RunWith(Parameterized.class)
public class AdvPageTest {
    private static TuneTestsProperties CONFIG = new TuneTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<? super TuneMorda> data() {
        List<? super TuneMorda> mordas = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();
        String useragentTouch = CONFIG.getMordaUserAgentTouchIphone();

        mordas.addAll(TouchTuneMainMorda.getDefaultList(scheme, environment, useragentTouch));
        mordas.add(touchTuneCom(scheme, environment, useragentTouch, MordaLanguage.EN));

        return mordas;
    }

    @Rule
    public MordaBaseWebDriverRule rule;
    public HierarchicalErrorCollectorRule collectorRule;
    private WebDriver driver;
    private AdvPage page;
    private TuneMorda morda;

    public AdvPageTest(TuneMorda morda) {
        this.morda = morda;
        this.collectorRule = new HierarchicalErrorCollectorRule();
        this.rule = morda.getRule().around(collectorRule);
        this.driver = rule.getDriver();
    }

    @Before
    public void init() throws InterruptedException, JsonProcessingException {
        WebPage webPage = morda.initialize(driver, AdvPage.class);
        this.page = (AdvPage) webPage;
    }

    @Test
    public void appearanceTest() {
        Validator<TuneMorda> validator = new Validator<>(driver, morda);
        collectorRule.getCollector()
                .check(page.validate(validator));
    }

    @Test
    public void myLocationTest() throws InterruptedException {
        page.disableLocation();
        sleep(500);
        TuneSteps.myShouldContains(driver, morda.getCookieDomain(), 58);
    }

    @Test
    public void myInterestsTest() throws InterruptedException {
        page.disableInterests();
        sleep(500);
        TuneSteps.myShouldContains(driver, morda.getCookieDomain(), 38);
    }

    @Test
    public void advTest() throws InterruptedException {
        assumeThat("На Com нет настройки баннера", morda.getMordaType(), equalTo(TOUCH_TUNE));
        page.disableAdv();
        sleep(500);
        TuneSteps.myShouldContains(driver, morda.getCookieDomain(), 46);
    }


}
