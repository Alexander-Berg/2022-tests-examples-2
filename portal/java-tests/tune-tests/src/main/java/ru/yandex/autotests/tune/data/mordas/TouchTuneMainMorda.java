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

import java.util.Collection;
import java.util.HashSet;
import java.util.Set;

import static java.util.Arrays.asList;
import static org.openqa.selenium.remote.DesiredCapabilities.firefox;
import static ru.yandex.autotests.morda.pages.MordaLanguage.BE;
import static ru.yandex.autotests.morda.pages.MordaLanguage.KK;
import static ru.yandex.autotests.morda.pages.MordaLanguage.RU;
import static ru.yandex.autotests.morda.pages.MordaLanguage.UK;
import static ru.yandex.autotests.morda.pages.MordaType.TOUCH_TUNE;
import static ru.yandex.geobase.regions.Belarus.MINSK;
import static ru.yandex.geobase.regions.Kazakhstan.ASTANA;
import static ru.yandex.geobase.regions.Russia.MOSCOW;
import static ru.yandex.geobase.regions.Ukraine.KYIV;

/**
 * User: asamar
 * Date: 28.11.16
 */
public class TouchTuneMainMorda extends TuneMorda<TouchTuneMainMorda>
        implements AbstractTouchMorda<TouchTuneMainMorda> {

    private static final Set<MordaLanguage> AVAILABLE_LANGUAGES =
            new HashSet<>(asList(MordaLanguage.RU, MordaLanguage.BE, MordaLanguage.KK, MordaLanguage.UK, MordaLanguage.TT));

    private String userAgent;

    private TouchTuneMainMorda(String scheme, String prefix, String environment, String userAgent) {
        super(scheme, prefix, environment);
        this.userAgent = userAgent;
    }

    public static TouchTuneMainMorda touchTuneMain(String userAgent) {
        return touchTuneMain("production", userAgent);
    }

    public static TouchTuneMainMorda touchTuneMain(String environment, String userAgent) {
        return touchTuneMain("https", environment, userAgent);
    }

    public static TouchTuneMainMorda touchTuneMain(String scheme, String environment, String userAgent) {
        String[] envs = environment.split("-");
        if (envs.length == 1) {
            return new TouchTuneMainMorda(scheme, "www", envs[0], userAgent);
        } else if (envs.length == 2) {
            return new TouchTuneMainMorda(scheme, envs[0], envs[1], userAgent);
        } else {
            throw new RuntimeException("Bad environment");
        }
    }

    public static Collection<? extends TuneMorda> getDefaultList(String scheme, String environment, String userAgent) {
        return asList(
                touchTuneMain(scheme, environment, userAgent).region(MOSCOW).language(RU),
                touchTuneMain(scheme, environment, userAgent).region(KYIV).language(UK),
                touchTuneMain(scheme, environment, userAgent).region(ASTANA).language(KK),
                touchTuneMain(scheme, environment, userAgent).region(MINSK).language(BE)
        );
    }

    @Override
    public MordaDomain getDomain() {
        return MordaDomain.fromString(getRegion().getKubrDomain());
    }

    @Override
    public Set<MordaLanguage> getAvailableLanguages() {
        return AVAILABLE_LANGUAGES;
    }

    @Override
    public MordaType getMordaType() {
        return TOUCH_TUNE;
    }

    @Override
    public TouchTuneMainMorda me() {
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
//        TuneSteps.setRegionWithCookie(driver, getCookieDomain(), getRegion());
        TuneSteps.setLanguageWithCookie(driver, getCookieDomain(), getLanguage());
        return page;
    }
}
