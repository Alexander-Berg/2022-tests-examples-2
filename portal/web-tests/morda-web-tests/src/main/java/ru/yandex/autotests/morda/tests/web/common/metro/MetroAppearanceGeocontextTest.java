package ru.yandex.autotests.morda.tests.web.common.metro;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithMetroBlock;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollectorRule;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.morda.tests.web.utils.GeoLocation;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.geohelper.GeohelperResponse;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.util.ArrayList;
import java.util.Collection;
import java.util.EnumSet;
import java.util.List;

import static ru.yandex.autotests.morda.tests.web.utils.GeoLocation.KIEV;
import static ru.yandex.autotests.morda.tests.web.utils.GeoLocation.MSK_BELORUSSKIY;
import static ru.yandex.autotests.morda.tests.web.utils.GeoLocation.NOVOSIBIRSK;
import static ru.yandex.autotests.morda.tests.web.utils.GeoLocation.SPB_FONTANKA;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 28/02/15
 */
@Aqua.Test(title = "Geocontext Metro Block Appearance")
@Features("Metro")
@Stories("Geocontext Metro Block Appearance")
@RunWith(Parameterized.class)
public class MetroAppearanceGeocontextTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}: {1}")
    public static Collection<Object[]> data() {
        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();
        String useragentTouch = CONFIG.getMordaUserAgentTouchIphone();

        List<Object[]> data = new ArrayList<>();

        for (GeoLocation location : EnumSet.of(MSK_BELORUSSKIY, SPB_FONTANKA, KIEV, NOVOSIBIRSK)) {
            data.add(new Object[]{
                    TouchRuMorda.touchRu(scheme, environment, useragentTouch, location.getRegion(),
                            location.getCoordinates().getLat(), location.getCoordinates().getLon(), Language.RU),
                    location});
        }
        return MordaType.filter(data, CONFIG.getMordaPagesToTest());
    }

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private HierarchicalErrorCollectorRule collectorRule;
    private WebDriver driver;
    private CommonMordaSteps user;
    private Morda<? extends PageWithMetroBlock<? extends Validateable>> morda;
    private PageWithMetroBlock<? extends Validateable> page;
    private String requestId;
    private Cleanvars cleanvars;
    private GeohelperResponse geohelperResponse;
    private GeoLocation geoLocation;

    public MetroAppearanceGeocontextTest(Morda<? extends PageWithMetroBlock<? extends Validateable>> morda, GeoLocation geoLocation) {
        this.morda = morda;
        this.collectorRule = new HierarchicalErrorCollectorRule();
        this.mordaAllureBaseRule = this.morda.getRule().withRule(collectorRule);
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.page = morda.getPage(driver);
        this.geoLocation = geoLocation;
    }

    @Before
    public void initialize() {
        morda.initialize(driver);
        requestId = (String) ((JavascriptExecutor) driver)
                .executeScript("return document.getElementById('requestId').innerHTML");
        System.out.println(requestId);
    }

    @Test
    public void metroAppearance() {
        Client client = MordaClient.getJsonEnabledClient();
        T dump = client.target("http://morda-mocks.wdevx.yandex.ru/api/v1/dumps/" + requestId)
                .request()
                .buildGet().invoke().readEntity(T.class);

        this.cleanvars = dump.data._full;
        this.geohelperResponse = new MordaClient(morda.getUrl()).geohelperActions(client)
                .getGeohelperResponse(
                        geoLocation.getCoordinates().getLat(),
                        geoLocation.getCoordinates().getLon(),
                        geoLocation.getGeoId(),
                        cleanvars.getPoiGroups().getList()
                );

        Validator validator = new Validator(driver, morda).withCleanvars(cleanvars).withGeohelperResponse(geohelperResponse);
        collectorRule.getCollector()
                .check(page.getMetroBlock().validate(validator));
    }


    private static class T {
        public E data;
    }

    private static class E {
        public Cleanvars _full;
    }
}
