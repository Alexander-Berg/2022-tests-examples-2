package ru.yandex.autotests.morda.pages.desktop.tune;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.desktop.tune.pages.TuneComTrPage;
import ru.yandex.autotests.morda.rules.allure.AllureFeatureRule;
import ru.yandex.autotests.morda.steps.NavigationSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.utils.morda.region.Region;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;

import static org.openqa.selenium.remote.DesiredCapabilities.firefox;
import static ru.yandex.autotests.morda.pages.MordaType.TUNE_COM_TR;
import static ru.yandex.autotests.utils.morda.language.Language.TR;

/**
 * User: asamar
 * Date: 16.08.16
 */
public class TuneComTrMorda extends Morda<TuneComTrPage> {


    public TuneComTrMorda(String scheme, Morda.MordaEnvironment environment) {
        super(scheme, environment);
    }

    public TuneComTrMorda(String scheme, Morda.MordaEnvironment environment, Region region) {
        super(scheme, environment);
        setRegion(region);
        setLanguage(TR);
    }

    public static TuneComTrMorda tuneComTr(String scheme, String env, Region region) {
        String[] envs = env.split("-");
        if (envs.length == 1) {
            return new TuneComTrMorda(scheme,
                    new Morda.MordaEnvironment("www", envs[0], false),
                    region);
        } else if (envs.length == 2) {
            return new TuneComTrMorda(scheme,
                    new Morda.MordaEnvironment(envs[0], envs[1], false),
                    region);
        } else {
            throw new RuntimeException("Bad environment");
        }
    }

//    public static TuneComTrMorda tuneComTr(String scheme, String env){
//        return new TuneComTrMorda(scheme,
//                new Morda.MordaEnvironment("tune", env, false));
//    }

    @Override
    public void initialize(WebDriver driver) {
        NavigationSteps.open(driver, getUrl());
//        TuneSteps.setRegionWithCookie(driver, getCookieDomain(), region);
    }

    public String getDomain() {
        return ".com.tr";
    }

    @Override
    public TuneComTrPage getPage(WebDriver driver) {
        return new TuneComTrPage(driver);
    }

    @Override
    public MordaType getMordaType() {
        return TUNE_COM_TR;
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
