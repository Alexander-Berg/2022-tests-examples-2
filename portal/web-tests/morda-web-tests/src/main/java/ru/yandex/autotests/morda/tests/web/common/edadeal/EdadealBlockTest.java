package ru.yandex.autotests.morda.tests.web.common.edadeal;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.morda.pages.interfaces.validation.Validator;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuPage;
import ru.yandex.autotests.morda.rules.errorcollector.HierarchicalErrorCollectorRule;
import ru.yandex.autotests.morda.tests.web.MordaWebTestsProperties;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.beans.cleanvars.Cleanvars;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import javax.ws.rs.client.Client;
import java.util.Collection;
import java.util.stream.Stream;

import static java.util.stream.Collectors.toList;
import static ru.yandex.autotests.morda.pages.touch.ru.TouchRuMorda.touchRu;
import static ru.yandex.autotests.utils.morda.language.Language.BE;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.Language.UK;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;

/**
 * User: asamar
 * Date: 20.02.17
 */
@Aqua.Test(title = "Edadeal Block Appearance")
@Features("Edadeal")
@Stories("Edadeal Block Appearance")
@RunWith(Parameterized.class)
public class EdadealBlockTest {

    private static final MordaWebTestsProperties CONFIG = new MordaWebTestsProperties();

    @Parameterized.Parameters(name = "{0}")
    public static Collection<TouchRuMorda> data() {

        String scheme = CONFIG.getMordaScheme();
        String environment = CONFIG.getMordaEnvironment();
        String useragentTouch = CONFIG.getMordaUserAgentTouchIphone();

        return Stream.of(RU, UK, BE)
                .map(lang -> touchRu(scheme, environment, useragentTouch, MOSCOW, lang))
                .collect(toList());
    }

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule;
    private HierarchicalErrorCollectorRule collectorRule;
    private WebDriver driver;
    private CommonMordaSteps user;
    private TouchRuMorda morda;
    private TouchRuPage page;
    private String requestId;
    private Cleanvars cleanvars;

    public EdadealBlockTest(TouchRuMorda morda) {
        this.morda = morda;
        this.collectorRule = new HierarchicalErrorCollectorRule();
        this.mordaAllureBaseRule = this.morda.getRule().withRule(collectorRule);
        this.driver = mordaAllureBaseRule.getDriver();
        this.user = new CommonMordaSteps(driver);
        this.page = morda.getPage(driver);
    }

    @Before
    public void initialize() throws InterruptedException {
        morda.initialize(driver);
        requestId = (String) ((JavascriptExecutor) driver)
                .executeScript("return document.getElementById('requestId').innerHTML");
        System.out.println(requestId);
    }

    @Test
    public void collectionsAppearance() {
        Client client = MordaClient.getJsonEnabledClient();
        this.cleanvars = client.target("http://morda-mocks.wdevx.yandex.ru/api/v1/dumps/" + requestId + "/cleanvars")
                .request()
                .buildGet().invoke().readEntity(Cleanvars.class);

        Validator validator = new Validator<>(driver, morda).withCleanvars(cleanvars);
        collectorRule.getCollector()
                .check(page.getEdadealBlock().validate(validator));

    }
}
