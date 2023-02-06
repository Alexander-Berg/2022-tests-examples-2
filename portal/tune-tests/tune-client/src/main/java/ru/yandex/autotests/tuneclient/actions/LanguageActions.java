package ru.yandex.autotests.tuneclient.actions;

import ru.yandex.autotests.tuneclient.TuneResponse;

import javax.ws.rs.client.Client;
import javax.ws.rs.client.ClientBuilder;
import javax.ws.rs.client.WebTarget;
import javax.ws.rs.core.Response;
import java.io.UnsupportedEncodingException;
import java.net.URI;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 21/01/15
 */
public class LanguageActions {
    private final URI baseURI;
    private final String path;
    private final String intl;
    private final String sk;
    private final String retpath;
    private final String json;

    public LanguageActions(URI baseURI, String path, String intl, String sk, String retpath, String json) {
        this.baseURI = baseURI;
        this.path = path;
        this.intl = intl;
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
                .queryParam("intl", intl)
                .queryParam("sk", sk)
                .queryParam("retpath", retpath)
                .queryParam("json", json);
    }

    public static class Builder {
        private final URI baseURI;
        private final String path;
        private String intl;
        private String sk;
        private String retpath;
        private String json;

        public Builder(URI baseURI, String path) {
            this.baseURI = baseURI;
            this.path = path;
        }

        public LanguageActions build() {
            return new LanguageActions(baseURI, path, intl, sk, retpath, json);
        }

        public Builder withIntl(String intl) {
            this.intl = intl;
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
