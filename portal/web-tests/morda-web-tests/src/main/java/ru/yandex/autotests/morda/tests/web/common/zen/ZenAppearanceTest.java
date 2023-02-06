package ru.yandex.autotests.morda.tests.web.common.zen;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithZenBlock;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollectorRule;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda.touchRu;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.utils.morda.language.Language.BE;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.Language.UK;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
@Aqua.Test(title = "Zen Block Appearance")
@Features("Zen")
@Stories("Zen Block Appearance")
@RunWith(Parameterized.class)
public class ZenAppearanceTest {

    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();
    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private HierarchicalErrorCollectorRule collectorRule;
    private WebDriver driver;
    private CommonMordaSteps user;
    private Morda<? extends PageWithZenBlock<? extends Validateable>> morda;
    private PageWithZenBlock<? extends Validateable> page;

    public ZenAppearanceTest(Morda<? extends PageWithZenBlock<? extends Validateable>> morda) {
        this.morda = morda;
        this.collectorRule = new HierarchicalErrorCollectorRule();
//        String yandexuidWithZen = new YandexuidGenerator().getYandexuid(withZen());
        this.mordaAllureBaseRule = this.morda.getRule().withRule(collectorRule);
//                .mergeProxyAction(CookieAction.class, new HashSet<>(asList(new Cookie("yandexuid", yandexuidWithZen))));
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.page = morda.getPage(driver);
    }

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();
        String useragentTouch = CONFIG.getMordaUserAgentTouchIphone();

        List<Morda<? extends PageWithZenBlock<? extends Validateable>>> data = new ArrayList<>();
        for (Language language : asList(RU, UK, BE)) {
            data.add(touchRu(scheme, environment, useragentTouch, Region.MOSCOW, language));
        }
        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    @Before
    public void initialize() {
        morda.initialize(driver);
    }

    @Test
    public void zenAppearance() {
        Validator validator = new Validator(driver, morda);
        collectorRule.getCollector()
                .check(page.getZenBlock().validate(validator));
    }
}
