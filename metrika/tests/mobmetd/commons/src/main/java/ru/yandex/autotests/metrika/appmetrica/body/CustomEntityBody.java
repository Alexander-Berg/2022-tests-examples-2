package ru.yandex.autotests.metrika.appmetrica.body;

public class CustomEntityBody {
    private final String contentType;
    private final byte[] content;

    public CustomEntityBody(String contentType, byte[] content) {
        this.contentType = contentType;
        this.content = content;
    }

    public String getContentType() {
        return contentType;
    }

    public byte[] getContent() {
        return content;
    }
}
