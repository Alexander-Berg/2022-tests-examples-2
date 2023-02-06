package ru.yandex.autotests.tune.data.mordas;

import io.qameta.htmlelements.WebPage;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.DesiredCapabilities;
import ru.yandex.autotests.morda.pages.AbstractMorda;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.rules.base.MordaBaseWebDriverRule;
import ru.yandex.geobase.regions.GeobaseRegion;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;

import static javax.ws.rs.core.UriBuilder.fromUri;

/**
 * User: asamar
 * Date: 28.11.16
 */
public abstract class TuneMorda<T> extends AbstractMorda<T> {
    protected TuneMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
    }

    public abstract MordaBaseWebDriverRule getRule(DesiredCapabilities caps);

    public abstract MordaBaseWebDriverRule getRule();


    public abstract <E extends WebPage> E initialize(WebDriver driver, Class<E> clazz) throws InterruptedException;

    @Override
    public URI getBaseUrl() {
        return UriBuilder.fromUri("scheme://yandex{domain}/")
                .scheme(getScheme())
                .build(getDomain().getValue());
    }

    @Override
    public URI getUrl() {
        String env = getEnvironment();
        if ("www-rc.".equals(env)){
            env = "l7test.";
        }

        return UriBuilder.fromUri("scheme://{env}yandex{domain}/tune/")
                .scheme(getScheme())
                .build(env, getDomain().getValue());
    }

    @Override
    public URI getPassportHost() {
        return UriBuilder.fromUri("https://passport.yandex{domain}/")
                .build(getDomain().getValue());
    }

    @Override
    public URI getTuneHost() {
        return UriBuilder.fromUri("scheme://{env}yandex{domain}/tune/")
                .scheme(getScheme())
                .build(getEnvironment(), getDomain().getValue());
    }

    @Override
    public T language(MordaLanguage language) {
        return super.language(language);
    }

    @Override
    public T region(GeobaseRegion region) {
        return super.region(region);
    }

    @Override
    public GeobaseRegion getRegion() {
        return super.getRegion();
    }

    @Override
    public String toString() {
        return super.toString() + " " + getRegion() + " " + getLanguage();
    }

    public String getCookieDomain() {
        return ".yandex" + getDomain().getValue();
    }

    public URI advPageUrl() {
        return fromUri(getUrl()).path("adv").build();
    }

    public URI geoPageUrl() {
        return fromUri(getUrl()).path("geo").build();
    }

    public URI placesPageUrl() {
        return fromUri(getUrl()).path("places").build();
    }

    public URI languagePageUrl() {
        return fromUri(getUrl()).path("lang").build();
    }

    public URI searchPageUrl() {
        return fromUri(getUrl()).path("search").build();
    }

    public URI commonPageUrl() {
        return fromUri(getUrl()).path("common").build();
    }

}
