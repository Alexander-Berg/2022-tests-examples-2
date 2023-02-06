package ru.yandex.autotests.morda.pages.desktop.hwlgV2;

import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.morda.pages.desktop.hwlgV2.blocks.AfishaBlock;
import ru.yandex.autotests.morda.pages.desktop.hwlgV2.blocks.DateTimeBlock;
import ru.yandex.autotests.morda.pages.desktop.hwlgV2.blocks.InfoBlock;
import ru.yandex.autotests.morda.pages.desktop.hwlgV2.blocks.LogoBlock;
import ru.yandex.autotests.morda.pages.desktop.hwlgV2.blocks.MapsBlock;
import ru.yandex.autotests.morda.pages.desktop.hwlgV2.blocks.NewsBlock;
import ru.yandex.autotests.morda.pages.desktop.hwlgV2.blocks.PhotoBlock;
import ru.yandex.autotests.morda.pages.desktop.hwlgV2.blocks.TvBlock;
import ru.yandex.autotests.morda.pages.desktop.hwlgV2.blocks.WeatherBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithAfishaBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithLogo;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithMetroBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithNewsBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithRegionBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithServicesBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithTrafficBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithTvBlock;
import ru.yandex.autotests.morda.pages.interfaces.pages.PageWithWeatherBlock;
import ru.yandex.qatools.htmlelements.loader.HtmlElementLoader;

/**
 * User: asamar
 * Date: 30.10.2015.
 */
public class DesktopHwLgV2Page implements PageWithLogo<LogoBlock>, PageWithWeatherBlock<WeatherBlock>,
        PageWithTvBlock<TvBlock>, PageWithNewsBlock<NewsBlock>, PageWithAfishaBlock<AfishaBlock>,
        PageWithRegionBlock<InfoBlock>, PageWithTrafficBlock<MapsBlock>, PageWithMetroBlock<DateTimeBlock>,
        PageWithServicesBlock<PhotoBlock> {

    private LogoBlock logo;
    private AfishaBlock afisha;
    private DateTimeBlock dateTime;
    private InfoBlock info;
    private MapsBlock maps;
    private NewsBlock news;
    private PhotoBlock photo;
    private TvBlock tv;
    private WeatherBlock weather;

    public DesktopHwLgV2Page(WebDriver driver) {
        HtmlElementLoader.populate(this, driver);
    }

    @Override
    public String toString() {
        return "desktop hw/lg_v2";
    }

    @Override
    public LogoBlock getLogo() {
        return logo;
    }

    @Override
    public WeatherBlock getWeatherBlock() {
        return weather;
    }

    @Override
    public TvBlock getTvBlock() {
        return tv;
    }

    @Override
    public AfishaBlock getAfishaBlock() {
        return afisha;
    }

    @Override
    public NewsBlock getNewsBlock() {
        return news;
    }

    @Override
    public InfoBlock getRegionBlock() {
        return info;
    }

    @Override
    public MapsBlock getTrafficBlock() {
        return maps;
    }

    @Override
    public PhotoBlock getServiceBlock() {
        return photo;
    }

    @Override
    public DateTimeBlock getMetroBlock() {
        return dateTime;
    }
}
