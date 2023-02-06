package ru.yandex.metrika.common.test.medium;

import java.nio.charset.Charset;
import java.util.Arrays;

import ru.yandex.autotests.metrika.commons.beans.CellWriter;
import ru.yandex.autotests.metrika.commons.tabseparated.TabSeparated;

import static ru.yandex.autotests.metrika.commons.tabseparated.Escape.escape;

/**
 * Враппер для ClickHouse'ного типа FixedString(N).
 * На самом деле является не строкой, а массивом байт фиксированного размера.
 */
public class FixedString implements CellWriter {

    private byte[] data;

    /**
     * Специальный конструктор для десериализации
     *
     * @param data массив байтов из ClickHouse'а
     */
    public FixedString(byte[] data) {
        this.data = data.clone();
    }

    /**
     * Метод сериализации
     *
     * @return сериализованное значение
     */
    @Override
    public byte[] write() {
        return escape(TabSeparated.UNESCAPED_TO_ESCAPED, toBytes());
    }

    @Override
    public String toString() {
        final StringBuilder sb = new StringBuilder("FixedString{");
        for (byte b : data) {
            sb.append(String.format("%02X", b));
        }
        sb.append('}');
        return sb.toString();
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof FixedString)) return false;
        FixedString that = (FixedString) o;
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

    public static FixedString fromString(String string, Charset charset) {
        return new FixedString(string.getBytes(charset));
    }

    public static FixedString fromBytes(byte[] bytes) {
        return new FixedString(bytes);
    }

    public static FixedString empty() {
        return empty(0);
    }

    public static FixedString empty(int length) {
        return fromBytes(new byte[length]);
    }

}
