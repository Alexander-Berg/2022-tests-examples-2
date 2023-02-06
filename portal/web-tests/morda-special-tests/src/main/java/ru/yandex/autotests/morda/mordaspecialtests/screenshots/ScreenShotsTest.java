package ru.yandex.autotests.morda.mordaspecialtests.screenshots;

import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.By;
import org.openqa.selenium.Dimension;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.aqua.annotations.project.Feature;
import ru.yandex.autotests.morda.mordaspecialtests.Properties;
import ru.yandex.autotests.morda.mordaspecialtests.data.ProjectInfo;
import ru.yandex.autotests.morda.mordaspecialtests.utils.DataUtils;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Attachment;
import ru.yandex.qatools.ashot.AShot;
import ru.yandex.qatools.ashot.Screenshot;
import ru.yandex.qatools.ashot.comparison.ImageDiff;
import ru.yandex.qatools.ashot.comparison.ImageDiffer;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.is;
import static ru.yandex.autotests.mordacommonsteps.rules.proxy.actions.HarAction.addHar;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 14/10/14
 */
@Aqua.Test(title = "ScreenShots at Rc and Prod", description = "")
@RunWith(Parameterized.class)
@Feature("ScreenShots at Rc and Prod")
public class ScreenShotsTest {

    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule rule() {
        return mordaAllureBaseRule.withProxyAction(addHar("js-test"));
    }

    private MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();
    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);

    @Parameterized.Parameters(name = "{1}, {0}")
    public static Collection<Object[]> data() {

        List<Dimension> dimensions = Arrays.asList(
                new Dimension(800, 600),
                new Dimension(1600, 600),
                new Dimension(600, 1600),
                new Dimension(1600, 1200)
        );

        List<ProjectInfo.ProjectInfoCase> list = DataUtils.getData(false);

        List<Object[]> data = new ArrayList<>();

        for (Dimension dimension : dimensions) {
            for (ProjectInfo.ProjectInfoCase projectCase : list) {
                data.add(new Object[]{dimension, projectCase});
            }
        }

        return data;
    }

    private Dimension dimension;
    private ProjectInfo.ProjectInfoCase projectInfoCase;

    public ScreenShotsTest(Dimension dimension, ProjectInfo.ProjectInfoCase projectInfoCase) {
        this.dimension = dimension;
        this.projectInfoCase = projectInfoCase;
    }

    @Test
    public void screenshot() throws IOException, InterruptedException {
        user.resizeWindow(dimension);

        Screenshot prod = makeScreenshot("prod", driver, projectInfoCase.getProd(), projectInfoCase.getExcude(),
                projectInfoCase.getJs());
        Screenshot test = makeScreenshot("test", driver, projectInfoCase.getTest(), projectInfoCase.getExcude(),
                projectInfoCase.getJs());

        ImageDiff diff = new ImageDiffer().makeDiff(prod, test);
        attach("diff", diff.getMarkedImage());

        assertThat("Images are different", diff.hasDiff(), is(false));
    }

    private Screenshot makeScreenshot(String name, WebDriver driver, String url, List<By> exclude, String js)
            throws InterruptedException {
        user.opensPage(url);

        executeJs(js);
        Thread.sleep(CONFIG.getTimeout());

        Screenshot screenshot = new AShot().ignoredElements(exclude).takeScreenshot(driver);
        attach(name, screenshot.getImage());
        return screenshot;
    }

    private void executeJs(String js) {
        ((JavascriptExecutor) driver).executeScript(js);
    }

    @Attachment("{0}")
    public byte[] attach(String name, BufferedImage screenshot) {
        try (ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
            ImageIO.write(screenshot, "png", baos);
            return baos.toByteArray();
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
}
