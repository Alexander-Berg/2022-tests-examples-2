package ru.yandex.autotests.tuneclient.actions;

import ru.yandex.autotests.tuneclient.TuneResponse;

import javax.ws.rs.client.Client;
import javax.ws.rs.client.ClientBuilder;
import javax.ws.rs.client.WebTarget;
import javax.ws.rs.core.GenericType;
import javax.ws.rs.core.Response;
import java.io.UnsupportedEncodingException;
import java.net.URI;
import java.util.Map;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 21/01/15
 */
public class RegionActions {
    private final URI baseURI;
    private final String path;
    private final String regionId;
    private final String name;
    private final String auto;
    private final String noLocation;
    private final String from;
    private final String sk;
    private final String retpath;
    private final String json;

    public RegionActions(URI baseURI, String path, String regionId, String name, String auto,
                         String noLocation, String from, String sk, String retpath, String json)
    {
        this.baseURI = baseURI;
        this.path = path;
        this.regionId = regionId;
        this.name = name;
        this.auto = auto;
        this.noLocation = noLocation;
        this.from = from;
        this.sk = sk;
        this.retpath = retpath;
        this.json = json;
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

    public TuneResponse getTuneResponse(Client client) {
        return getTarget(client)
                .request()
                .header("Accept", "application/json;q=0.9,*/*;q=0.8")
                .get(TuneResponse.class);
    }

    public URI getUri() {
        Client client = ClientBuilder.newClient();
        URI uri = getTarget(client).getUri();
        client.close();
        return uri;
    }

    private WebTarget getTarget(Client client) {
        return client.target(baseURI).path(path)
                .queryParam("id", regionId)
                .queryParam("name", name)
                .queryParam("auto", auto)
                .queryParam("no_location", noLocation)
                .queryParam("from", from)
                .queryParam("sk", sk)
                .queryParam("retpath", retpath)
                .queryParam("json", json);
    }

    public static class Builder {
        private final URI baseURI;
        private final String path;
        private String regionId;
        private String name;
        private String auto;
        private String noLocation;
        private String from;
        private String sk;
        private String retpath;
        private String json;

        public Builder(URI baseURI, String path) {
            this.baseURI = baseURI;
            this.path = path;
        }

        public RegionActions build() {
            return new RegionActions(baseURI, path, regionId, name, auto, noLocation, from, sk, retpath, json);
        }

        public Builder withRegionId(String regionId) {
            this.regionId = regionId;
            return this;
        }

        public Builder withName(String name) {
            this.name = name;
            return this;
        }

        public Builder withAuto(String auto) {
            this.auto = auto;
            return this;
        }

        public Builder withNoLocation(String noLocation) {
            this.noLocation = noLocation;
            return this;
        }

        public Builder withFrom(String from) {
            this.from = from;
            return this;
        }

        public Builder withRetpath(String retpath) {
            try {
                this.retpath = retpath == null
                        ? null
                        : java.net.URLEncoder.encode(retpath, "UTF-8");
            } catch (UnsupportedEncodingException e) {
                throw new RuntimeException(e);
            }
            return this;
        }

        public Builder withSk(String sk) {
            this.sk = sk;
            return this;
        }

        public Builder withJson(String json) {
            this.json = json;
            return this;
        }
    }

}
