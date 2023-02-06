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

import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static java.util.Arrays.asList;
import static org.openqa.selenium.remote.DesiredCapabilities.firefox;
import static ru.yandex.autotests.morda.pages.MordaLanguage.EN;
import static ru.yandex.autotests.morda.pages.MordaLanguage.ID;
import static ru.yandex.autotests.morda.pages.MordaType.TOUCH_COM_TUNE;

/**
 * User: asamar
 * Date: 21.12.16
 */
public class TouchTuneComMorda extends TuneMorda<TouchTuneComMorda>
        implements AbstractTouchMorda<TouchTuneComMorda> {
    private String userAgent;

    private static final Set<MordaLanguage> AVAILABLE_LANGUAGES =
            new HashSet<>(asList(MordaLanguage.EN, MordaLanguage.ID));

    private TouchTuneComMorda(String scheme, String prefix, String environment, String userAgent, MordaLanguage lang) {
        super(scheme, prefix, environment);
        language(lang);
        this.userAgent = userAgent;
    }

    public static TouchTuneComMorda touchTuneCom(String userAgent, MordaLanguage lang) {
        return touchTuneCom("production", userAgent, lang);
    }

    public static TouchTuneComMorda touchTuneCom(String environment, String userAgent, MordaLanguage lang) {
        return touchTuneCom("https", environment, userAgent, lang);
    }

    public static TouchTuneComMorda touchTuneCom(String scheme,
                                                 String environment,
                                                 String userAgent,
                                                 MordaLanguage lang) {
        String[] envs = environment.split("-");
        if (envs.length == 1) {
            return new TouchTuneComMorda(scheme, "www", envs[0], userAgent, lang);
        } else if (envs.length == 2) {
            return new TouchTuneComMorda(scheme, envs[0], envs[1], userAgent, lang);
        } else {
            throw new RuntimeException("Bad environment");
        }
    }

    public static List<? extends TuneMorda> getDefaultList(String scheme, String environment, String userAgent) {
        return asList(
                touchTuneCom(scheme, environment, userAgent, EN),
                touchTuneCom(scheme, environment, userAgent, ID)
        );
    }

    @Override
    public MordaDomain getDomain() {
        return MordaDomain.COM;
    }

    @Override
    public Set<MordaLanguage> getAvailableLanguages() {
        return AVAILABLE_LANGUAGES;
    }

    @Override
    public MordaType getMordaType() {
        return TOUCH_COM_TUNE;
    }

    @Override
    public TouchTuneComMorda me() {
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
        TuneSteps.setLanguageWithCookie(driver, getCookieDomain(), getLanguage());
        return page;
    }

    @Override
    public String toString() {
        return getMordaType().name().toLowerCase() + " \"" + getUrl() + "\"" + " " + getLanguage();
    }
}
