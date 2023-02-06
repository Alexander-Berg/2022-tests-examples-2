package ru.yandex.autotests.morda.tests.web.common.tuneweb;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TuneGeo;
import ru.yandex.autotests.morda.pages.desktop.tune.pages.TuneWithGeo;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollectorRule;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.morda.tests.web.utils.GeoLocation;
import ru.yandex.autotests.morda.utils.cookie.WebDriverCookieUtils;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.users.User;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.allure.annotations.Stories;

import java.net.MalformedURLException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.lang.Thread.sleep;
import static org.hamcrest.CoreMatchers.containsString;
import static org.hamcrest.CoreMatchers.not;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.text.IsEmptyString.isEmptyOrNullString;
import static org.openqa.selenium.remote.DesiredCapabilities.firefox;
import static ru.yandex.autotests.morda.pages.desktop.tune.TuneComTrMorda.tuneComTr;
import static ru.yandex.autotests.morda.pages.desktop.tune.TuneMainMorda.tune;
import static ru.yandex.autotests.morda.steps.TuneSteps.shouldSeeRegion;
import static ru.yandex.autotests.morda.utils.cookie.CookieUtilsFactory.cookieUtils;
import static ru.yandex.autotests.morda.utils.cookie.MordaCookieUtils.YP;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.PLAIN;
import static ru.yandex.autotests.utils.morda.region.Region.ASTANA;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.MINSK;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;
import static ru.yandex.autotests.utils.morda.users.UserType.DEFAULT;

/**
 * User: asamar
 * Date: 10.08.16
 */
@Aqua.Test(title = "Geo")
@Features("Tune")
@Stories("Geo")
@RunWith(Parameterized.class)
public class TuneGeoTest {

    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> parametrize() {
        List<Object[]> data = new ArrayList<>();

        String env = CONFIG.getMordaEnvironment();
        String scheme = CONFIG.getMordaScheme();

        data.add(new Object[]{tune(scheme, env, MOSCOW, Language.RU), GeoLocation.MSK_CENTER});
        data.add(new Object[]{tune(scheme, env, KIEV, Language.UK), GeoLocation.KIEV});
        data.add(new Object[]{tune(scheme, env, ASTANA, Language.KK), GeoLocation.ASTANA});
        data.add(new Object[]{tune(scheme, env, MINSK, Language.BE), GeoLocation.MINSK});
        data.add(new Object[]{tuneComTr(scheme, env, Region.ISTANBUL), GeoLocation.ISTANBUL});

        return data;//convert(MordaType.filter(data, CONFIG.getMordaPagesToTest())).subList(0, 1);
    }

    @Rule
    public MordaAllureBaseRule rule;
    public HierarchicalErrorCollectorRule collectorRule;
    private Morda<? extends TuneWithGeo> morda;
    private WebDriver driver;
    private TuneWithGeo page;
    private CommonMordaSteps user;
    private GeoLocation geoLocation;


    public TuneGeoTest(Morda<? extends TuneWithGeo> tune, GeoLocation geoLocation) {
        this.geoLocation = geoLocation;
        DesiredCapabilities caps = firefox();
        caps.setCapability("locationContextEnabled", true);

        this.morda = tune;
        this.collectorRule = new HierarchicalErrorCollectorRule();
        this.rule = tune.getRule(caps)
                .withRule(collectorRule);
        this.driver = rule.getDriver();
        this.page = tune.getPage(driver);
        this.user = new CommonMordaSteps(driver);
    }

    @Before
    public void init() {
        morda.initialize(driver);
//        NavigationSteps.open(driver, morda.getUrl() + "geo");
        user.opensPage(morda.getUrl() + "geo");
    }

    @Test
    public void geoAppearance() {
        Validator<Morda<? extends TuneWithGeo>> validator = new Validator<>(driver, morda);
        collectorRule.getCollector()
                .check(page.getGeoBlock().validate(validator));
    }

    @Test
    public void headerAppearance() {
        Validator<? extends Morda<? extends TuneWithGeo>> validator = new Validator<>(driver, morda);
        collectorRule.getCollector()
                .check(page.getHeaderBlock().validate(validator));
    }

    @Test
    public void autorizedHeaderAppearance() throws MalformedURLException {
        User u = rule.getUser(DEFAULT, PLAIN);

        user.logsInAs(u,
                morda.getPassportUrl().toURL(),
                morda.getUrl() + "geo");

        Validator<? extends Morda<? extends TuneWithGeo>> validator = new Validator<>(driver, morda);
        collectorRule.getCollector()
                .check(page.getHeaderBlock().validate(validator.withUser(u)));
    }

    @Test
    public void footerAppearance() {
        Validator<? extends Morda<? extends TuneWithGeo>> validator = new Validator<>(driver, morda);
        collectorRule.getCollector()
                .check(page.getFooterBlock().validate(validator));
    }

    @Test
    public void setRegionByInput() throws InterruptedException {
        TuneGeo geo = page.getGeoBlock();
        Region region = morda.getRegion();

        String regName = region.getName();
        if (region.getRegionIdInt() == 143) {
            regName = "Київ";
        }

        user.entersTextInInput(geo.cityInput, regName);
        user.shouldSeeElement(geo.suggest);
        TuneGeo.GeoSuggest.SuggestItems item = getSuggestItem(geo, regName);
        user.shouldSeeElement(item);
        user.clicksOn(item);
        user.shouldSeeElementIsNotSelected(geo.autoCheckBox);
        user.clicksOn(geo.saveButton);
        sleep(500);
        shouldSeeRegion(driver, morda.getCookieDomain(), region);
    }

    @Test
    public void autoCheckBox() {
        TuneGeo geo = page.getGeoBlock();

        user.shouldSeeElement(geo.autoCheckBox);
        user.deselectElement(geo.autoCheckBox);

        user.shouldSeeInputWithText(geo.cityInput, isEmptyOrNullString());

        user.selectElement(geo.autoCheckBox);
        user.shouldSeeInputWithText(geo.cityInput, not(isEmptyOrNullString()));

    }

    @Test
    public void foundMe() throws InterruptedException {
        TuneGeo geo = page.getGeoBlock();

        setGeoLocation(geoLocation);

        user.shouldSeeElement(geo.locateButton);
        user.clicksOn(geo.locateButton);

        user.shouldSeeElement(geo.saveButton);
        user.clicksOn(geo.saveButton);

        sleep(500);

        shouldSeelocation();

    }

    @Step("Should see \"gpauto\" block in YP")
    public void shouldSeelocation() {
        WebDriverCookieUtils utils = cookieUtils(driver);
        String ypValue = utils.getCookieValue(utils.getCookieNamed(YP, morda.getCookieDomain()));
        assertThat("В yp не выставился gpauto", ypValue, containsString("gpauto"));
    }

    @Step("Get suggest item {1}")
    public TuneGeo.GeoSuggest.SuggestItems getSuggestItem(TuneGeo geo, String city) {
        return geo.suggest.items.stream()
                .filter(e -> e.city.getText().startsWith(city))
                .findFirst()
                .orElseThrow(() -> new AssertionError("В саджесте нет нужного города"));
    }

    @Step("Set {0} coordinates")
    public void setGeoLocation(GeoLocation geoLocation){
        ((JavascriptExecutor) driver)
                .executeScript("x = { coords: { latitude: " +
                        geoLocation.getCoordinates().getLat() +
                        ", longitude: " +
                        geoLocation.getCoordinates().getLon() +
                        ", accuracy: 1444 }}; " +
                        "window.navigator.geolocation.getCurrentPosition = function(success){success(x)}");
        ((JavascriptExecutor) driver)
                .executeScript("window.navigator.geolocation.getCurrentPosition(function(ok){console.log(ok)})");
    }

}
