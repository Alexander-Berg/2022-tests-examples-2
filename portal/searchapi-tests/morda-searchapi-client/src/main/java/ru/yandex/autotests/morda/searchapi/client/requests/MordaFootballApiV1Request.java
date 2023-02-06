package ru.yandex.autotests.morda.searchapi.client.requests;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.module.SimpleModule;
import ru.yandex.autotests.morda.searchapi.beans.MordaSearchApiResponse;
import ru.yandex.autotests.morda.searchapi.beans.MordaSearchApiResponseDeserializer;
import ru.yandex.autotests.morda.utils.client.requests.GetRequestBuilder;
import ru.yandex.autotests.morda.utils.client.requests.Request;

import javax.ws.rs.client.Invocation;
import javax.ws.rs.core.GenericType;
import javax.ws.rs.core.MediaType;
import java.io.IOException;
import java.net.URI;

/**
 * User: asamar
 * Date: 11.11.2015.
 */
public class MordaFootballApiV1Request extends Request<MordaSearchApiResponse> {

    protected MordaFootballApiV1Request(Builder builder) {
        super(new GenericType<MordaSearchApiResponse>(){}, builder);
    }

    public static MordaFootballApiV1Request.Builder mordaFootballApiRequest(URI host) {
        return new Builder(host);
    }

    @Override
    public MordaSearchApiResponse read() {
        ObjectMapper objectMapper = new ObjectMapper();

        SimpleModule simpleModule = new SimpleModule().addDeserializer(MordaSearchApiResponse.class,
                new MordaSearchApiResponseDeserializer());
        objectMapper.registerModule(simpleModule);

        String response = read(String.class);

        try {
            return objectMapper.readValue(response, MordaSearchApiResponse.class);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public static class Builder extends GetRequestBuilder<Builder> {

        public Builder(URI host) {
            super(host);
            path("/portal/api/football/");
        }

        @Override
        protected Builder me() {
            return this;
        }

        @Override
        protected Invocation getInvocation() {
            return me()
                    .withVersion("1/")
                    .builder()
                    .accept(MediaType.APPLICATION_JSON_TYPE)
                    .buildGet();
        }

        @Override
        public MordaFootballApiV1Request build() {
            return new MordaFootballApiV1Request(this);
        }

        public Builder withVersion(String version){
            me().path(version);
            return me();
        }

        public Builder withFootballClub(String club){
            me().queryParam("football_tr_club", club);
            return me();
        }
    }
}
