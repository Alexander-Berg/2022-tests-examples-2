package ru.yandex.autotests.tuneclient.actions;

import javax.ws.rs.client.Client;
import javax.ws.rs.client.ClientBuilder;
import javax.ws.rs.client.WebTarget;
import javax.ws.rs.core.Response;
import java.net.URI;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
public class GeoSearchActions {
    private final URI baseURI;
    private final String path;
    private final String part;
    private final String types;
    private final String count;
    private final String callback;
    private final String lang;
    private final String format;
    private final String parents;

    public GeoSearchActions(URI baseURI, String path, String part, String types, String count, String callback, String lang,
                            String format, String parents)
    {
        this.baseURI = baseURI;
        this.path = path;
        this.part = part;
        this.types = types;
        this.count = count;
        this.callback = callback;
        this.lang = lang;
        this.format = format;
        this.parents = parents;
    }

    public Response get() {
        return get(ClientBuilder.newClient());
    }

    public Response get(Client client) {
        return getTarget(client)
                .request()
                .header("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
                .get();
    }

    public URI getUri() {
        Client client = ClientBuilder.newClient();
        URI uri = getTarget(client).getUri();
        client.close();
        return uri;
    }

    private WebTarget getTarget(Client client) {
        return client.target(baseURI).path(path)
                .queryParam("part", part)
                .queryParam("types", types)
                .queryParam("count", count)
                .queryParam("callback", callback)
                .queryParam("lang", lang)
                .queryParam("format", format)
                .queryParam("parents", parents);
    }

    public static class Builder {
        private final URI baseURI;
        private final String path;
        private String part;
        private String types;
        private String count;
        private String callback;
        private String lang;
        private String format;
        private String parents;

        public Builder(URI baseURI, String path) {
            this.baseURI = baseURI;
            this.path = path;
        }

        public GeoSearchActions build() {
            return new GeoSearchActions(baseURI, path, part, types, count, callback, lang, format, parents);
        }

        public Builder withPart(String part) {
            this.part = part;
            return this;
        }

        public Builder withTypes(String types) {
            this.types = types;
            return this;
        }

        public Builder withCount(String count) {
            this.count = count;
            return this;
        }

        public Builder withCallback(String callback) {
            this.callback = callback;
            return this;
        }

        public Builder withLang(String lang) {
            this.lang = lang;
            return this;
        }

        public Builder withFormat(String format) {
            this.format = format;
            return this;
        }

        public Builder withParents(String parents) {
            this.parents = parents;
            return this;
        }

    }
}
