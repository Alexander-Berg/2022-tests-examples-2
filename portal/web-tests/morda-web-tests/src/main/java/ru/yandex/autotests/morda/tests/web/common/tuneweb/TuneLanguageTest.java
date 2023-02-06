package ru.yandex.autotests.morda.tests.web.common.tuneweb;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.desktop.tune.TuneMainMorda;
import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TuneLanguage;
import ru.yandex.autotests.morda.pages.desktop.tune.pages.TuneWithLang;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollectorRule;
import ru.yandex.autotests.morda.steps.TuneSteps;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.users.User;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.net.MalformedURLException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.lang.Thread.sleep;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.PLAIN;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.utils.morda.language.Language.getLanguage;
import static ru.yandex.autotests.utils.morda.users.UserType.DEFAULT;

/**
 * User: asamar
 * Date: 10.08.16
 */
@Aqua.Test(title = "Language")
@Features("Tune")
@Stories("Language")
@RunWith(Parameterized.class)
public class TuneLanguageTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> parametrize() {
        List<Morda<? extends TuneWithLang>> data = new ArrayList<>();

        String env = CONFIG.getMordaEnvironment();
        String scheme = CONFIG.getMordaScheme();

        TuneMainMorda.getDefaultList(scheme, env).forEach(data::add);

        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    @Rule
    public MordaAllureBaseRule rule;
    private HierarchicalErrorCollectorRule collectorRule;
    private Morda<? extends TuneWithLang> morda;
    private WebDriver driver;
    private TuneWithLang page;
    private CommonMordaSteps user;

    public TuneLanguageTest(Morda<? extends TuneWithLang> tune) {
        this.morda = tune;
        this.collectorRule = new HierarchicalErrorCollectorRule();
        this.rule = tune.getRule().withRule(collectorRule);
        this.driver = rule.getDriver();
        this.page = tune.getPage(driver);
        this.user = new CommonMordaSteps(driver);
    }

    @Before
    public void init() {
        morda.initialize(driver);
//        NavigationSteps.open(driver, morda.getUrl() + "lang");
        user.opensPage(morda.getUrl() + "lang");
    }

    @Test
    public void langAppearance(){
        Validator<Morda<? extends TuneWithLang>> validator = new Validator<>(driver, morda);
        collectorRule.getCollector()
                .check(page.getLangBlock().validate(validator));
    }

    @Test
    public void footerAppearance(){
        Validator<? extends Morda<? extends TuneWithLang>> validator = new Validator<>(driver, morda);
        collectorRule.getCollector()
                .check(page.getFooterBlock().validate(validator));
    }

    @Test
    public void headerAppearance(){
        Validator<? extends Morda<? extends TuneWithLang>> validator = new Validator<>(driver, morda);
        collectorRule.getCollector()
                .check(page.getHeaderBlock().validate(validator));
    }

    @Test
    public void autorizedHeaderAppearance() throws MalformedURLException {
        User u = rule.getUser(DEFAULT, PLAIN);

        user.logsInAs(u,
                morda.getPassportUrl().toURL(),
                morda.getUrl() + "lang");

        Validator<? extends Morda<? extends TuneWithLang>> validator = new Validator<>(driver, morda);
        collectorRule.getCollector()
                .check(page.getHeaderBlock().validate(validator.withUser(u)));
    }

    @Test
    public void setRandomLang() throws InterruptedException {
        TuneLanguage lang = page.getLangBlock();

        user.shouldSeeElement(lang.langDropDown);
        String newLangValue = user.selectRandom(lang.langSelect);
        user.clicksOn(lang.saveButton);
        sleep(500);
        TuneSteps.shouldSeeLangInCookieMy(driver, morda.getCookieDomain(), getLanguage(newLangValue));

    }
}
