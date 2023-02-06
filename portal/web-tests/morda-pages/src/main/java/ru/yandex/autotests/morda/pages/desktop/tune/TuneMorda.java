package ru.yandex.autotests.morda.pages.desktop.tune;

import javax.ws.rs.core.UriBuilder;
import java.net.URI;

/**
 * User: asamar
 * Date: 04.08.16
 */
public abstract class TuneMorda{

    public abstract URI getUrl();

    public URI getGeoUrl() {
        return UriBuilder.fromUri(getUrl())
                .path("/geo")
                .build();
    }

    public URI getPlacesUrl() {
        return UriBuilder.fromUri(getUrl())
                .path("/places")
                .build();
    }

    public URI getLangUrl() {
        return UriBuilder.fromUri(getUrl())
                .path("/lang")
                .build();
    }

    public URI getSearchUrl() {
        return UriBuilder.fromUri(getUrl())
                .path("/search")
                .build();
    }

    public URI getAdvUrl() {
        return UriBuilder.fromUri(getUrl())
                .path("/adv")
                .build();
    }
}
