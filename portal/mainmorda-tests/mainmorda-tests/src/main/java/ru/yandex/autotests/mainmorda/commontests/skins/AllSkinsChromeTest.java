package ru.yandex.autotests.mainmorda.commontests.skins;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.steps.SkinsSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.Collection;

import static ru.yandex.autotests.mainmorda.data.SkinsData.ALL_SKINS;
import static ru.yandex.autotests.mordacommonsteps.rules.proxy.actions.HarAction.addHar;

@Aqua.Test(title = "Проверка всех скинов в Chrome")
@RunWith(Parameterized.class)
@Features({"Main", "Common", "Skins"})
@Stories("Static In Chrome")
public class AllSkinsChromeTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule(DesiredCapabilities.chrome())
            .withProxyAction(addHar("skins_har"));

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private SkinsSteps userSkins = new SkinsSteps(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        return ParametrizationConverter.convert(ALL_SKINS);
    }

    private String skinId;

    public AllSkinsChromeTest(String skinId) {
        this.skinId = skinId;
    }

    @Test
    public void skinStaticFirefox() throws Exception {
        user.opensPage(CONFIG.getBaseURL() + "/themes/" + skinId);
        userSkins.shouldSeeSkinInBrowser(skinId, "chrome");
        userSkins.shouldSeeSkinResources(skinId);
        user.shouldSeeStaticIsDownloaded(mordaAllureBaseRule.getProxyServer().getHar());
    }
}