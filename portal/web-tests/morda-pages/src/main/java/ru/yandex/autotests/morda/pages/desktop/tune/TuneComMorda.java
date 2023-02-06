package ru.yandex.autotests.morda.pages.desktop.tune;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.desktop.tune.pages.TuneComPage;
import ru.yandex.autotests.morda.rules.allure.AllureFeatureRule;
import ru.yandex.autotests.morda.steps.NavigationSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.utils.morda.language.Language;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;

import static org.openqa.selenium.remote.DesiredCapabilities.firefox;
import static ru.yandex.autotests.morda.pages.MordaType.TUNE_COM;
import static ru.yandex.autotests.utils.morda.language.Language.EN;

/**
 * User: asamar
 * Date: 16.08.16
 */
public class TuneComMorda extends Morda<TuneComPage> {

    public TuneComMorda(String scheme, Morda.MordaEnvironment environment, Language language) {
        super(scheme, environment);
        setLanguage(language);
    }

    public static TuneComMorda tuneCom(String scheme, String env){
        String[] envs = env.split("-");
        if (envs.length == 1) {
            return new TuneComMorda(scheme,
                    new Morda.MordaEnvironment("www", envs[0], false),
                    EN);
        } else if (envs.length == 2) {
            return new TuneComMorda(scheme,
                    new Morda.MordaEnvironment(envs[0], envs[1], false),
                    EN);
        } else {
            throw new RuntimeException("Bad environment");
        }

    }

    public String getDomain() {
        return ".com";
    }

    @Override
    public void initialize(WebDriver driver){
        NavigationSteps.open(driver, getUrl());

    }

    @Override
    public TuneComPage getPage(WebDriver driver) {
        return new TuneComPage(driver);
    }

    @Override
    public URI getUrl() {
        String env = environment.parseEnvironment();
        if ("www-rc.".equals(env)){
            env = "l7test.";
        }
        return UriBuilder.fromUri("scheme://{env}yandex{domain}/tune/")
                .scheme(scheme)
                .build(env, getDomain());
    }

    @Override
    public URI getPassportUrl(String passportEnv) {
        return UriBuilder.fromUri("https://{passportEnv}.yandex{domain}/")
                .build(passportEnv, getDomain());
    }

    @Override
    public URI getTuneUrl(String tuneEnv) {
        return UriBuilder.fromUri("scheme://{env}yandex{domain}/tune/")
                .scheme(scheme)
                .build(environment.parseEnvironment(), getDomain());
    }

    @Override
    public URI getSerpUrl() {
        return UriBuilder.fromUri("https://yandex{domain}/search").build(getDomain());
    }

    @Override
    public String getCookieDomain() {
        return ".yandex" + getDomain();
    }

    @Override
    public MordaType getMordaType() {
        return TUNE_COM;
    }

    @Override
    public MordaAllureBaseRule getRule() {
        return getRule(firefox());
    }

    @Override
    public MordaAllureBaseRule getRule(DesiredCapabilities caps) {
        return new MordaAllureBaseRule(caps)
                .withRule(new AllureFeatureRule(getFeature()));
    }

    @Override
    public String getFeature() {
        return "desktop " + getUrl();
    }

    @Override
    public String toString(){
        return "Tune " + getUrl() + " " + language.getValue();
    }
}
