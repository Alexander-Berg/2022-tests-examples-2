package ru.yandex.metrika.segments.clickhouse;

import org.junit.Ignore;
import org.junit.Test;

import ru.yandex.metrika.segments.clickhouse.ast.CHLiteral;
import ru.yandex.metrika.segments.clickhouse.types.TDate;
import ru.yandex.metrika.segments.clickhouse.types.TDateTime;
import ru.yandex.metrika.segments.clickhouse.types.TFloat64;
import ru.yandex.metrika.segments.clickhouse.types.TInt64;
import ru.yandex.metrika.segments.clickhouse.types.TString;
import ru.yandex.metrika.segments.clickhouse.types.TTuple2;
import ru.yandex.metrika.segments.clickhouse.types.TTuple3;
import ru.yandex.metrika.segments.clickhouse.types.TTuple4;
import ru.yandex.metrika.segments.clickhouse.types.TUInt16;
import ru.yandex.metrika.segments.clickhouse.types.TUInt8;
import ru.yandex.metrika.segments.core.type.TypeConverter;
import ru.yandex.metrika.segments.core.type.TypeConverters;

import static org.junit.Assert.assertEquals;

/**
 * Created by orantius on 10/9/15.
 */
@Ignore("METRIQA-936")
public class ValueParserTest {

    private final TypeConverter<TDate> cDate = TypeConverters.DATE;
    private final TypeConverter<TDateTime> cDateTime = TypeConverters.DATE_TIME;
    private final TypeConverter<TInt64> cInt = TypeConverters.getInt64Type(-2);
    private final TypeConverter<TUInt8> cInt8 = TypeConverters.getUInt8Type(0);
    private final TypeConverter<TUInt16> cInt16 = TypeConverters.getUInt16Type(0);
    private final TypeConverter<TFloat64> cFloat= TypeConverters.DOUBLE;

    private final TypeConverter<TString> cString = TypeConverters.STRING;

    @Test
    public void testParse() throws Exception {
        {
            TypeConverter<TTuple2<TDate, TDateTime>> productConverter = getDateDateTimeConverter(cDate, cDateTime, " ");
            CHLiteral<TTuple2<TDate, TDateTime>> parse = productConverter.parse("[\"2013-10-11\",\"2013-10-11 17:26:34\"]");
            assertEquals("(2013-10-11,2013-10-11 17:26:34)", parse.asString());
            assertEquals("tuple(toDate('2013-10-11'),toDateTime('2013-10-11 17:26:34'))", parse.asSql());
        }
        {
            TypeConverter<TTuple2<TDate, TInt64>> productConverter = getDateIntConverter(cDate, cInt, " ");
            CHLiteral<TTuple2<TDate, TInt64>> parse = productConverter.parse("[\"2013-10-11\",\"4242424242\"]");
            assertEquals("(2013-10-11,4242424242)", parse.asString());
            assertEquals("tuple(toDate('2013-10-11'),4242424242)", parse.asSql());

        }
        { // TODO STRING ESCAPE
            TypeConverter<TTuple2<TDate, TString>> productConverter = getDateStringConverter(cDate, cString, " ");
            CHLiteral<TTuple2<TDate, TString>> parse = productConverter.parse("[\"2013-10-11\",\"ab\\c42\"]");
            assertEquals("(2013-10-11,ab\\c42)", parse.asString());
            assertEquals("tuple(toDate('2013-10-11'),'ab\\\\c42')", parse.asSql());

        }
        {// эти тесты сейчас не работают, т.к. парсинг сломан.
            TypeConverter<TTuple2<TFloat64, TFloat64>> productConverter = getFloatFloatConverter(cFloat, cFloat, " ");
            {
                CHLiteral<TTuple2<TFloat64, TFloat64>> parse = productConverter.parse("[00.000321,231100.0012300]");
                assertEquals("(3.21E-4,231100.00123)", parse.asString());
                assertEquals("tuple(3.21E-4,231100.00123)", parse.asSql());
            }
            {
                CHLiteral<TTuple2<TFloat64, TFloat64>> parse = productConverter.parse("[0.1,1.0]");
                assertEquals("(0.1,1.0)", parse.asString());
                assertEquals("tuple(0.1,1.0)", parse.asSql());
            }
            {
                CHLiteral<TTuple2<TFloat64, TFloat64>> parse = productConverter.parse("[1e-7,-1e-7]");
                assertEquals("(1.0E-7,-1.0E-7)", parse.asString());
                assertEquals("tuple(1.0E-7,-1.0E-7)", parse.asSql());
            }
            {
                CHLiteral<TTuple2<TFloat64, TFloat64>> parse = productConverter.parse("[1.0e10,+1.0E+10]");
                assertEquals("(1.0E10,1.0E10)", parse.asString());
                assertEquals("tuple(1.0E10,1.0E10)", parse.asSql());
            }

        }

        {
            TypeConverter<TTuple3<TUInt8,TUInt16, TString>> productConverter = TypeConverters.getBrowserAndVersionConverter(cInt8, cInt16, cString, " ");
            CHLiteral<TTuple3<TUInt8, TUInt16, TString>> parse = productConverter.parse("[6,40,\"0\"]");
            assertEquals("(6,40,0)", parse.asString());
            assertEquals("tuple(6,40,'0')", parse.asSql());
        }

        {
            TypeConverter<TTuple4<TUInt8,TUInt16, TString, TDate>> productConverter = new TypeConverters.ProductTypeConverter4<TUInt8,TUInt16, TString, TDate>(cInt8, cInt16, cString, cDate, " ") {};
            CHLiteral<TTuple4<TUInt8, TUInt16, TString, TDate>> parse = productConverter.parse("[255,0,\"string\",\"2013-10-11\"]");
            assertEquals("(255,0,string,2013-10-11)", parse.asString());
            assertEquals("tuple(255,0,'string',toDate('2013-10-11'))", parse.asSql());
        }

    }

    public static TypeConverter<TTuple2<TDate, TDateTime>> getDateDateTimeConverter(TypeConverter<TDate> left, TypeConverter<TDateTime> right, String externalSeparator) {
        return new TypeConverters.ProductTypeConverter<TDate, TDateTime>(left, right, externalSeparator) {};
    }

    public static TypeConverter<TTuple2<TDate, TInt64>> getDateIntConverter(TypeConverter<TDate> left, TypeConverter<TInt64> right, String externalSeparator) {
        return new TypeConverters.ProductTypeConverter<TDate, TInt64>(left, right, externalSeparator) {};
    }

    public static TypeConverter<TTuple2<TDate, TFloat64>> getDateFloatConverter(TypeConverter<TDate> left, TypeConverter<TFloat64> right, String externalSeparator) {
        return new TypeConverters.ProductTypeConverter<TDate, TFloat64>(left, right, externalSeparator) {};
    }

    public static TypeConverter<TTuple2<TFloat64, TFloat64>> getFloatFloatConverter(TypeConverter<TFloat64> left, TypeConverter<TFloat64> right, String externalSeparator) {
        return new TypeConverters.ProductTypeConverter<TFloat64, TFloat64>(left, right, externalSeparator) {};
    }

    public static TypeConverter<TTuple2<TDate, TString>> getDateStringConverter(TypeConverter<TDate> left, TypeConverter<TString> right, String externalSeparator) {
        return new TypeConverters.ProductTypeConverter<TDate, TString>(left, right, externalSeparator) {};
    }

}
