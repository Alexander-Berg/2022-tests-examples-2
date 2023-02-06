package ru.yandex.autotests.morda.pages.yaru;

import ru.yandex.autotests.morda.pages.AbstractPdaMorda;
import ru.yandex.autotests.morda.pages.MordaType;

import java.util.List;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class PdaYaruMorda extends YaruMorda<PdaYaruMorda>
        implements AbstractPdaMorda<PdaYaruMorda> {

    private PdaYaruMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
    }

    public static PdaYaruMorda pdaYaru() {
        return pdaYaru("production");
    }

    public static PdaYaruMorda pdaYaru(String environment) {
        return pdaYaru("https", environment);
    }

    public static PdaYaruMorda pdaYaru(String scheme, String environment) {
        return new PdaYaruMorda(scheme, "www", environment);
    }

    public static List<PdaYaruMorda> getDefaultList(String environment) {
        return asList(pdaYaru(environment));
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.PDA_YARU;
    }

    @Override
    public PdaYaruMorda me() {
        return this;
    }
}
