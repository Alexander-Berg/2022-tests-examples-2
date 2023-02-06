package ru.yandex.autotests.morda.pages.desktop.tune;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.morda.pages.Morda;
import ru.yandex.autotests.morda.pages.MordaType;
import ru.yandex.autotests.morda.pages.desktop.tune.pages.TuneMainPage;
import ru.yandex.autotests.morda.rules.allure.AllureFeatureRule;
import ru.yandex.autotests.morda.steps.NavigationSteps;
import ru.yandex.autotests.morda.steps.TuneSteps;
import ru.yandex.autotests.mordacommonsteps.rules.MordaAllureBaseRule;
import ru.yandex.autotests.utils.morda.language.Language;
import ru.yandex.autotests.utils.morda.region.Region;
import ru.yandex.geobase.regions.GeobaseRegion;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.List;

import static java.util.Arrays.asList;
import static org.openqa.selenium.remote.DesiredCapabilities.firefox;
import static ru.yandex.autotests.morda.pages.MordaType.TUNE_MAIN;
import static ru.yandex.autotests.utils.morda.region.Region.ASTANA;
import static ru.yandex.autotests.utils.morda.region.Region.KIEV;
import static ru.yandex.autotests.utils.morda.region.Region.MINSK;
import static ru.yandex.autotests.utils.morda.region.Region.MOSCOW;

/**
 * User: asamar
 * Date: 16.08.16
 */
public class TuneMainMorda extends Morda<TuneMainPage> {

    public TuneMainMorda(String scheme, Morda.MordaEnvironment env, Region region, Language language) {
        super(scheme, env);
        setRegion(region);
        setLanguage(language);
    }

    public static TuneMainMorda tune(String scheme, String env, Region region){
        return tune(scheme, env, region, Language.RU);
    }

    public static TuneMainMorda tune(String scheme, String env, Region region, Language language){
        String[] envs = env.split("-");
        if (envs.length == 1) {
            return new TuneMainMorda(scheme,
                    new Morda.MordaEnvironment("www", envs[0], false),
                    region,
                    language);
        } else if (envs.length == 2) {
            return new TuneMainMorda(scheme,
                    new Morda.MordaEnvironment(envs[0], envs[1], false),
                    region,
                    language);
        } else {
            throw new RuntimeException("Bad environment");
        }
    }

    public static List<TuneMainMorda> getDefaultList(String scheme, String env){
        return asList(
                tune(scheme, env, MOSCOW, Language.RU),
                tune(scheme, env, KIEV, Language.UK),
                tune(scheme, env, ASTANA, Language.KK),
                tune(scheme, env, MINSK, Language.BE)
        );
    }

    @Override
    public void initialize(WebDriver driver) {
        NavigationSteps.open(driver, getUrl());
//        TuneSteps.setRegionWithCookie(driver, getCookieDomain(), region);
        TuneSteps.setLanguageWithCookie(driver, getCookieDomain(), language);
    }

    @Override
    public URI getUrl() {
        String env = environment.parseEnvironment();
        if ("www-rc.".equals(env)){
            env = "l7test.";
        }
        return UriBuilder.fromUri("scheme://{env}yandex{domain}/tune/")
                .scheme(scheme)
                .build(env, getDomain(region));
    }

    @Override
    public URI getPassportUrl(String passportEnv) {
        return UriBuilder.fromUri("https://{passportEnv}.yandex{domain}/")
                .build(passportEnv, getDomain(region));
    }

    @Override
    public URI getTuneUrl(String tuneEnv) {
        return UriBuilder.fromUri("scheme://{env}yandex{domain}/tune/")
                .scheme(scheme)
                .build(environment.parseEnvironment(), getDomain(region));
    }

    @Override
    public URI getSerpUrl() {
        return UriBuilder.fromUri("https://yandex{domain}/search").build(getDomain(region));
    }

    @Override
    public String getCookieDomain() {
        return ".yandex" + getDomain(region);
    }

    @Override
    public String getFeature() {
        return "desktop " + getUrl();
    }

    @Override
    public MordaType getMordaType() {
        return TUNE_MAIN;
    }

    @Override
    public MordaAllureBaseRule getRule(){
        return getRule(firefox());
    }

    @Override
    public MordaAllureBaseRule getRule(DesiredCapabilities caps) {
        return new MordaAllureBaseRule(caps)
                .withRule(new AllureFeatureRule(getFeature()));
    }

    public String getDomain(Region region){
        int by = 149;
        int kz = 159;
        int ua = 187;
        List<Integer> parents = new GeobaseRegion(region.getRegionIdInt()).getParentsIds();
        if (parents.contains(by)) {
            return ".by";
        } else if (parents.contains(kz)) {
            return ".kz";
        } else if (parents.contains(ua)) {
            return ".ua";
        }
        return ".ru";
    }

    @Override
    public TuneMainPage getPage(WebDriver driver){
        return new TuneMainPage(driver);
    }

    @Override
    public String toString(){
        return "Tune " + getUrl() + " " + language.getValue();
    }
}
