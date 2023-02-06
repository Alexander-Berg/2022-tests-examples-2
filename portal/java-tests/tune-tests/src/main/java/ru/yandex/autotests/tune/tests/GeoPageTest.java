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
import ru.yandex.autotests.morda.beans.cleanvars.geo.GeoLocation;
import ru.yandex.autotests.morda.data.validation.Validator;
import ru.yandex.autotests.morda.rules.base.MordaBaseWebDriverRule;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollectorRule;
import ru.yandex.autotests.tune.TuneTestsProperties;
import ru.yandex.autotests.tune.data.element.InputSuggest;
import ru.yandex.autotests.tune.data.mordas.TuneMorda;
import ru.yandex.autotests.tune.data.pages.GeoPage;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.geobase.regions.Turkey;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static io.qameta.htmlelements.matcher.DisplayedMatcher.displayed;
import static io.qameta.htmlelements.matcher.HasTextMatcher.hasText;
import static java.lang.Thread.sleep;
import static org.hamcrest.CoreMatchers.not;
import static org.hamcrest.text.IsEmptyString.isEmptyOrNullString;
import static ru.yandex.autotests.morda.pages.MordaLanguage.BE;
import static ru.yandex.autotests.morda.pages.MordaLanguage.KK;
import static ru.yandex.autotests.morda.pages.MordaLanguage.RU;
import static ru.yandex.autotests.morda.pages.MordaLanguage.UK;
import static ru.yandex.autotests.morda.steps.TuneSteps.shouldSeeRegion;
import static ru.yandex.autotests.morda.steps.TuneSteps.ypShouldContains;
import static ru.yandex.autotests.tune.data.mordas.TouchTuneComTrMorda.touchTuneComTr;
import static ru.yandex.autotests.tune.data.mordas.TouchTuneMainMorda.touchTuneMain;
import static ru.yandex.geobase.regions.Belarus.MINSK;
import static ru.yandex.geobase.regions.Kazakhstan.ASTANA;
import static ru.yandex.geobase.regions.Russia.MOSCOW;
import static ru.yandex.geobase.regions.Ukraine.KYIV;

/**
 * User: asamar
 * Date: 14.12.16
 */
@Aqua.Test(title = "Tune geo page")
@Features({"Tune", "Touch"})
@RunWith(Parameterized.class)
public class GeoPageTest {
    private static TuneTestsProperties CONFIG = new TuneTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Object[]> mordas = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();
        String useragentTouch = CONFIG.getMordaUserAgentTouchIphone();

        GeoLocation minsk = new GeoLocation().withLat(53.89156869807424).withLon(27.547818463671277);
        GeoLocation moscow = new GeoLocation().withLat(55.74783793380062).withLon(37.565237400882175);
        GeoLocation kiev = new GeoLocation().withLat(50.450097).withLon(30.523397);
        GeoLocation astana = new GeoLocation().withLat(51.14168269361951).withLon(71.4334735332312);
        GeoLocation istanbul = new GeoLocation().withLat(41.05073036834944).withLon(28.9698424397361);

        mordas.add(new Object[]{touchTuneMain(scheme, environment, useragentTouch).region(MOSCOW).language(RU), moscow});
        mordas.add(new Object[]{touchTuneMain(scheme, environment, useragentTouch).region(MINSK).language(BE), minsk});
        mordas.add(new Object[]{touchTuneMain(scheme, environment, useragentTouch).region(KYIV).language(UK), kiev});
        mordas.add(new Object[]{touchTuneMain(scheme, environment, useragentTouch).region(ASTANA).language(KK), astana});

        mordas.add(new Object[]{touchTuneComTr(scheme, environment, useragentTouch, Turkey.ISTANBUL_11508), istanbul});

//        mordas.add(touchTuneCom(scheme, environment, useragentTouch, MordaLanguage.EN));

        return mordas;
    }

    @Rule
    public MordaBaseWebDriverRule rule;
    public HierarchicalErrorCollectorRule collectorRule;
    private WebDriver driver;
    private GeoPage page;
    private TuneMorda morda;
    private GeoLocation geoLocation;

    public GeoPageTest(TuneMorda morda, GeoLocation geoLocation) {
        this.morda = morda;
        this.geoLocation = geoLocation;
        this.collectorRule = new HierarchicalErrorCollectorRule();
        this.rule = morda.getRule().around(collectorRule);
        this.driver = rule.getDriver();
    }

    @Before
    public void init() throws InterruptedException, JsonProcessingException {
        WebPage webPage = morda.initialize(driver, GeoPage.class);
        this.page = (GeoPage) webPage;
    }

    @Test
    public void appearanceTest() {
        Validator<TuneMorda> validator = new Validator<>(driver, morda);
        collectorRule.getCollector()
                .check(page.validate(validator));
    }

    @Test
    public void foundMeButtonTest() throws InterruptedException {
        page.setGeoLocation(geoLocation);
        page.findMeClick();
        sleep(500);

        ypShouldContains(driver, morda.getCookieDomain(), "gpauto");
    }

    @Test
    public void autoCheckBox() {
        page.automaticaly().unCheck();
        page.cityInput().should(hasText(isEmptyOrNullString()));
        page.saveButton().should(displayed());
        page.automaticaly().check();
        page.cityInput().should(hasText(not(isEmptyOrNullString())));
    }

    @Test
    public void setRegionByInput() throws InterruptedException {
        GeobaseRegion region = morda.getRegion();
        String reg = region.getTranslations(morda.getLanguage().getValue()).getNominativeCase();

        page.cityInput().entersTextInInput(reg);
        InputSuggest.Item item = page.getSuggestItem(reg);
        item.should(displayed()).click();
        sleep(500);
        shouldSeeRegion(driver, morda.getCookieDomain(), region);
    }
}
