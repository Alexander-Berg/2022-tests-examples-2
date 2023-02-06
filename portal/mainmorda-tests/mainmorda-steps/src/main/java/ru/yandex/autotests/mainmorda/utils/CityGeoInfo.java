package ru.yandex.autotests.mainmorda.utils;

import org.hamcrest.Matcher;
import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mordacommonsteps.utils.LinkInfo;
import ru.yandex.autotests.utils.morda.region.Region;

import java.util.List;

import static org.hamcrest.Matchers.endsWith;
import static org.hamcrest.Matchers.isEmptyOrNullString;
import static org.hamcrest.Matchers.startsWith;
import static ru.yandex.autotests.mainmorda.data.GeoIconsData.GeoRandomIcons;
import static ru.yandex.autotests.mordacommonsteps.matchers.HtmlAttributeMatcher.hasAttribute;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;

/**
 * User: ivannik
 * Date: 04.06.13
 * Time: 19:37
 * <p/>
 * Содержит информацию о сервисах в геоблоке (Регион, список сервисов, отображаемых иконками, список сервисов,
 * отображаемых ссылками)
 */
public class CityGeoInfo {
    public final Region region;
    public final List<GeoIconInfo> iconList;
    public final List<LinkInfo> linkList;

    public CityGeoInfo(Region region,
                       List<GeoIconInfo> iconList,
                       List<LinkInfo> linkList) {
        this.region = region;
        this.iconList = iconList;
        this.linkList = linkList;
    }

    public Region getRegion() {
        return region;
    }

    @Override
    public String toString() {
        return region.toString();
    }

    public static class GeoIconInfo {
        public GeoIconType dataType;
        public Matcher<String> iconUrl;
        public Matcher<String> iconHref;
        public String randomIconPattern;

        public GeoIconInfo(GeoIconType dataType, Matcher<String> iconHref, Matcher<String> iconUrl) {
            this.dataType = dataType;
            this.iconHref = iconHref;
            this.iconUrl = iconUrl;
        }

        public GeoIconInfo(GeoIconType dataType, String randomIconPattern) {
            this.dataType = dataType;
            this.randomIconPattern = randomIconPattern;
            this.iconHref = endsWith(randomIconPattern);
            this.iconUrl = endsWith(randomIconPattern);
        }

        public LinkInfo getLink() {
            return new LinkInfo(isEmptyOrNullString(), iconUrl, hasAttribute(HREF, iconHref));
        }

        public void updateRandomIconMatchers(WebDriver driver, GeoRandomIcons icon) {
            iconUrl = startsWith(icon.getUrlPattern(driver) + randomIconPattern);
            iconHref = startsWith(icon.getUrlPattern(driver) + randomIconPattern);
        }

        @Override
        public String toString() {
            return dataType.toString();
        }
    }
}
