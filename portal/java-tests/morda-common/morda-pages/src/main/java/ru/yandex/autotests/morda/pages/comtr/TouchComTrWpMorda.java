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
public class TouchComTrWpMorda extends ComTrMorda<TouchComTrWpMorda>
        implements AbstractTouchMorda<TouchComTrWpMorda> {

    private TouchComTrWpMorda(String scheme, String prefix, String environment) {
        super(scheme, prefix, environment);
    }

    public static TouchComTrWpMorda touchComTrWp() {
        return touchComTrWp("production");
    }

    public static TouchComTrWpMorda touchComTrWp(String environment) {
        return touchComTrWp("https", environment);
    }

    public static TouchComTrWpMorda touchComTrWp(String scheme, String environment) {
        return new TouchComTrWpMorda(scheme, "www", environment);
    }

    public static List<TouchComTrWpMorda> getDefaultList(String environment) {
        return asList(touchComTrWp(environment));
    }

    @Override
    public URI getBaseUrl() {
        return UriBuilder.fromUri(super.getBaseUrl()).queryParam("q", "").build();
    }

    @Override
    public String getDefaultUserAgent() {
        return CONFIG.getTouchwpUserAgent();
    }

    @Override
    public MordaType getMordaType() {
        return MordaType.TOUCH_COMTR_WP;
    }

    @Override
    public TouchComTrWpMorda me() {
        return this;
    }
}
