package ru.yandex.autotests.morda.tests.web.mail;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithLoginDomik;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollectorRule;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.morda.pages.touch.comtr.TouchComTrMorda.touchComTr;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 09/04/15
 */
@Aqua.Test(title = "Login Domik Appearance")
@Features("Mail")
@Stories("Login Domik Appearance")
@RunWith(Parameterized.class)
public class LoginDomikAppearanceTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private HierarchicalErrorCollectorRule collectorRule;

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda<? extends PageWithLoginDomik<? extends Validateable>>> data = new ArrayList<>();

        data.add(touchComTr(CONFIG.getMordaScheme(), CONFIG.getMordaEnvironment(), Region.ISTANBUL,
                CONFIG.getMordaUserAgentTouchIphone()));

        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    private Morda<? extends PageWithLoginDomik<? extends Validateable>> morda;
    private PageWithLoginDomik<? extends Validateable> page;

    public LoginDomikAppearanceTest(Morda<? extends PageWithLoginDomik<? extends Validateable>> morda) {
        this.morda = morda;
        this.collectorRule = new HierarchicalErrorCollectorRule();
        this.mordaAllureBaseRule = this.morda.getRule().withRule(collectorRule);
        this.driver = mordaAllureBaseRule.getDriver();
        this.page = morda.getPage(driver);
    }

    @Before
    public void initialize() {
        morda.initialize(driver);
        page.openLoginDomik();
    }

    @Test
    public void loginDomikAppearance() throws InterruptedException {
        Validator<?> validator = new Validator<>(driver, morda);
        collectorRule.getCollector()
                .check(page.getLoginDomik().validate(validator));
    }

}
