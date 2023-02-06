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
import ru.yandex.autotests.tune.TuneTestsProperties;
import ru.yandex.autotests.tune.data.mordas.TouchTuneMainMorda;
import ru.yandex.autotests.tune.data.mordas.TuneMorda;
import ru.yandex.autotests.tune.data.pages.LangPage;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.morda.steps.TuneSteps.shouldSeeLangInCookieMy;

/**
 * User: asamar
 * Date: 24.11.16
 */
@Aqua.Test(title = "Tune lang page")
@Features({"Tune", "Touch"})
@RunWith(Parameterized.class)
public class LanguageTest {
    private static TuneTestsProperties CONFIG = new TuneTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<? super TuneMorda> data() {
        List<? super TuneMorda> mordas = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();
        String useragentTouch = CONFIG.getMordaUserAgentTouchIphone();

        mordas.addAll(TouchTuneMainMorda.getDefaultList(scheme, environment, useragentTouch));

        return mordas;
    }

    @Rule
    public MordaBaseWebDriverRule rule;
    public HierarchicalErrorCollectorRule collectorRule;
    private WebDriver driver;
    private LangPage page;
    private TuneMorda morda;

    public LanguageTest(TuneMorda morda) {
        this.morda = morda;
        this.collectorRule = new HierarchicalErrorCollectorRule();
        this.rule = morda.getRule().around(collectorRule);
        this.driver = rule.getDriver();
    }

    @Before
    public void init() throws InterruptedException, JsonProcessingException {
        WebPage webPage = morda.initialize(driver, LangPage.class);
        this.page = (LangPage) webPage;
    }

    @Test
    public void testLang() throws InterruptedException {
        String langValue = page.selectNextLang(morda.getLanguage());
        page.refresh();
        shouldSeeLangInCookieMy(driver, morda.getCookieDomain(), MordaLanguage.fromValue(langValue));
    }

    @Test
    public void appearanceTest() {
        Validator<TuneMorda> validator = new Validator<>(driver, morda);
        collectorRule.getCollector()
                .check(page.validate(validator));
    }
}
