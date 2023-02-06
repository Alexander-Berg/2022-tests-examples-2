package ru.yandex.autotests.morda.pages.desktop.main;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.FindBy;
import ru.yandex.autotests.morda.pages.desktop.main.blocks.*;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.EditModeControls;
import ru.yandex.autotests.morda.pages.desktop.main.htmlelements.Widget;
import ru.yandex.autotests.morda.pages.desktop.main.widgets.SkinsBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.*;
import ru.yandex.qatools.htmlelements.annotations.Name;
import ru.yandex.qatools.htmlelements.element.HtmlElement;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

import java.util.List;

import static ru.yandex.qatools.htmlelements.matchers.WrapsElementMatchers.exists;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 26/02/15
 */
public class DesktopMainPage implements PageWithSearchBlock<SearchBlock>, PageWithLogo<LogoBlock>,
        PageWithSetHomeBlock<SetHomeBlock>, PageWithFooter<FooterBlock>, PageWithWeatherBlock<WeatherBlock>,
        PageWithRegionBlock<RegionBlock>, PageWithServicesBlock<ServicesBlock>, PageWithTeaserBlock<TeaserBlock>,
        PageWithTvBlock<TvBlock>, PageWithAfishaBlock<AfishaBlock>, PageWithNewsBlock<TopnewsBlock>,
        PageWithTrafficBlock<TrafficBlock>, PageWithHeader<HeaderBlock>, PageWithSkinsBlock<SkinsBlock> {

    @Name("Элементы с BADID")
    @FindBy(xpath = "//*[contains(@onmousedown, 'BADID')]")
    public List<HtmlElement> elementsWithBadId;
    @Name("Сбросить настройки")
    @FindBy(xpath = "//button[contains(@class, 'catalog__reset')]")
    public HtmlElement resetButton;

    private Banner banner;
    private SearchBlock searchBlock;
    private LogoBlock logoBlock;
    private SetHomeBlock setHomeBlock;
    private FooterBlock footerBlock;
    private WeatherBlock weatherBlock;
    private RegionBlock regionBlock;
    private ServicesBlock servicesBlock;
    private TeaserBlock teaserBlock;
    private TvBlock tvBlock;
    private AfishaBlock afishaBlock;
    private TopnewsBlock topnewsBlock;
    private TrafficBlock trafficBlock;
    private HeaderBlock headerBlock;
    private SkinsBlock skinsBlock;
    private EditModeControls editModeControls;
    private RssBlock rssBlock;
    private RatesBlock ratesBlock;
    private EtrainsBlock etrainsBlock;

    @Name("Виджеты")
    @FindBy(xpath = "//div[contains(@id, 'wd-wrapper-') " +
            "and not(contains(@class, 'widget_mode_hidden')) " +
            "and not(contains(@class, 'widget_removed_yes'))]")
    private List<Widget> widgets;

    @Name("Добавляемый виджет")
    @FindBy(xpath = "//div[contains(@id, 'wd-wrapper-') " +
            "and contains(@class, 'widget_state_add')]")
    private Widget widgetBeingAdded;

    @Name("Css скина")
    @FindBy(xpath = "//link[@rel='stylesheet' and contains(@href, 'skins')]")
    private HtmlElement skinCss;

    @Name("Script скина")
    @FindBy(xpath = "//script[contains(@src, 'skins')]")
    private HtmlElement skinScript;

    @Name("Css обложки")
    @FindBy(xpath = "//link[@rel='stylesheet' and contains(@href, 'covers')]")
    private HtmlElement coverCss;

    @Name("Script обложки")
    @FindBy(xpath = "//script[contains(@src, 'covers') and not(contains(@src, 'settings.js'))]")
    private HtmlElement coverScript;

    @FindBy(xpath = "//meta[@name='yamm']")
    private HtmlElement yamm;

    public DesktopMainPage(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    public List<HtmlElement> getElementsWithBadId() {
        return elementsWithBadId;
    }

    public SearchBlock getSearchBlock() {
        return searchBlock;
    }

    public RatesBlock getRatesBlock() {
        return ratesBlock;
    }

    public EtrainsBlock getEtrainsBlock() {
        return etrainsBlock;
    }

    public HtmlElement getCoverScript() {
        return coverScript;
    }

    public HtmlElement getCoverCss() {
        return coverCss;
    }

    @Override
    public LogoBlock getLogo() {
        return logoBlock;
    }

    @Override
    public SetHomeBlock getSetHomeBlock() {
        return setHomeBlock;
    }

    @Override
    public FooterBlock getFooterBlock() {
        return footerBlock;
    }

    @Override
    public WeatherBlock getWeatherBlock() {
        return weatherBlock;
    }

    @Override
    public RegionBlock getRegionBlock() {
        return regionBlock;
    }

    @Override
    public ServicesBlock getServiceBlock() {
        return servicesBlock;
    }

    @Override
    public TeaserBlock getTeaserBlock() {
        return teaserBlock;
    }

    @Override
    public TvBlock getTvBlock() {
        return tvBlock;
    }

    @Override
    public AfishaBlock getAfishaBlock() {
        return afishaBlock;
    }

    @Override
    public TopnewsBlock getNewsBlock() {
        return topnewsBlock;
    }

    @Override
    public TrafficBlock getTrafficBlock() {
        return trafficBlock;
    }

    @Override
    public HeaderBlock getHeaderBlock() {
        return headerBlock;
    }

    public List<Widget> getWidgets() {
        return widgets;
    }

    public Widget getWidgetBeingAdded() {
        return widgetBeingAdded;
    }

    public RssBlock getRssBlock() {
        return rssBlock;
    }

    public EditModeControls getEditModeControls() {
        return editModeControls;
    }

    public Mode getMode() {
        if (exists().matches(yamm)) {
            return Mode.getMode(yamm.getAttribute("content"));
        }

        throw new IllegalStateException("Meta yamm not found");
    }

    @Override
    public SkinsBlock getSkinsBlock() {
        return skinsBlock;
    }

    public HtmlElement getSkinCss() {
        return skinCss;
    }

    public HtmlElement getSkinScript() {
        return skinScript;
    }

    public Banner getBanner() {
        return banner;
    }

    public enum Mode {
        PLAIN("p"),
        EDIT("e"),
        WIDGET("w"),
        FAKE("f");

        private String value;

        Mode(String value) {
            this.value = value;
        }

        public static Mode getMode(String mode) {
            for (Mode m : Mode.values()) {
                if (m.value.equals(mode)) {
                    return m;
                }
            }

            throw new IllegalArgumentException("Unknown mode \"" + mode + "\"");
        }
    }
}
