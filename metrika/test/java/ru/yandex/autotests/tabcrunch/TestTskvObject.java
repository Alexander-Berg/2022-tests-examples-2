
package ru.yandex.autotests.tabcrunch;

import ru.yandex.autotests.metrika.commons.beans.Column;
import ru.yandex.autotests.metrika.commons.beans.Position;

public class TestTskvObject {

    @Position(1)
    @Column(name = "booleanValue", type = "UInt8")
    private java.lang.Boolean booleanValue;
    @Position(2)
    @Column(name = "Int8Value", type = "Int8")
    private java.lang.Integer int8Value;
    @Position(3)
    @Column(name = "Int16Value", type = "Int16")
    private java.lang.Integer int16Value;
    @Position(4)
    @Column(name = "Int32Value", type = "Int32")
    private java.lang.Integer int32Value;
    @Position(5)
    @Column(name = "Int64Value", type = "Int64")
    private java.lang.Long int64Value;
    @Position(6)
    @Column(name = "UInt8Value", type = "UInt8")
    private java.lang.Integer UInt8Value;
    @Position(7)
    @Column(name = "UInt16Value", type = "UInt16")
    private java.lang.Integer UInt16Value;
    @Position(8)
    @Column(name = "UInt32Value", type = "UInt32")
    private java.lang.Long UInt32Value;
    @Position(9)
    @Column(name = "UInt64Value", type = "UInt64")
    private java.math.BigInteger UInt64Value;
    @Position(10)
    @Column(name = "StringValue", type = "String")
    private java.lang.String stringValue;
    @Position(11)
    @Column(name = "float32Value", type = "Float32")
    private java.lang.Float float32Value;
    @Position(12)
    @Column(name = "float64Value", type = "Float64")
    private java.lang.Double float64Value;
    @Position(13)
    @Column(name = "LocalDateTimeValue", type = "DateTime")
    private org.joda.time.DateTime localDateTimeValue;
    @Position(14)
    @Column(name = "LocalDateValue", type = "Date")
    private org.joda.time.DateTime localDateValue;
    @Position(15)
    @Column(name = "vectorStringValue", type = "Array(String)")
    private java.lang.String[] vectorStringValue;
    @Position(16)
    @Column(name = "vectorDoubleValue", type = "Array(Double)")
    private java.lang.Double[] vectorDoubleValue;
    @Position(17)
    @Column(name = "vectorUint16Value", type = "Array(UInt16)")
    private java.lang.Integer[] vectorUint16Value;
    @Position(18)
    @Column(name = "vectorUint32Value", type = "Array(UInt32)")
    private java.lang.Long[] vectorUint32Value;
    @Position(19)
    @Column(name = "vectorUint64Value", type = "Array(UInt64)")
    private java.math.BigInteger[] vectorUint64Value;

    public TestTskvObject() {
    }

    public TestTskvObject(TestTskvObject testTskvObject) {
        this.booleanValue = testTskvObject.booleanValue;
        this.int8Value = testTskvObject.int8Value;
        this.int16Value = testTskvObject.int16Value;
        this.int32Value = testTskvObject.int32Value;
        this.int64Value = testTskvObject.int64Value;
        this.UInt8Value = testTskvObject.UInt8Value;
        this.UInt16Value = testTskvObject.UInt16Value;
        this.UInt32Value = testTskvObject.UInt32Value;
        this.UInt64Value = testTskvObject.UInt64Value;
        this.stringValue = testTskvObject.stringValue;
        this.float32Value = testTskvObject.float32Value;
        this.float64Value = testTskvObject.float64Value;
        this.localDateTimeValue = testTskvObject.localDateTimeValue;
        this.localDateValue = testTskvObject.localDateValue;
        this.vectorStringValue = testTskvObject.vectorStringValue;
        this.vectorDoubleValue = testTskvObject.vectorDoubleValue;
        this.vectorUint16Value = testTskvObject.vectorUint16Value;
        this.vectorUint32Value = testTskvObject.vectorUint32Value;
        this.vectorUint64Value = testTskvObject.vectorUint64Value;
    }

    public java.lang.Boolean getBooleanValue() {
        return booleanValue;
    }

    public void setBooleanValue(java.lang.Boolean booleanValue) {
        this.booleanValue = booleanValue;
    }

    public TestTskvObject withBooleanValue(java.lang.Boolean booleanValue) {
        this.booleanValue = booleanValue;
        return this;
    }

    public java.lang.Integer getInt8Value() {
        return int8Value;
    }

    public void setInt8Value(java.lang.Integer int8Value) {
        this.int8Value = int8Value;
    }

    public TestTskvObject withInt8Value(java.lang.Integer int8Value) {
        this.int8Value = int8Value;
        return this;
    }

    public java.lang.Integer getInt16Value() {
        return int16Value;
    }

    public void setInt16Value(java.lang.Integer int16Value) {
        this.int16Value = int16Value;
    }

    public TestTskvObject withInt16Value(java.lang.Integer int16Value) {
        this.int16Value = int16Value;
        return this;
    }

    public java.lang.Integer getInt32Value() {
        return int32Value;
    }

    public void setInt32Value(java.lang.Integer int32Value) {
        this.int32Value = int32Value;
    }

    public TestTskvObject withInt32Value(java.lang.Integer int32Value) {
        this.int32Value = int32Value;
        return this;
    }

    public java.lang.Long getInt64Value() {
        return int64Value;
    }

    public void setInt64Value(java.lang.Long int64Value) {
        this.int64Value = int64Value;
    }

    public TestTskvObject withInt64Value(java.lang.Long int64Value) {
        this.int64Value = int64Value;
        return this;
    }

    public java.lang.Integer getUInt8Value() {
        return UInt8Value;
    }

    public void setUInt8Value(java.lang.Integer UInt8Value) {
        this.UInt8Value = UInt8Value;
    }

    public TestTskvObject withUInt8Value(java.lang.Integer UInt8Value) {
        this.UInt8Value = UInt8Value;
        return this;
    }

    public java.lang.Integer getUInt16Value() {
        return UInt16Value;
    }

    public void setUInt16Value(java.lang.Integer UInt16Value) {
        this.UInt16Value = UInt16Value;
    }

    public TestTskvObject withUInt16Value(java.lang.Integer UInt16Value) {
        this.UInt16Value = UInt16Value;
        return this;
    }

    public java.lang.Long getUInt32Value() {
        return UInt32Value;
    }

    public void setUInt32Value(java.lang.Long UInt32Value) {
        this.UInt32Value = UInt32Value;
    }

    public TestTskvObject withUInt32Value(java.lang.Long UInt32Value) {
        this.UInt32Value = UInt32Value;
        return this;
    }

    public java.math.BigInteger getUInt64Value() {
        return UInt64Value;
    }

    public void setUInt64Value(java.math.BigInteger UInt64Value) {
        this.UInt64Value = UInt64Value;
    }

    public TestTskvObject withUInt64Value(java.math.BigInteger UInt64Value) {
        this.UInt64Value = UInt64Value;
        return this;
    }

    public java.lang.String getStringValue() {
        return stringValue;
    }

    public void setStringValue(java.lang.String stringValue) {
        this.stringValue = stringValue;
    }

    public TestTskvObject withStringValue(java.lang.String stringValue) {
        this.stringValue = stringValue;
        return this;
    }

    public java.lang.Float getFloat32Value() {
        return float32Value;
    }

    public void setFloat32Value(java.lang.Float float32Value) {
        this.float32Value = float32Value;
    }

    public TestTskvObject withFloat32Value(java.lang.Float float32Value) {
        this.float32Value = float32Value;
        return this;
    }

    public java.lang.Double getFloat64Value() {
        return float64Value;
    }

    public void setFloat64Value(java.lang.Double float64Value) {
        this.float64Value = float64Value;
    }

    public TestTskvObject withFloat64Value(java.lang.Double float64Value) {
        this.float64Value = float64Value;
        return this;
    }

    public org.joda.time.DateTime getLocalDateTimeValue() {
        return localDateTimeValue;
    }

    public void setLocalDateTimeValue(org.joda.time.DateTime localDateTimeValue) {
        this.localDateTimeValue = localDateTimeValue;
    }

    public TestTskvObject withLocalDateTimeValue(org.joda.time.DateTime localDateTimeValue) {
        this.localDateTimeValue = localDateTimeValue;
        return this;
    }

    public org.joda.time.DateTime getLocalDateValue() {
        return localDateValue;
    }

    public void setLocalDateValue(org.joda.time.DateTime localDateValue) {
        this.localDateValue = localDateValue;
    }

    public TestTskvObject withLocalDateValue(org.joda.time.DateTime localDateValue) {
        this.localDateValue = localDateValue;
        return this;
    }

    public java.lang.String[] getVectorStringValue() {
        return vectorStringValue;
    }

    public void setVectorStringValue(java.lang.String[] vectorStringValue) {
        this.vectorStringValue = vectorStringValue;
    }

    public TestTskvObject withVectorStringValue(java.lang.String[] vectorStringValue) {
        this.vectorStringValue = vectorStringValue;
        return this;
    }

    public java.lang.Double[] getVectorDoubleValue() {
        return vectorDoubleValue;
    }

    public void setVectorDoubleValue(java.lang.Double[] vectorDoubleValue) {
        this.vectorDoubleValue = vectorDoubleValue;
    }

    public TestTskvObject withVectorDoubleValue(java.lang.Double[] vectorDoubleValue) {
        this.vectorDoubleValue = vectorDoubleValue;
        return this;
    }

    public java.lang.Integer[] getVectorUint16Value() {
        return vectorUint16Value;
    }

    public void setVectorUint16Value(java.lang.Integer[] vectorUint16Value) {
        this.vectorUint16Value = vectorUint16Value;
    }

    public TestTskvObject withVectorUint16Value(java.lang.Integer[] vectorUint16Value) {
        this.vectorUint16Value = vectorUint16Value;
        return this;
    }

    public java.lang.Long[] getVectorUint32Value() {
        return vectorUint32Value;
    }

    public void setVectorUint32Value(java.lang.Long[] vectorUint32Value) {
        this.vectorUint32Value = vectorUint32Value;
    }

    public TestTskvObject withVectorUint32Value(java.lang.Long[] vectorUint32Value) {
        this.vectorUint32Value = vectorUint32Value;
        return this;
    }

    public java.math.BigInteger[] getVectorUint64Value() {
        return vectorUint64Value;
    }

    public void setVectorUint64Value(java.math.BigInteger[] vectorUint64Value) {
        this.vectorUint64Value = vectorUint64Value;
    }

    public TestTskvObject withVectorUint64Value(java.math.BigInteger[] vectorUint64Value) {
        this.vectorUint64Value = vectorUint64Value;
        return this;
    }

    public TestTskvObject withByteArrayValue(byte[] byteArrayValue) {
        return this;
    }

}
