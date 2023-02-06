package ru.yandex.autotests.morda.pages.spok;

import ru.yandex.autotests.morda.pages.AbstractMorda;
import ru.yandex.autotests.morda.pages.MordaDomain;
import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.pages.MordaWithRegion;
import ru.yandex.geobase.regions.GeobaseRegion;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 20/07/16
 */
public abstract class SpokMorda<T> extends AbstractMorda<T> implements MordaWithRegion<T> {
    protected static final Set<MordaLanguage> AVAILABLE_LANGUAGES =
            new HashSet<>(asList(MordaLanguage.RU));

    protected MordaDomain domain;

    protected SpokMorda(String scheme, String environment, MordaDomain domain) {
        super(scheme, "www", environment);
        this.domain = domain;
    }

    public static List<SpokMorda<?>> getDefaultSpokList(String environment) {
        List<SpokMorda<?>> data = new ArrayList<>();
        data.addAll(DesktopSpokMorda.getDefaultList(environment));
        data.addAll(TouchSpokMorda.getDefaultList(environment));
        return data;
    }

    @Override
    public URI getPassportHost() {
        return UriBuilder.fromUri("https://passport.yandex{domain}/")
                .build(getDomain().getValue());
    }

    @Override
    public URI getTuneHost() {
        return UriBuilder.fromUri("https://tune.yandex{domain}/")
                .build(getDomain().getValue());
    }

    @Override
    public URI getBaseUrl() {
        return UriBuilder.fromUri("scheme://{env}yandex{domain}/")
                .scheme(getScheme())
                .build(getEnvironment(), getDomain().getValue());
    }

    @Override
    public Set<MordaLanguage> getAvailableLanguages() {
        return AVAILABLE_LANGUAGES;
    }

    @Override
    public MordaDomain getDomain() {
        return domain;
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
        return super.toString();
    }
}
