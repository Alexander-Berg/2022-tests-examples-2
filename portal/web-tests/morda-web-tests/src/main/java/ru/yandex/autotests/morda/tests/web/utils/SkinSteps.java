package ru.yandex.autotests.morda.tests.web.utils;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.glassfish.jersey.client.JerseyClient;
import org.glassfish.jersey.client.JerseyClientBuilder;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.pages.desktop.main.DesktopMainPage;
import ru.yandex.autotests.morda.pages.touch.ru.TouchRuPage;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.cookie.CookieManager;
import ru.yandex.qatools.allure.annotations.Step;

import java.net.URI;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static javax.ws.rs.core.UriBuilder.fromUri;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.endsWith;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.not;
import static ru.yandex.autotests.utils.morda.language.Dictionary.Home.Mobile.FOOT_TUNE;
import static ru.yandex.autotests.utils.morda.language.Language.RU;
import static ru.yandex.autotests.utils.morda.language.LanguageManager.getTranslation;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.exists;

/**
 * User: alex89
 * Date: 22.01.13
 */

public class SkinSteps {

    private WebDriver driver;
    private CommonMordaSteps userSteps;
    private DesktopMainPage page;

    public SkinSteps(WebDriver driver) {
        this.driver = driver;
        this.userSteps = new CommonMordaSteps(driver);
        this.page = new DesktopMainPage(driver);
    }

    @Step
    public void opensThemeMenu(String themeUrl) {
        userSteps.opensPage(themeUrl);
        userSteps.shouldSeeElement(page.getSkinsBlock());
    }

    @Step
    public void setAnySkinWithClick() {
        page.getSkinsBlock().skins.stream()
                .filter(sk -> !sk.getId().equals("default") && !sk.getId().equals("random"))
                .findAny().ifPresent(userSteps::clicksOn);
    }

    @Step("Set skin")
    public void setSkin(String skinId, String themeUrl, String browserName){
        opensThemeMenu(themeUrl);
        clickSkinOnPanel(skinId);
        shouldSeeSkinInBrowser(skinId, browserName);
        userSteps.shouldSeeElement(page.getSkinsBlock().save);
        userSteps.clicksOn(page.getSkinsBlock().save);
        userSteps.shouldNotSeeElement(page.getSkinsBlock());
        shouldSeeSkinInBrowser(skinId, browserName);
    }

    @Step
    public void clickSkinOnPanel(String skinId) {
        page.getSkinsBlock().skins.stream()
                .filter(skin -> skin.getId().equals(skinId))
                .findFirst()
                .ifPresent(userSteps::clicksOn);
    }

    @Step
    public void setSkinWithUrl(String themeUrl){
        driver.get(themeUrl + "/set?sk=" + CookieManager.getSecretKey(driver));
    }

    @Step
    public void resetSkins(String themeUrl) {
        driver.get(themeUrl + "/default/set?sk=" + CookieManager.getSecretKey(driver));
    }

    @Step("Reset skin from menu")
    public void resetSkinFromMenu(){
        userSteps.clicksOn(page.getHeaderBlock().settings);
        userSteps.shouldSeeElement(page.getHeaderBlock().settingsPopup.resetSkin);
        userSteps.clicksOn(page.getHeaderBlock().settingsPopup.resetSkin);
        shouldSeeDefaultMordaDesign();
    }

    @Step("Reset skin from panel")
    public void resetSkinFromPanel(String themeMenuUrl){
        opensThemeMenu(themeMenuUrl);
        userSteps.shouldSeeElement(page.getSkinsBlock().reset);
        userSteps.clicksOn(page.getSkinsBlock().reset);
        shouldSeeDefaultMordaDesign();
    }

    @Step
    public void shouldSeeSkinInBrowser(String skinId, String browserName) {
        String href = page.getSkinCss().getAttribute("href").split(":")[1];
        href = href.replace("static.yandex.sx", "yastatic.net");
        List<String> skinName = getSkinsMap(getSkinsVersion()).get(href);
        assertThat(skinName, hasItem(equalTo("bender/" + skinId + "/_" + skinId + ("chrome".equals(browserName) ? ".webp.css" : ".css"))));
    }

    @Step
    public void shouldSeeSkinResources(String skinId) {
        if (exists().matches(page.getSkinScript())) {
            String src = page.getSkinScript().getAttribute("src").split(":")[1];
            List<String> skinNames = getSkinsMap(getSkinsVersion()).get(src);
            assertThat(skinNames, hasItem(("bender/" + skinId + "/_" + skinId + ".js")));
        }
    }


    public static Map<String, List<String>> getSkinsMap(String skinsVersion) {
        try {
            JerseyClient client = JerseyClientBuilder.createClient();
            String result = client.target("https://yastatic.net/www-skins/")
                    .path(skinsVersion)
                    .path("/skins/freeze.json")
                    .request()
                    .get(String.class);
            return inverseMap(new ObjectMapper().readValue(result, HashMap.class));
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    public static Map<String, List<String>> getTouchSkinsMap(String skinsVersion) {
        try {
            JerseyClient client = JerseyClientBuilder.createClient();
            String result = client.target("https://yastatic.net/www-skins/")
                    .path(skinsVersion)
                    .path("/skins/freeze_touch.json")
                    .request()
                    .get(String.class);
            return inverseMap(new ObjectMapper().readValue(result, HashMap.class));
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    private static <K, V> Map<V, List<K>> inverseMap(Map<K, V> map) {

        /*return map.entrySet().stream().collect(
                HashMap<V, List<K>>::new,
                (t, u) -> t.put(u.getValue(), u.getKey()),
                HashMap<V, List<K>>::putAll);*/

        Map<V, List<K>> result = new HashMap<V, List<K>>();
        for (Map.Entry<K, V> entry : map.entrySet()) {
            List<K> toInsert = new ArrayList<>();
            if (result.containsKey(entry.getValue())) {
                toInsert = result.get(entry.getValue());
            }
            toInsert.add(entry.getKey());
            result.put(entry.getValue(), toInsert);
        }
        return result;
    }

    @Step
    public void rightScrollThemes() {
        while (page.getSkinsBlock().rightArrow.isDisplayed()) {
            userSteps.clicksOn(page.getSkinsBlock().rightArrow);
            try {
                Thread.sleep(200);
            } catch (InterruptedException ignore) {
            }
        }
    }

    private String getSkinsVersion() {
        return  (String) ((JavascriptExecutor) driver)
                .executeScript("return JSON.parse(document.getElementsByClassName('page-info')[0].innerHTML).skins");
    }

    @Step
    public void shouldSeeDefaultMordaDesign() {
        assertThat(page.getSkinCss(), not(exists()));
    }

    @Step("Skin css {1} {2}")
    public void shouldSeeSkinInTouch(TouchRuPage page, String skinId, String browserName){
        String href = page.getSkinCss().getAttribute("href").split(":")[1];
        List<String> skinName = getTouchSkinsMap(getSkinsVersion()).get(href);
        assertThat(skinName, hasItem(equalTo("touch/" + skinId + "/_" + skinId + ("chrome".equals(browserName) ? ".webp.css" : ".css"))));
    }

    @Step("Should not see any skin on page")
    public void shouldNotSeeSkin(TouchRuPage page){
        assertThat(page.getSkinCss(), not(exists()));
    }

    @Step("Switch off skin")
    public void disableSkinOnTouch(TouchRuPage page){
        page.openMenu();
        page.getMenuBlock().allLinks.stream()
                .filter(e -> e.getText().equals(getTranslation(FOOT_TUNE, RU)))
                .findFirst()
                .get()
                .click();
        page.getTune().switchOffTheme();
    }

    @Step
    public void shouldSeeCoverInBrowser(String id){
        String cssUrl = page.getCoverCss().getAttribute("href");
        assertThat("css обложки плохой", cssUrl, endsWith(id + ".css"));
    }

    @Step
    public void shouldSeeCoverInResources(String id){
        if (exists().matches(page.getCoverScript())) {
            String jsUrl = page.getCoverScript().getAttribute("src");
            URI js = fromUri(jsUrl).build();

            assertThat("js обложки плохой", js.getPath(), containsString(id));
        }
    }
}

