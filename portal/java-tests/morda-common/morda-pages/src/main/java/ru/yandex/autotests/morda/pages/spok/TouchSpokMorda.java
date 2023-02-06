package ru.yandex.autotests.morda.pages.spok;

import ru.yandex.autotests.morda.pages.AbstractTouchMorda;
import ru.yandex.autotests.morda.pages.MordaDomain;
import ru.yandex.autotests.morda.pages.MordaType;

import java.util.List;
import java.util.stream.Collectors;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class TouchSpokMorda extends SpokMorda<TouchSpokMorda>
        implements AbstractTouchMorda<TouchSpokMorda> {

    private TouchSpokMorda(String scheme, String environment, MordaDomain domain) {
        super(scheme, environment, domain);
    }

    public static TouchSpokMorda touchSpok(MordaDomain domain) {
        return touchSpok("production", domain);
    }

    public static TouchSpokMorda touchSpok(String environment, MordaDomain domain) {
        return touchSpok("https", environment, domain);
    }

    public static TouchSpokMorda touchSpok(String scheme, String environment, MordaDomain domain) {
        return new TouchSpokMorda(scheme, environment, domain);
    }

    public static List<TouchSpokMorda> getDefaultList(String environment) {
        return MordaDomain.getSpokDomains().stream()
                .filter(e -> e != MordaDomain.MD)
                .map(d -> touchSpok(environment, d))
                .collect(Collectors.toList());
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.DESKTOP_MAIN;
    }

    @Override
    public TouchSpokMorda me() {
        return this;
    }
}
