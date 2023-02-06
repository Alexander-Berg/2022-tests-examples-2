package ru.yandex.autotests.morda.tests.web.common.tuneweb;

import org.junit.Assume;
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
import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TuneSearch;
import ru.yandex.autotests.morda.pages.desktop.tune.pages.TuneWithSearch;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollectorRule;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.morda.utils.cookie.WebDriverCookieUtils;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.users.User;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.allure.annotations.Stories;

import java.net.MalformedURLException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static org.hamcrest.CoreMatchers.containsString;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.not;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.morda.pages.MordaType.TUNE_COM;
import static ru.yandex.autotests.morda.pages.desktop.tune.TuneComMorda.tuneCom;
import static ru.yandex.autotests.morda.pages.desktop.tune.TuneComTrMorda.tuneComTr;
import static ru.yandex.autotests.morda.utils.cookie.CookieUtilsFactory.cookieUtils;
import static ru.yandex.autotests.morda.utils.cookie.MordaCookieUtils.YP;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.PLAIN;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.utils.morda.users.UserType.DEFAULT;

/**
 * User: asamar
 * Date: 11.08.16
 */
@Aqua.Test(title = "Search")
@Features("Tune")
@Stories("Search")
@RunWith(Parameterized.class)
public class TuneSearchTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> parametrize() {
        List<Morda<? extends TuneWithSearch>> data = new ArrayList<>();

        String env = CONFIG.getMordaEnvironment();
        String scheme = CONFIG.getMordaScheme();

        TuneMainMorda.getDefaultList(scheme, env).forEach(data::add);

        data.add(tuneComTr(scheme, env, Region.ISTANBUL));
        data.add(tuneCom(scheme, env));

        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    @Rule
    public MordaAllureBaseRule rule;
    private HierarchicalErrorCollectorRule collectorRule;
    private Morda<? extends TuneWithSearch> morda;
    private WebDriver driver;
    private TuneWithSearch page;
    private CommonMordaSteps user;

    public TuneSearchTest(Morda<? extends TuneWithSearch> morda) {
        this.morda = morda;
        this.collectorRule = new HierarchicalErrorCollectorRule();
        this.rule = morda.getRule().withRule(collectorRule);
        this.driver = rule.getDriver();
        this.page = morda.getPage(driver);
        this.user = new CommonMordaSteps(driver);
    }

    @Before
    public void init() throws MalformedURLException {
        morda.initialize(driver);
//        NavigationSteps.open(driver, morda.getUrl() + "search");
        user.opensPage(morda.getUrl() + "search");
    }

    @Test
    public void searchAppearance() {
        Validator<Morda<? extends TuneWithSearch>> validator = new Validator<>(driver, morda);
        collectorRule.getCollector()
                .check(page.getSearchBlock().validate(validator));
    }

    @Test
    public void footerAppearance() {
        Validator<Morda<? extends TuneWithSearch>> validator = new Validator<>(driver, morda);
        collectorRule.getCollector()
                .check(page.getFooterBlock().validate(validator));
    }

    @Test
    public void headerAppearance() {
        Validator<Morda<? extends TuneWithSearch>> validator = new Validator<>(driver, morda);
        collectorRule.getCollector()
                .check(page.getHeaderBlock().validate(validator));
    }

    @Test
    public void autorizedHeaderAppearance() throws MalformedURLException {
        User u = rule.getUser(DEFAULT, PLAIN);

        user.logsInAs(u,
                morda.getPassportUrl().toURL(),
                morda.getUrl() + "search");

        Validator<? extends Morda<? extends TuneWithSearch>> validator = new Validator<>(driver, morda);
        collectorRule.getCollector()
                .check(page.getHeaderBlock().validate(validator.withUser(u)));
    }


    @Test
    public void favouriteSites() throws InterruptedException {
        TuneSearch search = page.getSearchBlock();

        user.shouldSeeElement(search.sitesCheckBox);
        user.shouldSeeElementIsSelected(search.sitesCheckBox);
        user.deselectElement(search.sitesCheckBox);
        user.shouldSeeElementIsNotSelected(search.sitesCheckBox);
        user.clicksOn(search.saveButton);
        Thread.sleep(1000);
        user.shouldSeeElement(search.sitesCheckBox);
        user.shouldSeeElementIsNotSelected(search.sitesCheckBox);
        shouldNotSeeFavouriteSites(driver);

    }

    @Test
    public void favouriteRequests() throws InterruptedException, MalformedURLException {
        Assume.assumeThat("На .COM нет настройки частых запросов", morda.getMordaType(), not(equalTo(TUNE_COM)));

        user.logsInAs(rule.getUser(DEFAULT, PLAIN),
                morda.getPassportUrl().toURL(),
                morda.getUrl() + "search");

        TuneSearch search = page.getSearchBlock();

        user.shouldSeeElement(search.requestsCheckBox);
//        user.shouldSeeElementIsSelected(search.requestsCheckBox);
        user.deselectElement(search.requestsCheckBox);
        user.shouldSeeElementIsNotSelected(search.requestsCheckBox);
        user.clicksOn(search.saveButton);
        Thread.sleep(1000);
        user.shouldSeeElement(search.requestsCheckBox);
        user.shouldSeeElementIsNotSelected(search.requestsCheckBox);
        user.selectElement(search.requestsCheckBox);
        user.shouldSeeElementIsSelected(search.requestsCheckBox);
        user.clicksOn(search.saveButton);
    }

    @Step("Should see favourite sites settings in YP cookie")
    public void shouldNotSeeFavouriteSites(WebDriver driver) {
        WebDriverCookieUtils utils = cookieUtils(driver);
        String cookieYpValue = utils.getCookieValue(utils.getCookieNamed(YP, morda.getCookieDomain()));
        assertThat("Неверне значение куки yp(настройка любимых сайтов /search)", cookieYpValue, containsString("pns.0"));
    }
}
