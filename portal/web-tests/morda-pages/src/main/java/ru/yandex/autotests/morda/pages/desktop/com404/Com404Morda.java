package ru.yandex.autotests.morda.pages.desktop.com404;

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
import static ru.yandex.autotests.utils.morda.language.Language.EN;
import static ru.yandex.autotests.utils.morda.language.Language.ID;

/**
 * User: asamar
 * Date: 06.10.2015.
 */
public class Com404Morda extends Morda<Com404Page> {

    private Com404Morda(String scheme, MordaEnvironment environment) {
        this(scheme, environment, EN);
    }

    private Com404Morda(String scheme, MordaEnvironment environment, Language language) {
        super(scheme, environment);
        setLanguage(language);
    }

    public static Com404Morda com404(String scheme, String environment, Language language){
        return new Com404Morda(scheme,
                new MordaEnvironment("www", environment, false),
                language
        );
    }

    public static Com404Morda com404(String scheme, String environment){
        return new Com404Morda(scheme,
                new MordaEnvironment("www", environment, false)
        );
    }

    public static List<Com404Morda> getDefaultList(String scheme, String environment) {
        return asList(
                com404(scheme, environment, EN),
                com404(scheme, environment, ID)
        );
    }

    @Override
    public void initialize(WebDriver driver) {
        NavigationSteps.open(driver, getUrl());
        TuneSteps.setLanguageWithCookie(driver, getCookieDomain(), language);
//        TuneSteps.setLanguageNewTune(driver, getUrl(), getCookieDomain(), language);

    }

    @Override
    public MordaType getMordaType() {
        return MordaType.D_COM_404;
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
    public Com404Page getPage(WebDriver driver) {
        return new Com404Page(driver);
    }

    @Override
    public URI getUrl() {
        return UriBuilder.fromUri("scheme://{env}yandex{tld}/sl/blah")
                .scheme(scheme)
                .build(environment.parseEnvironment(), ".com");
    }

    @Override
    public URI getPassportUrl(String passportEnv) {
        return UriBuilder.fromUri("https://{passportEnv}.yandex{tld}/")
                .build(passportEnv, ".com");
    }

    @Override
    public URI getTuneUrl(String tuneEnv) {
        return UriBuilder.fromUri("https://{tuneEnv}.yandex{tld}/")
                .build(tuneEnv, ".com");
    }

    @Override
    public URI getSerpUrl() {
        return UriBuilder.fromUri("https://yandex.com/search").build();
    }

    @Override
    public String getCookieDomain() {
        return String.format(".yandex%s", ".com");
    }

    @Override
    public String getFeature() {
        return "desktop 404 " + getUrl();
    }

    @Override
    public String toString(){
        return  "desktop 404 com " + getUrl() + " " + language;
    }
}
