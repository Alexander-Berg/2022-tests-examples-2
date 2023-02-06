package ru.yandex.autotests.morda.pages.comtr;

import ru.yandex.autotests.morda.pages.AbstractPdaMorda;
import ru.yandex.autotests.morda.pages.MordaType;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.List;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class PdaComTrAllMorda extends ComTrMorda<PdaComTrAllMorda>
        implements AbstractPdaMorda<PdaComTrAllMorda> {

    private PdaComTrAllMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
    }

    public static PdaComTrAllMorda pdaComTrAll() {
        return pdaComTrAll("production");
    }

    public static PdaComTrAllMorda pdaComTrAll(String environment) {
        return pdaComTrAll("https", environment);
    }

    public static PdaComTrAllMorda pdaComTrAll(String scheme, String environment) {
        return new PdaComTrAllMorda(scheme, "www", environment);
    }

    @Override
    public URI getBaseUrl() {
        return UriBuilder.fromUri(super.getBaseUrl()).path("all").build();
    }

    public static List<PdaComTrAllMorda> getDefaultList(String environment) {
        return asList(pdaComTrAll(environment));
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.PDA_COMTR;
    }

    @Override
    public PdaComTrAllMorda me() {
        return this;
    }
}
