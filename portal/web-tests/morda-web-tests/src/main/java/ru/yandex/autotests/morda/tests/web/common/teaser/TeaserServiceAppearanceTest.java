package ru.yandex.autotests.morda.tests.web.common.teaser;

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
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithTeaserServiceBlock;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollectorRule;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda.touchRu;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.utils.morda.language.Language.BE;
import static ru.yandex.autotests.utils.morda.language.Language.KK;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.Language.UK;
import static ru.yandex.autotests.utils.morda.region.Region.ASTANA;
import static ru.yandex.autotests.utils.morda.region.Region.HARKOV;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.MINSK;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 28/02/15
 */
@Aqua.Test(title = "Teaser Service Block Appearance")
@Features("Teaser")
@Stories("Teaser Service Block Appearance")
@RunWith(Parameterized.class)
public class TeaserServiceAppearanceTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda<? extends PageWithTeaserServiceBlock<? extends Validateable>>> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();
        String useragentTouch = CONFIG.getMordaUserAgentTouchIphone();

        data.addAll(asList(
                touchRu(scheme, environment, useragentTouch, MOSCOW, RU),
                touchRu(scheme, environment, useragentTouch, KIEV, UK),
                touchRu(scheme, environment, useragentTouch, HARKOV, RU),
                touchRu(scheme, environment, useragentTouch, MINSK, BE),
                touchRu(scheme, environment, useragentTouch, ASTANA, KK)
        ));

        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private HierarchicalErrorCollectorRule collectorRule;
    private WebDriver driver;
    private CommonMordaSteps user;
    private Morda<? extends PageWithTeaserServiceBlock<? extends Validateable>> morda;
    private PageWithTeaserServiceBlock<? extends Validateable> page;
    private String requestId;
    private Cleanvars cleanvars;

    public TeaserServiceAppearanceTest(Morda<? extends PageWithTeaserServiceBlock<? extends Validateable>> morda) {
        this.morda = morda;
        this.collectorRule = new HierarchicalErrorCollectorRule();
        this.mordaAllureBaseRule = this.morda.getRule().withRule(collectorRule);
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.page = morda.getPage(driver);
    }

    @Before
    public void initialize() {
        morda.initialize(driver);
        requestId = (String) ((JavascriptExecutor) driver)
                .executeScript("return document.getElementById('requestId').innerHTML");
        System.out.println(requestId);
    }

    @Test
    public void teaserServiceAppearance() {
        Client client = MordaClient.getJsonEnabledClient();
        T dump = client.target("http://morda-mocks.wdevx.yandex.ru/api/v1/dumps/" + requestId)
                .request()
                .buildGet().invoke().readEntity(T.class);

        this.cleanvars = dump.data._full;

        Validator validator = new Validator(driver, morda).withCleanvars(cleanvars);
        collectorRule.getCollector()
                .check(page.getTeaserServiceBlock().validate(validator));
    }


    private static class T {
        public E data;
    }

    private static class E {
        public Cleanvars _full;
    }
}
