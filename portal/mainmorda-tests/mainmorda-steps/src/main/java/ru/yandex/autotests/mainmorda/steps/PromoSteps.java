package ru.yandex.autotests.mainmorda.steps;

import org.openqa.selenium.Cookie;
import org.openqa.selenium.WebDriver;
import ru.yandex.autotests.mainmorda.Properties;
import ru.yandex.autotests.mainmorda.pages.BasePage;
import ru.yandex.qatools.allure.annotations.Step;

import static org.hamcrest.CoreMatchers.containsString;
import static org.hamcrest.CoreMatchers.equalTo;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.notNullValue;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;
import static org.junit.Assume.assumeFalse;
import static ru.yandex.autotests.mainmorda.data.PromoData.YABS_HREF_PATTERN;
import static ru.yandex.autotests.mordacommonsteps.matchers.RegexMatcher.matches;
import static ru.yandex.autotests.mordacommonsteps.utils.HtmlAttribute.HREF;
import static ru.yandex.autotests.utils.morda.url.Domain.KZ;
import static ru.yandex.autotests.utils.morda.url.Domain.UA;
import static ru.yandex.qatools.htmlelements.matchers.common.DoesElementExistMatcher.exists;

/**
 * User: alex89
 * Date: 10.12.12
 */

public class PromoSteps {
    private static final Properties CONFIG = new Properties();

    private WebDriver driver;
    private BasePage basePage;

    public PromoSteps(WebDriver driver) {
        this.driver = driver;
        this.basePage = new BasePage(driver);
    }

    @Step
    public void shouldSeeThatPromoLinkAndImageHaveSameYabsHref() {
        String teaserHeaderHref = basePage.teaserBlock.promoLink.getAttribute(HREF.getValue());
        String teaserImageHref = basePage.teaserBlock.promoImageLink.getAttribute(HREF.getValue());
        assertThat("href изображения и текста тизера различны!", teaserHeaderHref, equalTo(teaserImageHref));
        assertTrue("href тизера некорректен: " + teaserHeaderHref, teaserHeaderHref.matches(YABS_HREF_PATTERN));
    }

    @Step
    public void shouldSeeYabsFrequencyCookie() {
        Cookie yfCookie = driver.manage().getCookieNamed("yabs-frequency");
        assertThat("Кука yabs-frequency отсутствует", yfCookie, notNullValue());
        assertThat("Кука yabs-frequency имеет неправильный формат", yfCookie.getValue(), matches("/\\d/\\d+/[^/]+/"));
    }

    //Шаги баннера
    @Step
    public void triesToNoticeBanner() {
        excludeDomain();
        for (int i = 0; i < 5; i++) {
            driver.get(driver.getCurrentUrl());
            if (exists().matches(basePage.banner)) {
                return;
            }
        }
        fail("Баннер не показался после 5 перезагрузок страницы");
    }

    @Step
    public void triesToNoticeVerticalBanner() {
        excludeDomain();
        for (int i = 0; i < 5; i++) {
            driver.get(driver.getCurrentUrl());
            if (exists().matches(basePage.verticalBanner.flashObject)) {
                return;
            }
        }
        fail("Баннер не показался после 5 перезагрузок страницы");
    }

    @Step("Should see adt_id {0} on awaps page")
    public void shouldSeeAdtIdOnAwapsPage(String s) {
        assertThat("В ответе awaps нет id " + s, driver.getPageSource(), containsString(s));
    }

    private void excludeDomain() {
        assumeFalse("Для домена " + CONFIG.getBaseDomain() + " баннер может и не показываться",
                CONFIG.domainIs(UA) || CONFIG.domainIs(KZ));
    }
}