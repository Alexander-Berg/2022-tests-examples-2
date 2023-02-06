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
import ru.yandex.autotests.morda.pages.desktop.tune.blocks.TunePlaces;
import ru.yandex.autotests.morda.pages.desktop.tune.pages.TuneWithPlaces;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollectorRule;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.autotests.utils.morda.users.User;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.allure.annotations.Stories;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.net.MalformedURLException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;

import static java.lang.Thread.sleep;
import static org.hamcrest.CoreMatchers.containsString;
import static ru.yandex.autotests.morda.pages.desktop.tune.TuneComTrMorda.tuneComTr;
import static ru.yandex.autotests.mordacommonsteps.utils.Mode.PLAIN;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.utils.morda.language.Language.BE;
import static ru.yandex.autotests.utils.morda.language.Language.KK;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.Language.TR;
import static ru.yandex.autotests.utils.morda.language.Language.UK;
import static ru.yandex.autotests.utils.morda.users.UserType.DEFAULT;

/**
 * User: asamar
 * Date: 29.08.16
 */
@Aqua.Test(title = "Places")
@Features("Tune")
@Stories("Places")
@RunWith(Parameterized.class)
public class TunePlacesTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> parametrize() {
        List<Morda<? extends TuneWithPlaces>> data = new ArrayList<>();

        String env = CONFIG.getMordaEnvironment();
        String scheme = CONFIG.getMordaScheme();

        TuneMainMorda.getDefaultList(scheme, env).forEach(data::add);

        data.add(tuneComTr(scheme, env, Region.ISTANBUL));

        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    @Rule
    public MordaAllureBaseRule rule;
    private HierarchicalErrorCollectorRule collectorRule;
    private Morda<? extends TuneWithPlaces> morda;
    private WebDriver driver;
    private TuneWithPlaces page;
    private CommonMordaSteps user;
    private User u;

    public TunePlacesTest(Morda<? extends TuneWithPlaces> morda) {
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
        u = rule.getUser(DEFAULT, PLAIN);

        user.logsInAs(u,
                morda.getPassportUrl().toURL(),
                morda.getUrl() + "places");
    }

    @Test
    public void placesAppearance() {
        Validator<Morda<? extends TuneWithPlaces>> validator = new Validator<>(driver, morda);
        collectorRule.getCollector()
                .check(page.getPlacesBlock().validate(validator));
    }

    @Test
    public void footerAppearance() {
        Validator<Morda<? extends TuneWithPlaces>> validator = new Validator<>(driver, morda);
        collectorRule.getCollector()
                .check(page.getFooterBlock().validate(validator));
    }

    @Test
    public void authorizedHeaderAppearance() {
        Validator<Morda<? extends TuneWithPlaces>> validator = new Validator<>(driver, morda);
        collectorRule.getCollector()
                .check(page.getHeaderBlock().validate(validator.withUser(u)));
    }

    @Test
    public void setPlaces() throws InterruptedException {

        HashMap<Language, String> homes = new HashMap<Language, String>(){{
            put(RU, "Ленинский");
            put(BE, "Ленинский");
            put(KK, "Ленинский");
            put(TR, "Leninsky");
//            put(UK, "Победы");
//            put(UK, "Ленінський");
            put(UK, "Саксаганського");
        }};

        HashMap<Language, String> works = new HashMap<Language, String>(){{
            put(RU, "Кутузовский");
            put(KK, "Кутузовский");
            put(BE, "Кутузовский");
            put(TR, "Kutuzovsky");
//            put(UK, "Московська");
            put(UK, "Жилянська");
        }};

        TunePlaces places = page.getPlacesBlock();
        String home = homes.get(morda.getLanguage());//"Ленинский";
        String work = works.get(morda.getLanguage());//"Кутузовский";

        user.entersTextInInput(places.homeInput, home);
        sleep(500);
        HtmlElement homeItem = getSuggestItem(places.suggest, home);
        user.shouldSeeElement(homeItem);
        user.clicksOn(homeItem);


        user.entersTextInInput(places.jobInput, work);
        sleep(500);
        HtmlElement jobItem = getSuggestItem(places.suggest, work);
        user.shouldSeeElement(jobItem);
        user.clicksOn(jobItem);

        user.shouldSeeElement(places.saveButton);
        user.clicksOn(places.saveButton);

        sleep(1000);

        user.refreshPage();

        user.shouldSeeInputWithText(places.homeInput, containsString(home));
        user.shouldSeeInputWithText(places.jobInput, containsString(work));

    }

    @Step("Get suggest item {1}")
    public HtmlElement getSuggestItem(List<HtmlElement> items, String city) {
        return items.stream()
                .filter(e -> e.getText().contains(city))
                .findFirst()
                .orElseThrow(() -> new AssertionError("В саджесте нет нужного города"));
    }
}
