package ru.yandex.autotests.morda.tests.web.common.suggest;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.interfaces.blocks.BlockWithSuggest;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSearchBlock;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.morda.pages.desktop.yaru.DesktopYaruMorda.desktopYaru;
import static ru.yandex.autotests.morda.pages.touch.comtr.TouchComTrMorda.touchComTr;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 28/02/15
 */
@Aqua.Test(title = "Suggest appears")
@Features("Suggest")
@Stories("Suggest appears")
@RunWith(Parameterized.class)
public class SuggestAppearsTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private CommonMordaSteps user;
    private SuggestSteps userSuggest;

    @Parameterized.Parameters(name = "{0}, {1}")
    public static Collection<Object[]> data() {
        List<Object[]> data = new ArrayList<>();
        String request = "request";

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();
        String userAgentTouchIphone = CONFIG.getMordaUserAgentTouchIphone();
        String userAgentTouchWp = CONFIG.getMordaUserAgentTouchWp();
        String userAgentPda = CONFIG.getMordaUserAgentPda();

        List<Morda<?>> mordas = new ArrayList<>();

        mordas.add(desktopYaru(scheme, environment));
        mordas.add(touchComTr(scheme, environment, Region.ISTANBUL, userAgentTouchIphone));

        for (Morda<?> morda : MordaType.filter(mordas, CONFIG.getMordaPagesToTest())) {
            data.add(new Object[]{morda, request});
        }

        return data;
    }

    private Morda<? extends PageWithSearchBlock<? extends BlockWithSuggest>> morda;
    private PageWithSearchBlock<? extends BlockWithSuggest> page;
    private String request;

    public SuggestAppearsTest(Morda<? extends PageWithSearchBlock<? extends BlockWithSuggest>> morda, String request) {
        this.morda = morda;
        this.request = request;
        this.mordaAllureBaseRule = this.morda.getRule();
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.userSuggest = new SuggestSteps(driver);
        this.page = morda.getPage(driver);
    }

    @Before
    public void initialize() {
        morda.initialize(driver);
    }

    @Test
    public void suggestAppears() throws InterruptedException {
        user.shouldSeeElement(page.getSearchBlock());
        user.shouldSeeElement(page.getSearchBlock().getSearchInput());
        userSuggest.appendsTextInInputSlowly(page.getSearchBlock().getSearchInput(), request);
        user.shouldSeeElement(page.getSearchBlock().getSuggest());
    }

}
