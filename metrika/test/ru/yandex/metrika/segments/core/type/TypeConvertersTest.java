package ru.yandex.metrika.segments.core.type;

import org.junit.Test;

import ru.yandex.metrika.segments.clickhouse.ClickHouse;
import ru.yandex.metrika.segments.clickhouse.ast.CHLiteral;
import ru.yandex.metrika.segments.clickhouse.literals.CHTuple4;
import ru.yandex.metrika.segments.clickhouse.types.TString;
import ru.yandex.metrika.segments.clickhouse.types.TTuple4;
import ru.yandex.metrika.segments.clickhouse.types.TUInt16;
import ru.yandex.metrika.segments.clickhouse.types.TUInt8;

import static org.junit.Assert.assertEquals;
import static ru.yandex.metrika.segments.core.type.TypeConverters.STRING;
import static ru.yandex.metrika.segments.core.type.TypeConverters.getUInt16Type;
import static ru.yandex.metrika.segments.core.type.TypeConverters.getUInt8Type;

/**
 * Created by vesel4ak-u on 11.11.15.
 */
public class TypeConvertersTest {

    TypeConverter<TTuple4<TUInt8,TUInt16, TString, TString>> productConverter = new TypeConverters.ProductTypeConverter4<TUInt8,TUInt16, TString, TString>(
            getUInt8Type(0), getUInt16Type(0), STRING, STRING, " ") {};

    @Test
    public void testProductConverter4toInternalIncorrect() {
        CHLiteral<TTuple4<TUInt8, TUInt16, TString, TString>> tuple = productConverter.toInternal("incorrect", null);
        CHTuple4<TUInt8,TUInt16, TString, TString> t = ClickHouse.unwrapt4(tuple);
        assertEquals(0, ClickHouse.unwrapun8(t.getT()).getV());
        assertEquals(0, ClickHouse.unwrapun16(t.getT2()).getV());
        assertEquals("", ClickHouse.unwraps(t.getT3()).getV());
        assertEquals("", ClickHouse.unwraps(t.getT4()).getV());
    }

    @Test
    public void testProductConverter4toInternal() {
        //TypeConverter<CHTuple4<CHUInt8,CHUInt16, CHString, CHString>> productConverter = new TypeConverters.ProductTypeConverter4<CHUInt8,CHUInt16, CHString, CHString>(
                //getUInt8Type(0), getUInt16Type(0), STRING, STRING, " ") {};
        CHLiteral<TTuple4<TUInt8, TUInt16, TString, TString>> tuple = productConverter.toInternal("255 0 string ", null);
        CHTuple4<TUInt8,TUInt16, TString, TString> t = ClickHouse.unwrapt4(tuple);
        assertEquals(255, ClickHouse.unwrapun8(t.getT()).getV());
        assertEquals(0, ClickHouse.unwrapun16(t.getT2()).getV());
        assertEquals("string", ClickHouse.unwraps(t.getT3()).getV());
        assertEquals("", ClickHouse.unwraps(t.getT4()).getV());
    }

    @Test
    public void testProductConverter4toExternal() {
        //TypeConverter<CHTuple4<CHUInt8,CHUInt16, CHString, CHString>> productConverter = new TypeConverters.ProductTypeConverter4<CHUInt8,CHUInt16, CHString, CHString>(
                //getUInt8Type(0), getUInt16Type(0), STRING, STRING, " ") {};
        CHLiteral<TTuple4<TUInt8, TUInt16, TString, TString>> tuple = productConverter.parse("[255,0,\"string\",\"\"]");
        assertEquals("255 0 string null", productConverter.toExternal(tuple, null));
    }

}
