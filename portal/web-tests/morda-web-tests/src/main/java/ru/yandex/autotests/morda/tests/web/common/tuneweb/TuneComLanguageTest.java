package ru.yandex.autotests.morda.tests.web.common.tuneweb;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.desktop.tune.TuneComMorda;
import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TuneLanguage;
import ru.yandex.autotests.morda.pages.desktop.tune.pages.TuneComPage;
import ru.yandex.autotests.morda.steps.TuneSteps;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.net.URI;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.lang.Thread.sleep;
import static java.util.Arrays.asList;
import static javax.ws.rs.core.UriBuilder.fromUri;
import static ru.yandex.autotests.morda.pages.desktop.tune.TuneComMorda.tuneCom;
import static ru.yandex.autotests.utils.morda.language.Language.EN;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.Language.getLanguage;

/**
 * User: asamar
 * Date: 28.12.16
 */
@Aqua.Test(title = "Language on COM")
@Features("Tune")
@Stories("Language")
@RunWith(Parameterized.class)
public class TuneComLanguageTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}, {1}")
    public static Collection<Object[]> parametrize() {
        List<Object[]> data = new ArrayList<>();

        String env = CONFIG.getMordaEnvironment();
        String scheme = CONFIG.getMordaScheme();

        for (Language lang: asList (RU, EN)) {
            data.add(new Object[]{tuneCom(scheme, env), lang});
        }

        return data;
    }

    @Rule
    public MordaAllureBaseRule rule;
    private TuneComMorda morda;
    private WebDriver driver;
    private TuneComPage page;
    private CommonMordaSteps user;
    private Language lang;

    public TuneComLanguageTest(TuneComMorda tune, Language lang) {
        this.morda = tune;
        this.lang = lang;
        this.rule = tune.getRule();
        this.driver = rule.getDriver();
        this.page = tune.getPage(driver);
        this.user = new CommonMordaSteps(driver);
    }

    @Before
    public void init() {
        URI uri = fromUri(morda.getUrl()).path("lang").build();
        user.opensPage(uri.toString());
    }

    @Test
    public void setLang() throws InterruptedException {
        TuneLanguage langPage = page.getLanguageBlock();
        user.shouldSeeElement(langPage.langDropDown);
        langPage.selectLangByValue(lang.getValue());
        user.clicksOn(langPage.saveButton);
        sleep(500);
        TuneSteps.shouldSeeLangInCookieMy(driver, morda.getCookieDomain(), getLanguage(lang.getValue()));

    }
}
