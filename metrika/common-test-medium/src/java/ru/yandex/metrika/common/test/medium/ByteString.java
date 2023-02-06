package ru.yandex.metrika.common.test.medium;

import java.nio.charset.Charset;
import java.util.Arrays;

import ru.yandex.autotests.metrika.commons.beans.CellWriter;

/**
 * В Clickhouse сторки это просто последовательность байтов. Поэтому там в типе String можно спокойно
 * сохранять бинарные данные (например, протобуф), что мы успешно и делаем.
 * Но в Java строки имеют кодировку и сохранить туда какой-то мусор не получится.
 */
public class ByteString implements CellWriter {

    private final byte[] data;

    /**
     * Специальный конструктор для десериализации
     *
     * @param data массив байтов из ClickHouse'а
     */
    public ByteString(byte[] data) {
        this.data = data.clone();
    }

    /**
     * Метод сериализации
     *
     * @return сериализованное значение
     */
    @Override
    public byte[] write() {
        return toBytes();
    }

    @Override
    public String toString() {
        final StringBuilder sb = new StringBuilder("ByteString{");
        for (byte b : data) {
            sb.append(String.format("%02X", b));
        }
        sb.append('}');
        return sb.toString();
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof ByteString)) return false;
        ByteString that = (ByteString) o;
        return Arrays.equals(data, that.data);
    }

    @Override
    public int hashCode() {
        return Arrays.hashCode(data);
    }

    public String toString(Charset charset) {
        return new String(data, charset);
    }

    public byte[] toBytes() {
        return data.clone();
    }

    public static ByteString fromString(String string, Charset charset) {
        return new ByteString(string.getBytes(charset));
    }

    public static ByteString fromBytes(byte[] bytes) {
        return new ByteString(bytes);
    }

    public static ByteString empty() {
        return empty(0);
    }

    public static ByteString empty(int length) {
        return fromBytes(new byte[length]);
    }

}
