package ru.yandex.autotests.tune.tests;

import io.qameta.htmlelements.WebPage;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.data.validation.Validateable;
import ru.yandex.autotests.morda.data.validation.Validator;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.rules.base.MordaBaseWebDriverRule;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollectorRule;
import ru.yandex.autotests.tune.TuneTestsProperties;
import ru.yandex.autotests.tune.data.mordas.TouchTuneComTrMorda;
import ru.yandex.autotests.tune.data.mordas.TouchTuneMainMorda;
import ru.yandex.autotests.tune.data.mordas.TuneMorda;
import ru.yandex.autotests.tune.data.pages.MainPage;
import ru.yandex.geobase.regions.Turkey;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.tune.data.mordas.TouchTuneComMorda.touchTuneCom;

/**
 * User: asamar
 * Date: 06.12.16
 */
@Aqua.Test(title = "Tune main page")
@Features({"Tune", "Touch"})
@RunWith(Parameterized.class)
public class MainPageTest {

    private static TuneTestsProperties CONFIG = new TuneTestsProperties();

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
    private WebPage page;
    private TuneMorda morda;

    public MainPageTest(TuneMorda morda) {
        this.morda = morda;
        this.collectorRule = new HierarchicalErrorCollectorRule();
        this.rule = morda.getRule().around(collectorRule);
        this.driver = rule.getDriver();
    }

    @Before
    public void init() throws InterruptedException {
        this.page = morda.initialize(driver, MainPage.class);
    }

    @Test
    public void appearanceTest() {
        Validator<? extends TuneMorda> validator = new Validator<>(driver, morda);
        collectorRule.getCollector()
                .check(((Validateable<TuneMorda>)page).validate(validator));
    }
}
