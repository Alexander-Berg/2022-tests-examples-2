package ru.yandex.autotests.mainmorda.steps;

import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.MainPage;
import ru.yandex.autotests.mainmorda.utils.SocialIcon;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.utils.morda.cookie.CookieManager;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import java.util.ArrayList;
import java.util.List;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.hasItem;
import static org.hamcrest.Matchers.isEmptyString;
import static org.hamcrest.Matchers.not;
import static org.junit.Assert.fail;
import static ru.yandex.autotests.mainmorda.blocks.ThemeMenu.SkinMenuItem;
import static ru.yandex.autotests.mainmorda.blocks.ThemeMenu.TabMenuItem;
import static ru.yandex.autotests.mainmorda.data.SkinsData.ALL_SKINS;
import static ru.yandex.autotests.mainmorda.data.SkinsData.ALL_SKIN_GROUPS;
import static ru.yandex.autotests.mainmorda.data.SkinsData.SAVE_SKIN_URL;
import static ru.yandex.autotests.mainmorda.data.SkinsData.SET_SKIN_URL;
import static ru.yandex.autotests.mainmorda.data.SkinsData.THEME_PAGE_URL;
import static ru.yandex.autotests.mainmorda.data.SkinsData.getSkinHrefMatcher;
import static ru.yandex.autotests.mainmorda.data.SkinsData.getSkinSrcMatcher;
import static ru.yandex.autotests.mainmorda.data.SkinsData.getSkinTextMatcher;
import static ru.yandex.autotests.mainmorda.data.SkinsData.getSkinsMap;
import static ru.yandex.autotests.mainmorda.data.SkinsData.getTabTextMatcher;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.ALT;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.SRC;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.TITLE;
import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.exists;

/**
 * User: alex89
 * Date: 22.01.13
 */

public class SkinsSteps {
    private static final Properties CONFIG = new Properties();
    private static final int TIMEOUT = 15000;
    private static final int NUMBER_OF_ATTEMPT = 15;

    private static final String CSS_TYPE = "chrome".equals(CONFIG.getBrowserName()) ? ".webp.css" : ".css";

    private WebDriver driver;
    private CommonMordaSteps userSteps;
    private MainPage mainPage;

    public SkinsSteps(WebDriver driver) {
        this.driver = driver;
        this.userSteps = new CommonMordaSteps(driver);
        this.mainPage = new MainPage(driver);
    }

    @Step
    public void opensThemeMenu() {
        userSteps.opensPage(THEME_PAGE_URL);
        userSteps.shouldSeeElement(mainPage.themeMenu);
    }

    @Step
    public void setSkinWithClick(String skinId) {
        SkinMenuItem skinMenuItem = findSkinInMenu(skinId);
        if (skinMenuItem != null) {
            userSteps.clicksOn(skinMenuItem);
        }
    }

    @Step
    public void setSkinWithUrl(String skinId) {
        driver.get(String.format(SET_SKIN_URL, skinId));
    }

    @Step
    public void savesSkinWithUrl(String skinId) {
        driver.get(String.format(SAVE_SKIN_URL, skinId, CookieManager.getSecretKey(driver)));
    }

    @Step
    public void savesSkinWithUrlWithoutFirstLetterInSK(String skinId) {
        driver.get(String.format(SAVE_SKIN_URL, skinId,
                CookieManager.getSecretKey(driver).substring(1)));
    }

    @Step
    public void savesSkinWithUrlWithoutSK(String skinId) {
        driver.get(String.format(SAVE_SKIN_URL, skinId, ""));
    }

    @Step
    public void savesSkinWithUrlWithRandomSK(String skinId) {
        driver.get(String.format(SAVE_SKIN_URL, skinId,
                CookieManager.md5(String.valueOf(System.nanoTime()))));
    }

    @Step
    public void savesSkinWithUrlWithUnAuthSK(String skinId, String sk) {
        driver.get(String.format(SAVE_SKIN_URL, skinId, sk));
    }

    @Step
    public SkinMenuItem findSkinInMenu(String skinId) {
        for (SkinMenuItem skinMenuItem : mainPage.themeMenu.skinsListInMenu) {
            if (skinMenuItem.getNotation().equals(skinId)) {
                scrollToSkin(skinMenuItem);
                return getSkinFromMenu(skinId);
            }
        }
        fail("Скин не найден: " + skinId);
        return null;
    }

    private void scrollToSkin(SkinMenuItem skin) {
        for (int i = 0; !skin.isDisplayed() && i < NUMBER_OF_ATTEMPT; i++) {
            mainPage.themeMenu.nextButton.click();
            try {
                Thread.sleep(200);
            } catch (InterruptedException ignore) {
            }
        }
    }

    private SkinMenuItem getSkinFromMenu(String skinId) {
        for (SkinMenuItem skinMenuItem : mainPage.themeMenu.skinsListInMenu) {
            if (skinMenuItem.getNotation().equals(skinId)) {
                System.out.println("retVal " + skinMenuItem.getNotation());
                return skinMenuItem;
            }
        }
        fail("Скин не найден: " + skinId);
        return null;
    }

    @Step
    public TabMenuItem findTabInMenu(String groupId) {
        for (TabMenuItem tabMenuItem : mainPage.themeMenu.tabsListInMenu) {
            if (tabMenuItem.getId().equals(groupId)) {
                return tabMenuItem;
            }
        }
        fail("Таб не найден: " + groupId);
        return null;
    }


    @Step
    public void resetSkins() {
        driver.get(THEME_PAGE_URL + "/default/set?sk=" + CookieManager.getSecretKey(driver));
    }

    @Step
    public void shouldSeeSkin(String skinId) {
        String href = mainPage.skinCss.getAttribute("href").split(":")[1];
        List<String> skinNames = getSkinsMap(getSkinsVersion()).get(href);
        assertThat(skinNames, hasItem(equalTo("big/" + skinId + "/_" + skinId + CSS_TYPE)));
    }

    @Step
    public void shouldSeeSkinInBrowser(String skinId, String browser) {
        String href = mainPage.skinCss.getAttribute("href").split(":")[1];
        List<String> skinName = getSkinsMap(getSkinsVersion()).get(href);
        assertThat(skinName, hasItem(equalTo("big/" + skinId + "/_" + skinId + ("chrome".equals(browser) ? ".webp.css" : ".css"))));
    }


    @Step
    public void shouldSeeSkinResources(String skinId) {
        if (exists().matches(mainPage.skinScript)) {
            String src = mainPage.skinScript.getAttribute("src").split(":")[1];
            List<String> skinNames = getSkinsMap(getSkinsVersion()).get(src);
            assertThat(skinNames, hasItem(("big/" + skinId + "/_" + skinId + ".js")));
        }
    }

    @Step
    public void shouldSeeDefaultMordaDesign() {
        assertThat(mainPage.skinCss, not(exists()));
    }

    @Step
    public void shouldSeeSkinInMenuWhenChosen(String skinId) {
        SkinMenuItem skinMenuItem = findSkinInMenu(skinId);
        if (skinId != null) {
            userSteps.shouldSeeElementMatchingTo(skinMenuItem.skinIcon,
                    hasAttribute(ALT, getSkinTextMatcher(skinId)),
                    hasAttribute(TITLE, getSkinTextMatcher(skinId)),
                    hasAttribute(SRC, getSkinSrcMatcher(skinId))
            );
            userSteps.shouldSeeElementWithText(skinMenuItem, getSkinTextMatcher(skinId));
        }
    }

    @Step
    public void shouldSeeSkinInMenuWhenNotChosen(String skinId) {
        SkinMenuItem skinMenuItem = findSkinInMenu(skinId);
        if (skinId != null) {
            userSteps.shouldSeeElementMatchingTo(skinMenuItem.skinIcon,
                    hasAttribute(ALT, getSkinTextMatcher(skinId)),
                    hasAttribute(TITLE, getSkinTextMatcher(skinId)),
                    hasAttribute(SRC, getSkinSrcMatcher(skinId))
            );
            userSteps.shouldSeeElementMatchingTo(skinMenuItem.skinSetUpLink,
                    hasAttribute(HREF, getSkinHrefMatcher(skinId)));
            userSteps.shouldSeeElementWithText(skinMenuItem, isEmptyString());
        }
    }

    @Step
    public void shouldSeeSocialIcons(String skinId) {
        shouldSeeSocialIcon(mainPage.themeMenu.shareBlock.fbIcon, SocialIcon.FACEBOOK, skinId);
        shouldSeeSocialIcon(mainPage.themeMenu.shareBlock.twIcon, SocialIcon.TWITTER, skinId);
        shouldSeeSocialIcon(mainPage.themeMenu.shareBlock.vkIcon, SocialIcon.VK, skinId);
        shouldSeeSocialIcon(mainPage.themeMenu.shareBlock.odnoklIcon, SocialIcon.ODNOKL, skinId);
        shouldSeeSocialIcon(mainPage.themeMenu.shareBlock.moimirlIcon, SocialIcon.MOIMIR, skinId);
    }

    @Step
    public void shouldSeeSocialIcon(HtmlElement socIcon, SocialIcon iconInfo, String skinId) {
        userSteps.shouldSeeElement(socIcon);
        userSteps.shouldSeeElementMatchingTo(socIcon,
                hasAttribute(TITLE, iconInfo.text),
                hasAttribute(HREF, iconInfo.getHrefMatcher(skinId)));
    }

    @Step
    public void shouldSeeTab(String groupId) {
        TabMenuItem tabMenuItem = findTabInMenu(groupId);
        if (tabMenuItem != null) {
            userSteps.shouldSeeElementWithText(tabMenuItem, getTabTextMatcher(groupId));
            userSteps.selectElement(tabMenuItem);
            userSteps.shouldSeeElementIsSelected(tabMenuItem);
            shouldSeeAllSkinsForTab(groupId);
            userSteps.shouldSeeListWithSize(mainPage.themeMenu.skinsListInMenu,
                    equalTo(getGroupThemes(groupId).size()));
        }
    }

    @Step
    public void shouldSeeAllSkinsForTab(String groupId) {
        for (String skin : getGroupThemes(groupId)) {
            findSkinInMenu(skin);
        }
    }

    private List<String> getGroupThemes(String groupId) {
        String[] themesRaw = ALL_SKIN_GROUPS.get(groupId).getThemes().split(",");
        List<String> groupThemes = new ArrayList<>();
        for (String theme : themesRaw) {
            if (ALL_SKINS.contains(theme.trim())) {
                groupThemes.add(theme.trim());
            }
        }
        return groupThemes;
    }

    private String getSkinsVersion() {
        return  (String) ((JavascriptExecutor) driver)
                .executeScript("return JSON.parse(document.getElementsByClassName('page-info')[0].innerHTML).skins");
    }

}

