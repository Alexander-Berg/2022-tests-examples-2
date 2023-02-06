package ru.yandex.autotests.mordacom.search;

//import net.lightbody.bmp.core.har.Har;
//import net.lightbody.bmp.proxy.http.BrowserMobHttpRequest;
//import net.lightbody.bmp.proxy.http.RequestInterceptor;
//import org.junit.Before;
//import org.junit.Rule;
//import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.openqa.selenium.WebDriver;
import ru.yandex.aqua.annotations.project.Aqua;
import ru.yandex.autotests.mordabackend.MordaClient;
import ru.yandex.autotests.mordabackend.utils.parameters.ServicesParameterProvider;
import ru.yandex.autotests.mordacom.Properties;
import ru.yandex.autotests.mordacom.pages.HomePage;
import ru.yandex.autotests.mordacom.pages.TuneSuggestPage;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.qatools.allure.annotations.Features;
import ru.yandex.qatools.allure.annotations.Stories;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import static ru.yandex.autotests.mordacom.data.SearchData.SUGGEST_TESTS;
//import static ru.yandex.autotests.mordacommonsteps.rules.proxy.actions.RequestInterceptorAction.addRequestInterceptor;
import static ru.yandex.autotests.utils.morda.auth.User.COM_DEFAULT;

/**
 * User: eoff
 * Date: 28.11.12
 */
@Aqua.Test(title = "Саджест")
@RunWith(Parameterized.class)
@Features("Search")
@Stories("Suggest")
public class SuggestTest {
//    private static final Properties CONFIG = new Properties();
//
//   /* @Rule
//    public MordaAllureBaseRule rule(){
//        return mordaAllureBaseRule.withProxyAction(addRequestInterceptor((browserMobHttpRequest, har) -> {
//
//        }));
//    }*/
//
//    @Rule
//    public MordaAllureBaseRule mordaAllureBaseRule = new MordaAllureBaseRule()
//            .withProxyAction(addRequestInterceptor((browserMobHttpRequest, har) -> {
//                System.out.println(browserMobHttpRequest.getMethod().getRequestLine().getUri());
//            }));
//
//    private WebDriver driver = mordaAllureBaseRule.getDriver();
//    private CommonMordaSteps user = new CommonMordaSteps(driver);
//    private HomePage homePage = new HomePage(driver);
//    private TuneSuggestPage tuneSuggestPage = new TuneSuggestPage(driver);
//
//    @Parameterized.Parameters(name = "{0}: {1}")
//    public static Collection<Object[]> data() {
//        List<Object[]> data = new ArrayList<>();
//        for (Language language : CONFIG.getMordaComLangs()) {
//            for (String request : SUGGEST_TESTS) {
//                data.add(new Object[]{language, request});
//            }
//        }
//        return data;
//    }
//
//    private final Language language;
//    private final String request;
//
//    public SuggestTest(Language language, String request) {
//        this.language = language;
//        this.request = request;
//    }
//
//    @Before
//    public void setUp() {
//        user.opensPage(CONFIG.getBaseURL());
//        user.setsLanguageOnCom(language);
//    }
//
//    @Test
//    public void suggestAppears() {
//        user.shouldSeeElement(homePage.search.input);
//        user.clearsInput(homePage.search.input);
//        user.entersTextInInput(homePage.search.input, request);
//        user.shouldSeeElement(homePage.search.suggest);
//        user.clicksOn(homePage.search.input);
//        user.clearsInput(homePage.search.input);
//        user.entersTextInInput(homePage.search.input, "");
//        user.shouldNotSeeElement(homePage.search.suggest);
//    }
//
//    @Test
//    public void suggestAppearsLogin() {
//        user.logsInAs(COM_DEFAULT, CONFIG.getBaseURL());
//        user.shouldSeeElement(homePage.search.input);
//        user.clearsInput(homePage.search.input);
//        user.entersTextInInput(homePage.search.input, request);
//        user.shouldSeeElement(homePage.search.suggest);
//        user.clicksOn(homePage.search.input);
//        user.clearsInput(homePage.search.input);
//        user.entersTextInInput(homePage.search.input, "");
//        user.shouldNotSeeElement(homePage.search.suggest);
//    }
}
