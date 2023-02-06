package ru.yandex.autotests.morda.tests.web.common.logo;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.desktop.firefox.DesktopFirefoxMorda;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithFirefoxLogo;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollectorRule;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 28/02/15
 */
@Aqua.Test(title = "Firefox Logo")
@Features("Logo")
@Stories("Firefox Logo")
@RunWith(Parameterized.class)
public class FirefoxLogoTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private CommonMordaSteps user;
    private HierarchicalErrorCollectorRule collectorRule;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda<? extends PageWithFirefoxLogo<? extends Validateable>>> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();

//        data.add(desktopFirefoxRu(scheme, environment, Region.MOSCOW, Language.RU));
//        data.add(desktopFirefoxUa(scheme, environment, Region.KIEV, Language.UK));
//        data.add(desktopFirefoxComTr(scheme, environment, Region.IZMIR));

        data.addAll(DesktopFirefoxMorda.getDefaultList(scheme, environment));
        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    private Morda<? extends PageWithFirefoxLogo<? extends Validateable>> morda;
    private PageWithFirefoxLogo<? extends Validateable> page;

    public FirefoxLogoTest(Morda<? extends PageWithFirefoxLogo<? extends Validateable>> morda) {
        this.morda = morda;
        this.collectorRule = new HierarchicalErrorCollectorRule();
        this.mordaAllureBaseRule = this.morda.getRule().withRule(collectorRule);
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.page = morda.getPage(driver);
    }

    @Before
    public void init() throws InterruptedException {
        morda.initialize(driver);
    }

    @Test
    public void logo() throws InterruptedException {
        Validator<?> validator = new Validator<>(driver, morda);
        collectorRule.getCollector()
                .check(page.getFirefoxLogo().validate(validator));
    }
}
