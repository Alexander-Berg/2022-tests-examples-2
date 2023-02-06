package ru.yandex.autotests.morda.pages.comtr;

import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.pages.AbstractMorda;
import ru.yandex.autotests.morda.pages.MordaDomain;
import ru.yandex.autotests.morda.pages.MordaWithRegion;
import ru.yandex.geobase.regions.GeobaseRegion;
import ru.yandex.geobase.regions.Turkey;

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
public abstract class ComTrMorda<T> extends AbstractMorda<T>
        implements MordaWithRegion<T> {

    private static final Set<MordaLanguage> AVAILABLE_LANGUAGES =
            new HashSet<>(asList(MordaLanguage.TR));
    private static final URI PASSPORT_HOST = URI.create("https://passport.yandex.com.tr/");
    private static final URI TUNE_HOST = URI.create("https://tune.yandex.com.tr/");

    protected ComTrMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
        region(Turkey.ISTANBUL_11508);
    }

    public static List<ComTrMorda<?>> getDefaultComTrList(String environment) {
        List<ComTrMorda<?>> data = new ArrayList<>();
        data.addAll(DesktopComTrAllMorda.getDefaultList(environment));
        data.addAll(DesktopComTrFootballMorda.getDefaultList(environment));
        data.addAll(DesktopComTrMorda.getDefaultList(environment));
        data.addAll(DesktopFamilyComTrMorda.getDefaultList(environment));
        data.addAll(TouchComTrAllMorda.getDefaultList(environment));
        data.addAll(TouchComTrMorda.getDefaultList(environment));
        data.addAll(TouchComTrWpMorda.getDefaultList(environment));
        data.addAll(PdaComTrMorda.getDefaultList(environment));
        data.addAll(PdaComTrAllMorda.getDefaultList(environment));
        return data;
    }

    @Override
    public URI getPassportHost() {
        return PASSPORT_HOST;
    }

    @Override
    public URI getTuneHost() {
        return TUNE_HOST;
    }

    @Override
    public URI getBaseUrl() {
        return UriBuilder.fromUri("scheme://{env}yandex{domain}/")
                .scheme(getScheme())
                .build(getEnvironment(), getDomain().getValue());
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
    public T region(GeobaseRegion region) {
        return super.region(region);
    }

    @Override
    public GeobaseRegion getRegion() {
        return super.getRegion();
    }

    @Override
    public String toString() {
        return super.toString() + " " + getRegion();
    }
}
