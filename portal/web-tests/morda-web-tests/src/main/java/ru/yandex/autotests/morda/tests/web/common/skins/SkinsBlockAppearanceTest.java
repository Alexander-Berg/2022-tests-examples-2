package ru.yandex.autotests.morda.tests.web.common.skins;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda;
import ru.yandex.autotests.morda.pages.desktop.main.widgets.SkinsBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSkinsBlock;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollectorRule;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.morda.tests.web.utils.SkinSteps;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordabackend.beans.themes.Group;
import ru.yandex.autotests.mordabackend.beans.themes.Themes;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Optional;

import static org.junit.Assert.fail;
import static ru.yandex.autotests.morda.pages.desktop.main.DesktopMainMorda.desktopMain;
import static ru.yandex.autotests.mordabackend.MordaClient.getJsonEnabledClient;

/**
 * User: asamar
 * Date: 27.11.2015.
 */
@Aqua.Test(title = "Themes Block Appearance")
@Features("Skins")
@Stories("Themes Block Appearance")
@RunWith(Parameterized.class)
public class SkinsBlockAppearanceTest {
    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private WebDriver driver;
    private HierarchicalErrorCollectorRule collectorRule;

    @Parameterized.Parameters(name = "{0}, {2}")
    public static Collection<Object[]> data() {
//        List<Morda<? extends PageWithSkinsBlock<? extends Validateable>>> data = new ArrayList<>();
        List<Object[]> data = new ArrayList<>();

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();

        DesktopMainMorda morda = desktopMain(scheme, environment, Region.SANKT_PETERBURG);

        Cleanvars cleanvars = new MordaClient(morda.getThemeUrl())
                .cleanvarsActions(getJsonEnabledClient())
                .get();

        Themes themes = cleanvars.getThemes();
        List<Group> groups = themes.getGroup();
        Group allGroup = new Group();
        allGroup.setId("all");
        groups.add(0, allGroup);
        groups.stream().forEach(it ->
            data.add(new Object[]{morda, it, it.getId()})
        );

//        data.add(desktopMain(scheme, environment, Region.SANKT_PETERBURG));

        return data;//convert(MordaType.filter(data, CONFIG.getMordaPagesToTest()));
    }

    private DesktopMainMorda morda;
    private PageWithSkinsBlock<SkinsBlock> page;
    private Cleanvars cleanvars;
    private CommonMordaSteps user;
    private SkinSteps skinSteps;
    private Validator<DesktopMainMorda> validator;
    private Group group;

    public SkinsBlockAppearanceTest(DesktopMainMorda morda, Group group, String name) {
        this.morda = morda;
        this.collectorRule = new HierarchicalErrorCollectorRule();
        this.mordaAllureBaseRule = this.morda.getRule().withRule(collectorRule);
        this.driver = mordaAllureBaseRule.getDriver();
        this.page = morda.getPage(driver);
        this.user = new CommonMordaSteps(driver);
        this.skinSteps = new SkinSteps(driver);
        this.group = group;
    }

    @Before
    public void init() {
//        morda.initialize(driver);
        user.opensPage(morda.getThemeUrl().toString());
        String requestId = (String) ((JavascriptExecutor) driver)
                .executeScript("return document.getElementById('requestId').innerHTML");
        System.out.println(requestId);

        Client client = MordaClient.getJsonEnabledClient();
        this.cleanvars = client.target("http://morda-mocks.wdevx.yandex.ru/api/v1/dumps/" + requestId + "/cleanvars")
                .request()
                .buildGet().invoke().readEntity(Cleanvars.class);
        validator = new Validator<>(driver, morda).withCleanvars(cleanvars);
    }

    @Test
    public void groupTest() {
        Optional<SkinsBlock.ThemeGroup> theme = page.getSkinsBlock().themeGroups.stream()
                .filter(it -> it.getGroupName().equals(group.getId()))
                .findFirst();
        if(theme.isPresent()){
            user.clicksOn(theme.get());
        }else {
            fail("Группы с id=" + group.getId() +" нет в верстке");
        }
        skinSteps.rightScrollThemes();
        collectorRule.getCollector()
                .check(page.getSkinsBlock().validate(validator));
    }
}
