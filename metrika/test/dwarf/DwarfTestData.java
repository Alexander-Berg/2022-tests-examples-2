package ru.yandex.metrika.mobmet.crash.decoder.test.dwarf;

import java.util.List;
import java.util.Objects;

import ru.yandex.metrika.mobmet.crash.decoder.symbols.dwarf.functions.model.YDBFunction;
import ru.yandex.metrika.mobmet.crash.ios.DwarfEntryInfo;

public class DwarfTestData {

    private final DwarfEntryInfo meta;

    private final List<YDBFunction> data;

    public DwarfTestData(DwarfEntryInfo meta, List<YDBFunction> data) {
        this.meta = meta;
        this.data = data;
    }

    public DwarfEntryInfo getMeta() {
        return meta;
    }

    public List<YDBFunction> getData() {
        return data;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        DwarfTestData that = (DwarfTestData) o;
        return Objects.equals(meta, that.meta) &&
                Objects.equals(data, that.data);
    }

    @Override
    public int hashCode() {
        return Objects.hash(meta, data);
    }

    @Override
    public String toString() {
        return "DwarfTestData{" +
                "meta=" + meta +
                ", data=" + data +
                '}';
    }
}
