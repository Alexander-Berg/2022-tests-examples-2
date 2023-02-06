package ru.yandex.autotests.hwmorda.steps;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.hwmorda.pages.FotkiPage;
import ru.yandex.autotests.hwmorda.pages.MainHomePage;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import static ru.yandex.autotests.utils.morda.language.Dictionary.Local.Traffic.TRAFFIC_0;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Local.Traffic.TRAFFIC_1;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Local.Traffic.TRAFFIC_10;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Local.Traffic.TRAFFIC_2;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Local.Traffic.TRAFFIC_3;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Local.Traffic.TRAFFIC_4;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Local.Traffic.TRAFFIC_5;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Local.Traffic.TRAFFIC_6;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Local.Traffic.TRAFFIC_7;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Local.Traffic.TRAFFIC_8;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Local.Traffic.TRAFFIC_9;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;

/**
 * User: alex89
 * Date: 12.09.12
 */

public class HwUserSteps {

    private WebDriver driver;
    private MainHomePage mainHomePage;
    private FotkiPage fotkiPage;
    private CommonMordaSteps user;

    public HwUserSteps(WebDriver driver) {
        this.driver = driver;
        user = new CommonMordaSteps(driver);
        mainHomePage = new MainHomePage(driver);
        fotkiPage = new FotkiPage(driver);
    }

    public static final Map<Integer, String> TRAFFIC_DESCRIPTIONS = new HashMap<Integer, String>() {{
        put(0, getTranslation(TRAFFIC_0, RU));
        put(1, getTranslation(TRAFFIC_1, RU));
        put(2, getTranslation(TRAFFIC_2, RU));
        put(3, getTranslation(TRAFFIC_3, RU));
        put(4, getTranslation(TRAFFIC_4, RU));
        put(5, getTranslation(TRAFFIC_5, RU));
        put(6, getTranslation(TRAFFIC_6, RU));
        put(7, getTranslation(TRAFFIC_7, RU));
        put(8, getTranslation(TRAFFIC_8, RU));
        put(9, getTranslation(TRAFFIC_9, RU));
        put(10, getTranslation(TRAFFIC_10, RU));
    }};

    @Step
    public String getFotoSrc() {
        return fotkiPage.foto.getAttribute("style").replace("http:", "").replace("https:", "").replaceAll("_X\\dL\"\\);$", "_L\");");
    }

    @Step
    public void shouldSeeNotZeroTrafficPoints() {
        if (!mainHomePage.traffic.trafficPoints.getText().isEmpty()) {
            user.shouldSeeElement(mainHomePage.traffic.trafficPoints);
        }
    }

    @Step
    public String getBMWTrafficMessage(HtmlElement element) {
        String text = user.getElementText(element)
                .replaceAll("[↓↑]", "")
                .replaceAll("(?<=^)(?=\\n)", "0баллов");
        Matcher matcher = Pattern.compile("[\\d]{1,2}(?=балл)").matcher(text);
        if (matcher.find()) {
            int points = Integer.parseInt(matcher.group());
            return text.replaceAll("((?=\\n\\Q" + TRAFFIC_DESCRIPTIONS.get(points) + "\\E)|\\n[А-я ]+$)", "");
        } else {
            return text;
        }
    }
}
