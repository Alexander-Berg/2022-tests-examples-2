package ru.yandex.autotests.mainmorda.steps;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mainmorda.blocks.GeoBlock;
import ru.yandex.autotests.mainmorda.pages.BasePage;
import ru.yandex.autotests.mainmorda.utils.GeoIconType;
import ru.yandex.autotests.mordacommonsteps.steps.CommonMordaSteps;
import ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.element.HtmlElement;

import static org.junit.Assert.fail;
import static ru.yandex.autotests.mainmorda.blocks.PageBlock.GEO;
import static ru.yandex.autotests.mainmorda.data.GeoIconsData.GeoRandomIcons;
import static ru.yandex.autotests.mainmorda.utils.CityGeoInfo.GeoIconInfo;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 02.04.13
 */
public class GeoIconsSteps {
    private WebDriver driver;
    private CommonMordaSteps userSteps;
    private BasePage basePage;
    private LinksSteps userLink;

    public GeoIconsSteps(WebDriver driver) {
        this.driver = driver;
        this.userSteps = new CommonMordaSteps(driver);
        this.basePage = new BasePage(driver);
        this.userLink = new LinksSteps(driver);
    }

    @Step
    public void shouldSeeIcon(GeoIconInfo info) {
        GeoBlock.GeoIcon item;
        if (info.dataType.equals(GeoIconType.RANDOM)) {
            item = findRandomGeoIconOnPage(info);
        } else {
            item = findGeoIconOnPage(info);
        }
        userLink.shouldSeeLink(item, info.getLink(), GEO);
    }

    @Step
    public void shouldSeeGeoLink(LinkInfo link) {
        HtmlElement item = findGeoLink(link);
        userLink.shouldSeeLink(item, link, GEO);
    }

    @Step
    public GeoBlock.GeoIcon findGeoIconOnPage(GeoIconInfo info) {
        for (GeoBlock.GeoIcon item : basePage.geoBlock.allIcons) {
            String currentType = item.icon.getAttribute(HtmlAttribute.CLASS.toString());
            if (currentType.contains(info.dataType.toString())) {
                return item;
            }
        }
        fail("Иконка типа " + info.dataType + " потерялась");
        return null;
    }

    @Step
    public GeoBlock.GeoIcon findRandomGeoIconOnPage(GeoIconInfo info) {
        for (GeoBlock.GeoIcon item : basePage.geoBlock.allIcons) {
            GeoRandomIcons icon = GeoRandomIcons.getIcon(item.icon.getAttribute(HtmlAttribute.CLASS.toString()));
            if (icon != null) {
                info.updateRandomIconMatchers(driver, icon);
                return item;
            }
        }
        fail("меняющаяся иконка не найдена");
        return null;
    }

    @Step
    public HtmlElement findGeoLink(LinkInfo link) {
        for (HtmlElement item : basePage.geoBlock.allPermanentLinks) {
            String currentText = item.getText();
            System.out.println(currentText);
            if (link.text.matches(currentText)) {
                System.out.println(item.getAttribute("href"));
                return item;
            }
        }
        fail("Ссылка " + link.text + " потерялась или переименовалась");
        return new HtmlElement();
    }
}
