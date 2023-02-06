package ru.yandex.autotests.mordabackend.beans.mail;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.JavaType;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.introspect.Annotated;
import com.fasterxml.jackson.databind.introspect.JacksonAnnotationIntrospector;
import com.fasterxml.jackson.databind.type.TypeFactory;
import com.fasterxml.jackson.module.jaxb.JaxbAnnotationIntrospector;

import java.io.IOException;
import java.util.List;

import static com.fasterxml.jackson.databind.AnnotationIntrospector.pair;

/**
 * User: ivannik
 * Date: 28.07.2014
 */
public class SocialInitList {

    private static final ObjectMapper om;

    static {
        om = new ObjectMapper();
        om.setAnnotationIntrospector(pair(new JaxbAnnotationIntrospector(TypeFactory.defaultInstance()) {
            @Override
            public Class<?> _doFindDeserializationType(Annotated a, JavaType baseContentType) {
                return null;
            }
        }, new JacksonAnnotationIntrospector()))
                .disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES)
                .enable(DeserializationFeature.ACCEPT_SINGLE_VALUE_AS_ARRAY);
    }

    private List<SocialInit> socialInits;

    @JsonCreator
    public SocialInitList(String socialInit) throws IOException {
        socialInits =
                om.readValue(socialInit, om.getTypeFactory().constructCollectionType(List.class, SocialInit.class));
    }

    public List<SocialInit> getList() {
        return socialInits;
    }
}
