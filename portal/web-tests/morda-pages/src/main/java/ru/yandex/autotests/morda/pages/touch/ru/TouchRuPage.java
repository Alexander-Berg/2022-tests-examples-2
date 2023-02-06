package ru.yandex.autotests.morda.pages.touch.ru;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithAeroexpressBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithAfishaBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithApplicationsBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithFooter;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithInformers;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithLogo;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithMenuBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithMetroBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithNewsBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithPoiBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithScheduleBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithSearchBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithTeaserBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithTeaserServiceBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithTrafficBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithTvBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithZenBlock;
import ru.yandex.autotests.morda.pages.touch.ru.blocks.AeroexpressBlock;
import ru.yandex.autotests.morda.pages.touch.ru.blocks.AfishaBlock;
import ru.yandex.autotests.morda.pages.touch.ru.blocks.AppsBlock;
import ru.yandex.autotests.morda.pages.touch.ru.blocks.CollectionsBlock;
import ru.yandex.autotests.morda.pages.touch.ru.blocks.EdadealBlock;
import ru.yandex.autotests.morda.pages.touch.ru.blocks.FooterBlock;
import ru.yandex.autotests.morda.pages.touch.ru.blocks.InformersBlock;
import ru.yandex.autotests.morda.pages.touch.ru.blocks.LogoBlock;
import ru.yandex.autotests.morda.pages.touch.ru.blocks.MenuBlock;
import ru.yandex.autotests.morda.pages.touch.ru.blocks.MetroBlock;
import ru.yandex.autotests.morda.pages.touch.ru.blocks.NewsBlock;
import ru.yandex.autotests.morda.pages.touch.ru.blocks.PoiBlock;
import ru.yandex.autotests.morda.pages.touch.ru.blocks.ScheduleBlock;
import ru.yandex.autotests.morda.pages.touch.ru.blocks.SearchBlock;
import ru.yandex.autotests.morda.pages.touch.ru.blocks.SkinGreetingBlock;
import ru.yandex.autotests.morda.pages.touch.ru.blocks.TeaserBlock;
import ru.yandex.autotests.morda.pages.touch.ru.blocks.TeaserServiceBlock;
import ru.yandex.autotests.morda.pages.touch.ru.blocks.TrafficBlock;
import ru.yandex.autotests.morda.pages.touch.ru.blocks.TvBlock;
import ru.yandex.autotests.morda.pages.touch.ru.blocks.ZenBlock;
import ru.yandex.qatools.allure.annotations.Step;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.CheckBox;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

import static ru.yandex.autotests.morda.steps.WebElementSteps.check;
import static ru.yandex.autotests.morda.steps.WebElementSteps.clickOn;
import static ru.yandex.autotests.morda.steps.WebElementSteps.shouldSee;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
public class TouchRuPage implements PageWithSearchBlock<SearchBlock>, PageWithLogo<LogoBlock>,
        PageWithApplicationsBlock<AppsBlock>, PageWithAfishaBlock<AfishaBlock>, PageWithMetroBlock<MetroBlock>,
        PageWithTeaserBlock<TeaserBlock>, PageWithFooter<FooterBlock>, PageWithScheduleBlock<ScheduleBlock>,
        PageWithPoiBlock<PoiBlock>, PageWithTvBlock<TvBlock>, PageWithNewsBlock<NewsBlock>, PageWithAeroexpressBlock<AeroexpressBlock>,
        PageWithTeaserServiceBlock<TeaserServiceBlock>, PageWithZenBlock<ZenBlock>, PageWithTrafficBlock<TrafficBlock>,
        PageWithInformers<InformersBlock>, PageWithMenuBlock<MenuBlock> {

    public TouchRuPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @FindBy(xpath = "//div[contains(@class, 'mheader3__menu')]")
    private HtmlElement menuBlockOpenButton;

    @Name("Css скина")
    @FindBy(xpath = "//link[@rel='stylesheet' and contains(@href, 'skins')]")
    private HtmlElement skinCss;

    @Name("Фон скина")
    @FindBy(xpath = "//div[@class='skin__bg']")
    private HtmlElement skinBackground;


    private SearchBlock searchBlock;
    private LogoBlock logoBlock;
    private AppsBlock appsBlock;
    private AfishaBlock afishaBlock;
    private MetroBlock metroBlock;
    private TeaserBlock teaserBlock;
    private TeaserServiceBlock teaserServiceBlock;
    private FooterBlock footerBlock;
    private ScheduleBlock scheduleBlock;
    private PoiBlock poiBlock;
    private TvBlock tvBlock;
    private NewsBlock newsBlock;
    private AeroexpressBlock aeroexpressBlock;
    private ZenBlock zenBlock;
    private TrafficBlock trafficBlock;
    private InformersBlock informersBlock;
    private MenuBlock menuBlock;
    private Tune tune;
    private CollectionsBlock collectionsBlock;
    private EdadealBlock edadealBlock;

    public EdadealBlock getEdadealBlock() {
        return edadealBlock;
    }

    public CollectionsBlock getCollectionsBlock() {
        return collectionsBlock;
    }

    public SkinGreetingBlock getSkinGreetingBlock() {
        return skinGreetingBlock;
    }

    private SkinGreetingBlock skinGreetingBlock;

    public SearchBlock getSearchBlock() {
        return searchBlock;
    }

    @Override
    public LogoBlock getLogo() {
        return logoBlock;
    }

    @Override
    public AppsBlock getApplicationsBlock() {
        return appsBlock;
    }

    @Override
    public AfishaBlock getAfishaBlock() {
        return afishaBlock;
    }

    @Override
    public MetroBlock getMetroBlock() {
        return metroBlock;
    }

    @Override
    public TeaserBlock getTeaserBlock() {
        return teaserBlock;
    }

    @Override
    public FooterBlock getFooterBlock() {
        return footerBlock;
    }

    @Override
    public ScheduleBlock getScheduleBlock() {
        return scheduleBlock;
    }

    @Override
    public PoiBlock getPoiBlock() {
        return poiBlock;
    }

    @Override
    public TvBlock getTvBlock() {
        return tvBlock;
    }

    @Override
    public NewsBlock getNewsBlock() {
        return newsBlock;
    }

    @Override
    public AeroexpressBlock getAeroexpressBlock() {
        return aeroexpressBlock;
    }

    @Override
    public TeaserServiceBlock getTeaserServiceBlock() {
        return teaserServiceBlock;
    }

    @Override
    public ZenBlock getZenBlock() {
        return zenBlock;
    }

    @Override
    public TrafficBlock getTrafficBlock() {
        return trafficBlock;
    }

    @Override
    public InformersBlock getInformersBlock() {
        return informersBlock;
    }

    @Override
    public MenuBlock getMenuBlock() {
        return menuBlock;
    }

    public HtmlElement getSkinCss() {
        return skinCss;
    }

    public HtmlElement getSkinBackground() {
        return skinBackground;
    }

    public Tune getTune() {
        return tune;
    }


    @Override
    @Step("Open menu")
    public void openMenu() {
        shouldSee(menuBlockOpenButton);
        if (!menuBlock.isDisplayed()) {
            menuBlockOpenButton.click();
        }
    }

    @Override
    @Step("Close menu")
    public void closeMenu() {
//        if (menuBlock.isDisplayed()) {
//            menuBlockOpenButton.click();
//        }
    }

    @Name("Тюн")
    @FindBy(xpath = "//form[contains(@class, 'b-form_action_tune')]")
    public static class Tune extends HtmlElement {

        @Name("Чекбокс \"Не включать тему\"")
        @FindBy(xpath = "//input[@id='mtd']")
        private CheckBox mtdCheckBox;

        @Name("Кнопка \"Сохранить\"")
        @FindBy(xpath = "//input[@class='b-form__submit']")
        private HtmlElement saveButton;

        @Step
        public void switchOffTheme() {
            check(mtdCheckBox);
            clickOn(saveButton);
        }

    }
}
