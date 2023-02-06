package ru.yandex.autotests.morda.client;

import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.xml.XmlMapper;
import com.fasterxml.jackson.jaxrs.json.JacksonJaxbJsonProvider;
import com.fasterxml.jackson.jaxrs.xml.JacksonJaxbXMLProvider;
import org.glassfish.jersey.apache.connector.ApacheConnectorProvider;
import org.glassfish.jersey.client.ClientConfig;
import org.glassfish.jersey.filter.LoggingFilter;

import javax.ws.rs.client.Client;
import javax.ws.rs.client.ClientBuilder;
import javax.ws.rs.core.MediaType;

/**
 * User: eoff (eoff@yandex-team.ru)
 * Date: 14/04/15
 */
public class MordaClientBuilder {
    private ObjectMapper objectMapper;
    private XmlMapper xmlMapper;
    private ClientConfig clientConfig;
    private JacksonJaxbXMLProvider jacksonJaxbXMLProvider;
    private JacksonJaxbJsonProvider jacksonJaxbJsonProvider;

    public MordaClientBuilder() {
        clientConfig = new ClientConfig();
        objectMapper = new ObjectMapper();
        xmlMapper = new XmlMapper();

        jacksonJaxbJsonProvider = new JacksonJaxbJsonProvider() {
            @Override
            protected boolean hasMatchingMediaType(MediaType mediaType) {
                return mediaType.isCompatible(MediaType.TEXT_PLAIN_TYPE) || super.hasMatchingMediaType(mediaType);
            }
        };
        jacksonJaxbJsonProvider.setMapper(objectMapper);
        jacksonJaxbJsonProvider.setAnnotationsToUse(JacksonJaxbJsonProvider.DEFAULT_ANNOTATIONS);
        jacksonJaxbXMLProvider = new JacksonJaxbXMLProvider();
        jacksonJaxbXMLProvider.setMapper(xmlMapper);

        clientConfig.connectorProvider(new ApacheConnectorProvider());
        clientConfig.register(jacksonJaxbJsonProvider);
        clientConfig.register(jacksonJaxbXMLProvider);
    }

    public static MordaClientBuilder mordaClient() {
        return new MordaClientBuilder();
    }

    public Client build() {
        return ClientBuilder.newBuilder().withConfig(clientConfig).build();
    }

    public MordaClientBuilder failOnUnknownProperties(boolean toFail) {
        if (toFail) {
            objectMapper.enable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES);
            xmlMapper.enable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES);
        } else {
            objectMapper.disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES);
            xmlMapper.disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES);
        }
        return this;
    }

    public MordaClientBuilder withLogging(boolean needLogging) {
        if (needLogging) {
            clientConfig.register(LoggingFilter.class);
        }
        return this;
    }

    public MordaClientBuilder acceptSingleValueAsArray(boolean singleValueAsArray) {
        if (singleValueAsArray) {
            objectMapper
                    .enable(DeserializationFeature.ACCEPT_SINGLE_VALUE_AS_ARRAY);
        } else {
            objectMapper
                    .disable(DeserializationFeature.ACCEPT_SINGLE_VALUE_AS_ARRAY);
        }
        return this;
    }
}
