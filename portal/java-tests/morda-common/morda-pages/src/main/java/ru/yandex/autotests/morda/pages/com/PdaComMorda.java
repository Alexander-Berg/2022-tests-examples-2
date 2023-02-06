package ru.yandex.autotests.morda.pages.com;

import ru.yandex.autotests.morda.pages.AbstractPdaMorda;
import ru.yandex.autotests.morda.pages.MordaType;

import java.util.List;
import java.util.stream.Collectors;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class PdaComMorda extends ComMorda<PdaComMorda>
        implements AbstractPdaMorda<PdaComMorda> {

    private PdaComMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
    }

    public static PdaComMorda pdaCom() {
        return pdaCom("production");
    }

    public static PdaComMorda pdaCom(String environment) {
        return pdaCom("https", environment);
    }

    public static PdaComMorda pdaCom(String scheme, String environment) {
        return new PdaComMorda(scheme, "www", environment);
    }

    public static List<PdaComMorda> getDefaultList(String environment) {
        return AVAILABLE_LANGUAGES.stream()
                .map(e -> pdaCom(environment).language(e))
                .collect(Collectors.toList());
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.PDA_COM;
    }

    @Override
    public PdaComMorda me() {
        return this;
    }
}
