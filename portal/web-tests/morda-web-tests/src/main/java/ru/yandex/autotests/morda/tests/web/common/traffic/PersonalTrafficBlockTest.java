package ru.yandex.autotests.morda.tests.web.common.traffic;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSearchForm;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSearchBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithTrafficBlock;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ru.blocks.TrafficBlock;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollectorRule;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda.touchRu;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.utils.morda.auth.UserManager.login;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.region.Region.SANKT_PETERBURG;

/**
 * User: asamar
 * Date: 22.09.2015.
 */
@Aqua.Test(title = "Traffic link test")
@Features("Traffic")
@Stories("Traffic link test")
@RunWith(Parameterized.class)
public class PersonalTrafficBlockTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda<? extends PageWithSearchBlock<? extends BlockWithSearchForm>>> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();
        String userAgentTouchIphone = CONFIG.getMordaUserAgentTouchIphone();

        data.add(touchRu(scheme, environment, userAgentTouchIphone, SANKT_PETERBURG, RU));

        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private HierarchicalErrorCollectorRule collectorRule;
    private WebDriver driver;
    private CommonMordaSteps user;
    private Morda<? extends PageWithTrafficBlock<? extends TrafficBlock>> morda;
    private PageWithTrafficBlock<? extends TrafficBlock> page;

    public PersonalTrafficBlockTest(Morda<? extends PageWithTrafficBlock<? extends TrafficBlock>> morda) {
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
        login(driver, "morda-trafficblock","Rcgfght!1.", morda.getUrl().toString());
    }

    @Test
    public void directionLinkTest() throws InterruptedException {
        user.shouldSeeElement(page.getTrafficBlock());
        user.shouldSeeElement(page.getTrafficBlock().directionLink);
        Validator validator = new Validator(driver, morda);
        collectorRule.getCollector().check(page.getTrafficBlock().validate(validator));
    }
}
