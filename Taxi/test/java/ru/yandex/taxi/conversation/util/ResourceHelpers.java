package ru.yandex.taxi.conversation.util;

import org.apache.commons.io.IOUtils;

import java.io.IOException;

public class ResourceHelpers {

    public static byte[] getResource(String resourcePath) {
        try {
            return IOUtils.toByteArray(ResourceHelpers.class.getResourceAsStream(resourcePath));
        } catch (IOException e) {
            throw new RuntimeException(String.format("cannot load resource %s", resourcePath));
        }
    }
}
