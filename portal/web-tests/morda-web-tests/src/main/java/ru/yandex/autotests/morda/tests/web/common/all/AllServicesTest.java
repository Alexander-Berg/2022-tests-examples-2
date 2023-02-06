package ru.yandex.autotests.morda.tests.web.common.all;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSearchBlock;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validateable;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollectorRule;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static java.util.Arrays.asList;
import static ru.yandex.autotests.morda.pages.desktop.com.DesktopComMorda.desktopCom;
import static ru.yandex.autotests.utils.morda.ParametrizationConverter.convert;
import static ru.yandex.autotests.utils.morda.language.Language.EN;
import static ru.yandex.autotests.utils.morda.language.Language.ID;

/**
 * User: asamar
 * Date: 25.09.2015.
 */
@Aqua.Test(title = "Редирект /all на морду")
@Features("All services")
@RunWith(Parameterized.class)
public class AllServicesTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        List<Morda<?>> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();

        for (Language language : asList(EN, ID)) {
            data.add(desktopCom(scheme, environment, language));
        }
        return convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private HierarchicalErrorCollectorRule collectorRule;
    private WebDriver driver;
    private CommonMordaSteps user;
    private Morda<? extends PageWithSearchBlock> morda;
    private PageWithSearchBlock<? extends Validateable> page;
    private String requestId;
    private Cleanvars cleanvars;

    public AllServicesTest(Morda<? extends PageWithSearchBlock> morda) {
        this.morda = morda;
        this.collectorRule = new HierarchicalErrorCollectorRule();
        this.mordaAllureBaseRule = this.morda.getRule().withRule(collectorRule);
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.page = morda.getPage(driver);
    }

    @Before
    public void initialize(){
        morda.initialize(driver);
    }

    @Test
    public void allRedirect() throws InterruptedException {
        user.opensPage(morda.getUrl() + "/all", morda.getUrl().toString());
    }
}
