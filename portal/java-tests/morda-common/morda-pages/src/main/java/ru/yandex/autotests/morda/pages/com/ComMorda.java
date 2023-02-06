package ru.yandex.autotests.morda.pages.com;

import ru.yandex.autotests.morda.pages.MordaLanguage;
import ru.yandex.autotests.morda.pages.AbstractMorda;
import ru.yandex.autotests.morda.pages.MordaDomain;
import ru.yandex.autotests.morda.pages.MordaWithLanguage;

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
public abstract class ComMorda<T> extends AbstractMorda<T>
        implements MordaWithLanguage<T> {

    protected static final Set<MordaLanguage> AVAILABLE_LANGUAGES =
            new HashSet<>(asList(MordaLanguage.EN, MordaLanguage.ID));
    private static final URI PASSPORT_HOST = URI.create("https://passport.yandex.com/");
    private static final URI TUNE_HOST = URI.create("https://tune.yandex.com/");

    protected ComMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
        header("No-Redirect","1");
        language(MordaLanguage.EN);
    }

    public static List<ComMorda<?>> getDefaultComList(String environment) {
        List<ComMorda<?>> data = new ArrayList<>();
        data.addAll(DesktopCom404Morda.getDefaultList(environment));
        data.addAll(DesktopComMorda.getDefaultList(environment));
        data.addAll(PdaComMorda.getDefaultList(environment));
        data.addAll(TouchComMorda.getDefaultList(environment));
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
        return MordaDomain.COM;
    }

    @Override
    public Set<MordaLanguage> getAvailableLanguages() {
        return AVAILABLE_LANGUAGES;
    }

    @Override
    public T language(MordaLanguage language) {
        return super.language(language);
    }

    @Override
    public String toString() {
        return super.toString() + " " + getLanguage();
    }
}
