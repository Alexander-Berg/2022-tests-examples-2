package ru.yandex.autotests.morda.pages.comtr;

import ru.yandex.autotests.morda.pages.AbstractTouchMorda;
import ru.yandex.autotests.morda.pages.MordaType;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;
import java.util.List;

import static java.util.Arrays.asList;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 27/02/15
 */
public class TouchComTrAllMorda extends ComTrMorda<TouchComTrAllMorda>
        implements AbstractTouchMorda<TouchComTrAllMorda> {

    private TouchComTrAllMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
    }

    public static TouchComTrAllMorda touchComTrAll() {
        return touchComTrAll("production");
    }

    public static TouchComTrAllMorda touchComTrAll(String environment) {
        return touchComTrAll("https", environment);
    }

    public static TouchComTrAllMorda touchComTrAll(String scheme, String environment) {
        return new TouchComTrAllMorda(scheme, "www", environment);
    }

    public static List<TouchComTrAllMorda> getDefaultList(String environment) {
        return asList(touchComTrAll(environment));
    }

    @Override
    public URI getBaseUrl() {
        return UriBuilder.fromUri(super.getBaseUrl()).path("all").build();
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.TOUCH_COMTR_ALL;
    }

    @Override
    public TouchComTrAllMorda me() {
        return this;
    }
}
