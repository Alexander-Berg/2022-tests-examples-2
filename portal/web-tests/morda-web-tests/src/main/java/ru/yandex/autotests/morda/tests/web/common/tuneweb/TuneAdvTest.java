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
import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TuneAdv;
import ru.yandex.autotests.morda.pages.desktop.tune.pages.TuneWithAdv;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollectorRule;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.morda.utils.cookie.WebDriverCookieUtils;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.users.User;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.cookies.my.CookieMy;

import java.net.MalformedURLException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.lang.Thread.sleep;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.CoreMatchers.notNullValue;
import static org.hamcrest.MatcherAssert.assertThat;
import static ru.yandex.autotests.morda.utils.cookie.CookieUtilsFactory.cookieUtils;
import static ru.yandex.autotests.morda.utils.cookie.MordaCookieUtils.MY;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.PLAIN;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.utils.morda.users.UserType.DEFAULT;

/**
 * User: asamar
 * Date: 11.08.16
 */
@Aqua.Test(title = "Adv")
@Features("Tune")
@Stories("Adv")
@RunWith(Parameterized.class)
public class TuneAdvTest {

    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> parametrize() {
        List<Morda<? extends TuneWithAdv>> data = new ArrayList<>();

        String env = CONFIG.getMordaEnvironment();
        String scheme = CONFIG.getMordaScheme();

        TuneMainMorda.getDefaultList(scheme, env).forEach(data::add);

        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    @Rule
    public MordaAllureBaseRule rule;
    private HierarchicalErrorCollectorRule collectorRule;
    private Morda<? extends TuneWithAdv> morda;
    private WebDriver driver;
    private TuneWithAdv page;
    private CommonMordaSteps user;

    public TuneAdvTest(Morda<? extends TuneWithAdv> tune) {
        this.morda = tune;
        this.collectorRule = new HierarchicalErrorCollectorRule();
        this.rule = morda.getRule().withRule(collectorRule);
        this.driver = rule.getDriver();
        this.page = tune.getPage(driver);
        this.user = new CommonMordaSteps(driver);
    }

    @Before
    public void init() {
        morda.initialize(driver);
//        NavigationSteps.open(driver, morda.getUrl() + "adv");
        user.opensPage(morda.getUrl() + "adv");
    }

    @Test
    public void headerAppearance(){
        Validator<? extends Morda<? extends TuneWithAdv>> validator = new Validator<>(driver, morda);
        collectorRule.getCollector()
                .check(page.getHeaderBlock().validate(validator));
    }

    @Test
    public void autorizedHeaderAppearance() throws MalformedURLException {
        User u = rule.getUser(DEFAULT, PLAIN);

        user.logsInAs(u,
                morda.getPassportUrl().toURL(),
                morda.getUrl() + "adv");

        Validator<? extends Morda<? extends TuneWithAdv>> validator = new Validator<>(driver, morda);
        collectorRule.getCollector()
                .check(page.getHeaderBlock().validate(validator.withUser(u)));
    }

    @Test
    public void footerAppearance(){
        Validator<? extends Morda<? extends TuneWithAdv>> validator = new Validator<>(driver, morda);
        collectorRule.getCollector()
                .check(page.getFooterBlock().validate(validator));
    }

    @Test
    public void advAppearance(){
        Validator<Morda<? extends TuneWithAdv>> validator = new Validator<>(driver, morda);
        collectorRule.getCollector()
                .check(page.getAdvBlock().validate(validator));
    }

    @Test
    public void advSettings() throws InterruptedException {
        TuneAdv adv = page.getAdvBlock();
        user.shouldSeeElement(adv.advCheckBox);
        user.shouldSeeElementIsSelected(adv.advCheckBox);
        user.deselectElement(adv.advCheckBox);
        user.shouldSeeElementIsNotSelected(adv.advCheckBox);
        user.clicksOn(adv.saveButton);
//        user.shouldSeeElement(adv.advCheckBox);
//        user.shouldSeeElementIsNotSelected(adv.advCheckBox);
        Thread.sleep(300);
        shouldNotSeeAdvertising(driver);
    }

    @Test
    public void interestsSettings() throws InterruptedException {
        TuneAdv adv = page.getAdvBlock();
        user.shouldSeeElement(adv.interestCheckBox);
        user.shouldSeeElementIsSelected(adv.interestCheckBox);
        user.deselectElement(adv.interestCheckBox);
        user.shouldSeeElementIsNotSelected(adv.interestCheckBox);
        user.clicksOn(adv.saveButton);
//        user.shouldSeeElement(adv.interestCheckBox);
//        user.shouldSeeElementIsNotSelected(adv.interestCheckBox);
        Thread.sleep(300);
        shouldNotNoteInterests(driver);
    }

    @Test
    public void locationSettings() throws InterruptedException {
        TuneAdv adv = page.getAdvBlock();
        user.shouldSeeElement(adv.geoCheckBox);
        user.shouldSeeElementIsSelected(adv.geoCheckBox);
        user.deselectElement(adv.geoCheckBox);
        user.shouldSeeElementIsNotSelected(adv.geoCheckBox);
        user.clicksOn(adv.saveButton);
//        user.shouldSeeElement(adv.geoCheckBox);
//        user.shouldSeeElementIsNotSelected(adv.geoCheckBox);
        Thread.sleep(300);
        shouldNotNoteLocation(driver);
    }

    @Test
    public void mainPageHint(){
        Validator<? extends Morda<? extends TuneWithAdv>> validator =
                new Validator<Morda<? extends TuneWithAdv>>(driver, morda);


        TuneAdv adv = page.getAdvBlock();
        user.shouldSeeElement(adv.mainPageHintButton);
        user.clicksOn(adv.mainPageHintButton);
        user.shouldSeeElement(adv.mainPageHint);

        collectorRule.getCollector()
                .check(adv.validateMainPageHint(validator));
    }

    @Test
    public void directHint(){
        Validator<? extends Morda<? extends TuneWithAdv>> validator =
                new Validator<Morda<? extends TuneWithAdv>>(driver, morda);

        TuneAdv adv = page.getAdvBlock();
        user.shouldSeeElement(adv.directHintButton);
        user.clicksOn(adv.directHintButton);
        user.shouldSeeElement(adv.directHint);

        collectorRule.getCollector()
                .check(adv.validateDirectHint(validator));
    }

//    @Test
    public void uncheckWithoutSave() throws InterruptedException {
        TuneAdv adv = page.getAdvBlock();
        user.shouldSeeElement(adv.advCheckBox);
        user.shouldSeeElementIsSelected(adv.advCheckBox);
        user.deselectElement(adv.advCheckBox);
        sleep(5000);
        user.refreshPage();
        sleep(5000);
        user.shouldSeeElement(adv.advCheckBox);
        user.shouldSeeElementIsSelected(adv.advCheckBox);
    }


    @Step("Should see location settings in MY cookie")
    public void shouldNotNoteLocation(WebDriver driver){
        WebDriverCookieUtils utils = cookieUtils(driver);
        String cookieMyValue = utils.getCookieValue(utils.getCookieNamed(MY, morda.getCookieDomain()));
        CookieMy my = new CookieMy(cookieMyValue);
        assertThat("В куку my не выставился нужный блок(58)", my.getBlock(58), notNullValue());
        assertThat("Неверне значение куки my(реклама не показывается)", my.getBlock(58).get(0), equalTo(1));
    }

    @Step("Should see interests settings in MY cookie")
    public void shouldNotNoteInterests(WebDriver driver){
        WebDriverCookieUtils utils = cookieUtils(driver);
        String cookieMyValue = utils.getCookieValue(utils.getCookieNamed(MY, morda.getCookieDomain()));
        CookieMy my = new CookieMy(cookieMyValue);
        assertThat("В куку my не выставился нужный блок(38)", my.getBlock(38), notNullValue());
        assertThat("Неверне значение куки my(реклама не показывается)", my.getBlock(38).get(0), equalTo(1));
    }

    @Step("Should see adv settings in MY cookie")
    public void shouldNotSeeAdvertising(WebDriver driver) {
        WebDriverCookieUtils utils = cookieUtils(driver);
        String cookieMyValue = utils.getCookieValue(utils.getCookieNamed(MY, morda.getCookieDomain()));
        CookieMy my = new CookieMy(cookieMyValue);
        assertThat("В куку my не выставился нужный блок(46)", my.getBlock(46), notNullValue());
        assertThat("Неверне значение куки my(реклама показывается)", my.getBlock(46).get(0), equalTo(1));
    }
}
