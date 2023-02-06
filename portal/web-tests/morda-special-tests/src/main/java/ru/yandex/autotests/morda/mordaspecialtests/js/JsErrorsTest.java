package ru.yandex.autotests.morda.mordaspecialtests.js;

import org.apache.log4j.Logger;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.logging.LogEntry;
import org.openqa.selenium.logging.LogType;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.aqua.annotations.project.Feature;
import ru.yandex.autotests.morda.mordaspecialtests.Properties;
import ru.yandex.autotests.morda.mordaspecialtests.data.ProjectInfo;
import ru.yandex.autotests.morda.mordaspecialtests.utils.DataUtils;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.terra.junit.rules.BottleMessageRule;

import java.io.IOException;
import java.util.Collection;
import java.util.List;
import java.util.logging.Level;

import static ch.lambdaj.Lambda.having;
import static ch.lambdaj.Lambda.on;
import static ch.lambdaj.Lambda.select;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasSize;
import static ru.yandex.autotests.mordacommonsteps.rules.proxy.actions.HarAction.addHar;

/**
 * Created by eoff on 09/10/14.
 */
@Aqua.Test(title = "JS Errors", description = "")
@RunWith(Parameterized.class)
@Feature("JS Errors")
public class JsErrorsTest {
    private static final Properties CONFIG = new Properties();
    public static final Logger LOG = Logger.getLogger(JsErrorsTest.class);

    @Rule
    public MordaAllureBaseRule rule() {
        return mordaAllureBaseRule
                .withProxyAction(addHar("js-test"))
                .withRule(new BottleMessageRule());
    }

    private MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();
    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> data() {
        return ParametrizationConverter.convert(DataUtils.getData(CONFIG.isRc()));
    }

    private ProjectInfo.ProjectInfoCase projectInfoCase;
    private String url;

    public JsErrorsTest(ProjectInfo.ProjectInfoCase projectInfoCase) {
        this.projectInfoCase = projectInfoCase;
        this.url = (CONFIG.isRc()) ? projectInfoCase.getTest() : projectInfoCase.getProd();
    }

    @Test
    public void noJSErrors() throws IOException {
        user.opensPage(url);

        List<LogEntry> severeLogs = select(driver.manage().logs().get(LogType.BROWSER).getAll(),
                having(on(LogEntry.class).getLevel(), equalTo(Level.SEVERE)));

        assertThat("Detected " + severeLogs.size() + " js-errors: " + severeLogs, severeLogs, hasSize(0));
    }

    @Test
    public void staticIsOk() {
        user.opensPage(url);
        user.shouldSeeStaticIsDownloaded(mordaAllureBaseRule.getProxyServer().getHar());
    }
}
