package ru.yandex.autotests.mordamobile.all;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordamobile.Properties;
import ru.yandex.autotests.mordamobile.pages.AllServicesPage;
import ru.yandex.autotests.mordamobile.steps.AllServicesSteps;
import ru.yandex.autotests.mordamobile.utils.Service;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.Collection;

import static ru.yandex.autotests.mordamobile.data.AllServicesData.getAllServicesList;

/**
 * User: Poluektov Evgeniy <poluektov@yandex-team.ru>
 * on: 05.02.2015.
 */
@Aqua.Test(title = "Проверка списка всех сервисов в центре страницы")
@RunWith(Parameterized.class)
@Features("All Services")
public class ServicesAllTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private AllServicesSteps userAll = new AllServicesSteps(driver);
    private AllServicesPage allServicesPage = new AllServicesPage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(getAllServicesList());
    }

    private Service service;

    public ServicesAllTest(Service service) {
        this.service = service;
    }

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL() + "/all");
        user.shouldSeeElement(allServicesPage.allServicesAllList);
    }

    @Test
    public void serviceContent() {
        userAll.shouldSeeService(allServicesPage.allServicesAllList, service);
    }
}
