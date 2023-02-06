package ru.yandex.autotests.morda.pages.desktop.com;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.rules.allure.AllureFeatureRule;
import ru.yandex.autotests.morda.steps.NavigationSteps;
import ru.yandex.autotests.morda.steps.TuneSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.Header;
import ru.yandex.autotests.mordacommonsteps.rules.proxy.configactions.HeaderAction;
import ru.yandex.autotests.utils.morda.language.Language;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.HashSet;
import java.util.List;

import static java.util.Arrays.asList;
import static java.util.Collections.singletonList;
import static org.openqa.selenium.remote.DesiredCapabilities.firefox;
import static ru.yandex.autotests.morda.pages.MordaType.D_COM;
import static ru.yandex.autotests.utils.morda.language.Language.EN;
import static ru.yandex.autotests.utils.morda.language.Language.ID;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class DesktopComMorda extends Morda<DesktopComPage> {

    private DesktopComMorda(String scheme, MordaEnvironment environment) {
        this(scheme, environment, EN);
    }

    private DesktopComMorda(String scheme, MordaEnvironment environment, Language language) {
        super(scheme, environment);
        setLanguage(language);
    }

    @Override
    public MordaType getMordaType() {
        return D_COM;
    }

    public static DesktopComMorda desktopCom(String scheme, String environment) {
        return new DesktopComMorda(scheme,
                new MordaEnvironment("www", environment, false)
        );
    }

    public static DesktopComMorda desktopCom(String scheme, String environment, Language language) {
        return new DesktopComMorda(scheme,
                new MordaEnvironment("www", environment, false),
                language
        );
    }

    public static List<DesktopComMorda> getDefaultList(String scheme, String environment) {
        return asList(
                desktopCom(scheme, environment, EN),
                desktopCom(scheme, environment, ID)
        );
    }

    @Override
    public void initialize(WebDriver driver) {
        NavigationSteps.open(driver, getUrl());
        TuneSteps.setLanguageWithCookie(driver, getCookieDomain(), language);
//        TuneSteps.setLanguageNewTune(driver, getUrl(), getCookieDomain(), language);
    }

    @Override
    public MordaAllureBaseRule getRule() {
        return getRule(firefox());
    }


    @Override
    public MordaAllureBaseRule getRule(DesiredCapabilities caps) {
        final String BOSTON_IP = "158.121.51.122";
        List<Header> headers = singletonList(
                new Header("X-Forwarded-For", BOSTON_IP)
//                new Header("No-Redirect", "1")
        );
        return new MordaAllureBaseRule(caps)
                .withRule(new AllureFeatureRule(getFeature()))
                .mergeProxyAction(HeaderAction.class, new HashSet<>(headers));
    }

    @Override
    public DesktopComPage getPage(WebDriver driver) {
        return new DesktopComPage(driver);
    }

    @Override
    public URI getUrl() {
        return UriBuilder.fromUri("scheme://{env}yandex.com/")
                .scheme(scheme)
                .build(environment.parseEnvironment());
    }

    @Override
    public URI getPassportUrl(String passportEnv) {
        return UriBuilder.fromUri("https://{passportEnv}.yandex.com/")
                .build(passportEnv);
    }

    @Override
    public URI getTuneUrl(String tuneEnv) {
        return UriBuilder.fromUri("https://{tuneEnv}.yandex.com/")
                .build(tuneEnv);
    }

    @Override
    public URI getSerpUrl() {
        return UriBuilder.fromUri("https://www.yandex.com/search").build();
    }

    @Override
    public String getCookieDomain() {
        return ".yandex.com";
    }

    @Override
    public String getFeature() {
        return "desktop " + getUrl();
    }

    @Override
    public String toString() {
        return "desktop " + getUrl() + ", " + language;
    }
}
