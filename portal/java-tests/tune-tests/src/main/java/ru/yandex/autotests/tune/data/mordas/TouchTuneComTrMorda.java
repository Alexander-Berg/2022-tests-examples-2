package ru.yandex.autotests.tune.data.mordas;

import io.qameta.htmlelements.WebPage;
import io.qameta.htmlelements.WebPageFactory;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.morda.pages.AbstractTouchMorda;
import ru.yandex.autotests.morda.pages.MordaDomain;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.rules.base.MordaBaseWebDriverRule;
import ru.yandex.autotests.morda.steps.TuneSteps;
import ru.yandex.geobase.regions.GeobaseRegion;

import java.util.HashSet;
import java.util.Set;

import static java.util.Collections.singletonList;
import static org.openqa.selenium.remote.DesiredCapabilities.firefox;
import static ru.yandex.autotests.morda.pages.MordaLanguage.TR;
import static ru.yandex.autotests.morda.pages.MordaType.TOUCH_COMTR_TUNE;

/**
 * User: asamar
 * Date: 21.12.16
 */
public class TouchTuneComTrMorda extends TuneMorda<TouchTuneComTrMorda>
        implements AbstractTouchMorda<TouchTuneComTrMorda> {
    private String userAgent;

    protected static final Set<MordaLanguage> AVAILABLE_LANGUAGES =
            new HashSet<>(singletonList(MordaLanguage.TR));

    protected TouchTuneComTrMorda(String scheme,
                                  String prefix,
                                  String environment,
                                  String userAgent,
                                  GeobaseRegion region) {
        super(scheme, prefix, environment);
        region(region);
        language(TR);
        this.userAgent = userAgent;

    }

    public static TouchTuneComTrMorda touchTuneComTr(String userAgent, GeobaseRegion region) {
        return touchTuneComTr("production", userAgent, region);
    }

    public static TouchTuneComTrMorda touchTuneComTr(String environment, String userAgent, GeobaseRegion region) {
        return touchTuneComTr("https", environment, userAgent, region);
    }

    public static TouchTuneComTrMorda touchTuneComTr(String scheme,
                                                     String environment,
                                                     String userAgent,
                                                     GeobaseRegion region) {
        String[] envs = environment.split("-");
        if (envs.length == 1) {
            return new TouchTuneComTrMorda(scheme, "www", envs[0], userAgent, region);
        } else if (envs.length == 2) {
            return new TouchTuneComTrMorda(scheme, envs[0], envs[1], userAgent, region);
        } else {
            throw new RuntimeException("Bad environment");
        }
    }

    @Override
    public MordaDomain getDomain() {
        return MordaDomain.COM_TR;
    }

    @Override
    public Set<MordaLanguage> getAvailableLanguages() {
        return AVAILABLE_LANGUAGES;
    }

    @Override
    public MordaType getMordaType() {
        return TOUCH_COMTR_TUNE;
    }

    @Override
    public TouchTuneComTrMorda me() {
        return this;
    }

    @Override
    public MordaBaseWebDriverRule getRule(DesiredCapabilities caps) {
        return new MordaBaseWebDriverRule(caps)
                .userAgent(userAgent);
    }

    public MordaBaseWebDriverRule getRule() {
        return getRule(firefox());
    }

    @Override
    public <T extends WebPage> T initialize(WebDriver driver, Class<T> clazz) throws InterruptedException {
        WebPageFactory pageObjectFactory = new WebPageFactory();
        T page = pageObjectFactory.get(driver, clazz);
        page.open(getUrl().toString());
        TuneSteps.setRegionWithCookie(driver, getCookieDomain(), getRegion());
        TuneSteps.setLanguageWithCookie(driver, getCookieDomain(), getLanguage());
        return page;
    }
}
