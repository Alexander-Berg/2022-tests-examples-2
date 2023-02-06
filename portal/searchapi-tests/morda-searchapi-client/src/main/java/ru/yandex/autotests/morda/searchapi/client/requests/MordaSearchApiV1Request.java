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

import static java.util.Arrays.asList;
import static org.apache.commons.lang3.StringUtils.join;

public class MordaSearchApiV1Request extends Request<MordaSearchApiResponse>{

    protected MordaSearchApiV1Request(Builder builder) {
        super(new GenericType<MordaSearchApiResponse>(){}, builder);
    }

    public static MordaSearchApiV1Request.Builder mordaSearchApiRequest(URI host) {
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
            path("/portal/api/search/");
        }

        @Override
        protected Builder me() {
            return this;
        }

        @Override
        protected Invocation getInvocation() {
            return me()
                    .withVersion("1/")
                    .withAppPlatform("android")
                    .builder()
                    .accept(MediaType.APPLICATION_JSON_TYPE)
                    .buildGet();
        }

        @Override
        public MordaSearchApiV1Request build() {
            return new MordaSearchApiV1Request(this);
        }

        public Builder withVersion(String version){
            me().path(version);
            return me();
        }

        public Builder withGeo(String geo){
            me().queryParam("geo", geo);
            return me();
        }

        public Builder withGeo(int geo) {
            return withGeo(String.valueOf(geo));
        }

        public Builder withGeoBySettings(String geoBySettings) {
            me().queryParam("geo_by_settings", geoBySettings);
            return me();
        }

        public Builder withGeoBySettings(int geoBySettings) {
            return withGeoBySettings(String.valueOf(geoBySettings));
        }

        public Builder withDp(String dp){
            me().queryParam("dp", dp);
            return me();
        }

        public Builder withLang(String lang){
            me().queryParam("lang", lang);
            return me();
        }

        public Builder withOauth(String oauth){
            me().queryParam("oauth", oauth);
            return me();
        }

        public Builder withAppPlatform(String appPlatform){
            me().queryParam("app_platform", appPlatform);
            return me();
        }

        public Builder withBlock(String... blocks){
            me().queryParam("block", join(asList(blocks), ','));
            return me();
        }
    }
}