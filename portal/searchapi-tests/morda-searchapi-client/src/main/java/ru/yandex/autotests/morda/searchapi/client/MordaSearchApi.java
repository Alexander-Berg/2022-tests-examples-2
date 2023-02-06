package ru.yandex.autotests.morda.searchapi.client;

import ru.yandex.autotests.morda.searchapi.client.requests.MordaFootballApiV1Request;
import ru.yandex.autotests.morda.searchapi.client.requests.MordaSearchApiV1Request;

import javax.ws.rs.client.Client;
import java.net.URI;

import static ru.yandex.autotests.morda.searchapi.client.requests.MordaFootballApiV1Request.mordaFootballApiRequest;
import static ru.yandex.autotests.morda.searchapi.client.requests.MordaSearchApiV1Request.mordaSearchApiRequest;
import static ru.yandex.autotests.morda.utils.client.MordaClientBuilder.mordaClient;

public class MordaSearchApi {

    private Client client;
    private URI host;

    public MordaSearchApi(URI host) {
        this(mordaClient()
                        .failOnUnknownProperties(false)
                        .withLogging(true)
                        .build(),
                host
        );
    }

    public MordaSearchApi(Client client, URI host) {
        this.client = client;
        this.host = host;
    }

    public MordaSearchApiV1Request.Builder getMordaSearchApiV1Req(){
        return mordaSearchApiRequest(host)
                .client(client);
    }

    public MordaFootballApiV1Request.Builder getMordaFootballApiV1Request(){
        return mordaFootballApiRequest(host)
                .client(client);
    }

    public static MordaSearchApi mordaSearchApi(URI host) {
        return new MordaSearchApi(host);
    }

    public static MordaSearchApi mordaSearchApi(Client client, URI host) {
        return new MordaSearchApi(client, host);
    }

    public Client getClient() {
        return client;
    }

    public void setClient(Client client) {
        this.client = client;
    }

    public URI getHost() {
        return host;
    }

    public void setHost(URI host) {
        this.host = host;
    }
}