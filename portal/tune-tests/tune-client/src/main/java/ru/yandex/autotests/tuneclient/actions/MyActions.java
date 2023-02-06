package ru.yandex.autotests.tuneclient.actions;

import ru.yandex.autotests.tuneclient.TuneResponse;

import javax.ws.rs.client.Client;
import javax.ws.rs.client.ClientBuilder;
import javax.ws.rs.client.WebTarget;
import javax.ws.rs.core.Response;
import java.io.UnsupportedEncodingException;
import java.net.URI;
import java.util.ArrayList;
import java.util.List;

/**
 * @author Ivan Nikolaev <ivannik@yandex-team.ru>
 */
public class MyActions {

    private final URI baseURI;
    private final String path;
    private final String[] params;
    private final String block;
    private final String sk;
    private final String retpath;
    private final String json;

    public MyActions(URI baseURI, String path, String[] params, String block, String sk, String retpath, String json) {
        this.baseURI = baseURI;
        this.path = path;
        this.params = params;
        this.block = block;
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
                .queryParam("param", params)
                .queryParam("block", block)
                .queryParam("sk", sk)
                .queryParam("retpath", retpath)
                .queryParam("json", json);
    }

    public static class Builder {
        private final URI baseURI;
        private final String path;
        private String[] params;
        private String block;
        private String sk;
        private String retpath;
        private String json;

        public Builder(URI baseURI, String path) {
            this.baseURI = baseURI;
            this.path = path;
        }

        public MyActions build() {
            return new MyActions(baseURI, path, params, block, sk, retpath, json);
        }

        public Builder withParams(List<String> params) {
            if (params != null) {
                this.params = params.toArray(new String[params.size()]);
            }
            return this;
        }

        public Builder withBlock(String block) {
            this.block = block;
            return this;
        }

        public Builder withSk(String sk) {
            this.sk = sk;
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

        public Builder withJson(String json) {
            this.json = json;
            return this;
        }
    }
}
