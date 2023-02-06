package ru.yandex.autotests.turkey.all;

import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.turkey.Properties;
import ru.yandex.autotests.turkey.pages.AllServicesPage;
import ru.yandex.autotests.turkey.steps.AllServicesSteps;
import ru.yandex.autotests.turkey.utils.Service;
import ru.yandex.autotests.utils.morda.ParametrizationConverter;
import ru.yandex.qatools.allure.annotations.Features;

import java.util.Collection;

import static ru.yandex.autotests.turkey.data.AllServicesData.getTopServicesList;


/**
 * User: Poluektov Evgeniy <poluektov@yandex-team.ru>
 * on: 03.02.2015.
 */

@Aqua.Test(title = "Сервисы в верхней части страницы")
@Features("All Services")
@RunWith(Parameterized.class)
public class ServicesTopTest {
    private static final Properties CONFIG = new Properties();

    @Rule
    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule();

    private WebDriver driver = mordaAllureBaseRule.getDriver();
    private CommonMordaSteps user = new CommonMordaSteps(driver);
    private AllServicesSteps userAll = new AllServicesSteps(driver);
    private AllServicesPage allServicesPage = new AllServicesPage(driver);

    @Parameterized.Parameters(name = "{0}")
    public static Collection<Object[]> testData() {
        return ParametrizationConverter.convert(getTopServicesList());
    }

    private Service service;

    public ServicesTopTest(Service service) {
        this.service = service;
    }

    @Before
    public void setUp() {
        user.opensPage(CONFIG.getBaseURL() + "/all");
        user.shouldSeeElement(allServicesPage.allServicesTopList);
    }

    @Test
    public void serviceContent() {
        userAll.shouldSeeService(allServicesPage.allServicesTopList, service);
    }
}
