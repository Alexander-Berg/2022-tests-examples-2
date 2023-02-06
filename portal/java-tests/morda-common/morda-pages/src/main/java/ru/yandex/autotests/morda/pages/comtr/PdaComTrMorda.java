package ru.yandex.autotests.morda.pages.comtr;

import ru.yandex.autotests.morda.pages.AbstractPdaMorda;
import ru.yandex.autotests.morda.pages.MordaType;

import java.util.List;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class PdaComTrMorda extends ComTrMorda<PdaComTrMorda>
        implements AbstractPdaMorda<PdaComTrMorda> {

    private PdaComTrMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
    }

    public static PdaComTrMorda pdaComTr() {
        return pdaComTr("production");
    }

    public static PdaComTrMorda pdaComTr(String environment) {
        return pdaComTr("https", environment);
    }

    public static PdaComTrMorda pdaComTr(String scheme, String environment) {
        return new PdaComTrMorda(scheme, "www", environment);
    }

    public static List<PdaComTrMorda> getDefaultList(String environment) {
        return asList(pdaComTr(environment));
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.PDA_COMTR;
    }

    @Override
    public PdaComTrMorda me() {
        return this;
    }
}
