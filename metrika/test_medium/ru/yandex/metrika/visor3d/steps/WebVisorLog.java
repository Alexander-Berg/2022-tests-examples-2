package ru.yandex.metrika.visor3d.steps;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.lang.reflect.Field;
import java.math.BigInteger;

import com.google.common.base.Ascii;
import org.jetbrains.annotations.NotNull;

import ru.yandex.autotests.metrika.commons.beans.Column;
import ru.yandex.autotests.metrika.commons.beans.Serialization;
import ru.yandex.metrika.common.test.medium.ByteString;
import ru.yandex.metrika.util.chunk.ChunkDescriptor;
import ru.yandex.metrika.util.chunk.ChunkRow;
import ru.yandex.metrika.util.chunk.output.CommandOutput;
import ru.yandex.metrika.wv2.proto.RecorderProto;

import static com.google.common.base.Throwables.propagate;
import static java.lang.String.format;
import static java.util.Arrays.stream;
import static java.util.stream.Collectors.joining;

public class WebVisorLog implements ChunkRow {

    @Column(name = "CounterID", type = "UInt32")
    private Long counterID;

    @Column(name = "UniqID", type = "UInt64")
    private BigInteger uniqID;

    @Column(name = "EventTime", type = "UInt32")
    private Long eventTime;

    @Column(name = "CounterClass", type = "UInt8")
    private Integer counterClass;

    @Column(name = "AntivirusYes", type = "UInt8")
    private Integer antivirusYes;

    @Column(name = "BrowserInfo", type = "String")
    private String browserInfo;

    @Column(name = "URL", type = "String")
    private String URL;

    @Column(name = "FuniqID", type = "UInt64")
    private BigInteger funiqID;

    @Column(name = "Hit", type = "UInt64")
    private BigInteger hit;

    @Column(name = "Part", type = "UInt16")
    private Integer part;

    @Column(name = "Checksum", type = "UInt32")
    private Long checksum;

    @Column(name = "Data", type = "String")
    private ByteString data;

    @Column(name = "Type", type = "UInt8")
    private Integer type;

    @Column(name = "SourceID", type = "String")
    private String sourceID;

    @Column(name = "SeqNo", type = "UInt64")
    private BigInteger seqNo;

    @Column(name = "Topic", type = "String")
    private String topic;

    @Column(name = "Partition", type = "UInt16")
    private Integer partition;

    @Column(name = "Offset", type = "UInt64")
    private BigInteger offset;

    @Column(name = "CTime", type = "UInt32")
    private Long CTime;

    @Column(name = "WTime", type = "UInt32")
    private Long WTime;

    private RecorderProto.BufferWrapper unserializedData;

    public WebVisorLog() {
    }

    public WebVisorLog(WebVisorLog webVisorLog) {
        this.counterID = webVisorLog.counterID;
        this.uniqID = webVisorLog.uniqID;
        this.eventTime = webVisorLog.eventTime;
        this.counterClass = webVisorLog.counterClass;
        this.antivirusYes = webVisorLog.antivirusYes;
        this.browserInfo = webVisorLog.browserInfo;
        this.URL = webVisorLog.URL;
        this.funiqID = webVisorLog.funiqID;
        this.hit = webVisorLog.hit;
        this.part = webVisorLog.part;
        this.checksum = webVisorLog.checksum;
        this.data = webVisorLog.data;
        this.type = webVisorLog.type;
        this.sourceID = webVisorLog.sourceID;
        this.seqNo = webVisorLog.seqNo;
        this.topic = webVisorLog.topic;
        this.partition = webVisorLog.partition;
        this.offset = webVisorLog.offset;
        this.CTime = webVisorLog.CTime;
        this.WTime = webVisorLog.WTime;
        this.unserializedData = webVisorLog.unserializedData;
    }

    public Long getCounterID() {
        return counterID;
    }

    public void setCounterID(Long counterID) {
        this.counterID = counterID;
    }

    public WebVisorLog withCounterID(Long counterID) {
        this.counterID = counterID;
        return this;
    }

    public BigInteger getUniqID() {
        return uniqID;
    }

    public void setUniqID(BigInteger uniqID) {
        this.uniqID = uniqID;
    }

    public WebVisorLog withUniqID(BigInteger uniqID) {
        this.uniqID = uniqID;
        return this;
    }

    public Long getEventTime() {
        return eventTime;
    }

    public void setEventTime(Long eventTime) {
        this.eventTime = eventTime;
    }

    public WebVisorLog withEventTime(Long eventTime) {
        this.eventTime = eventTime;
        return this;
    }

    public Integer getCounterClass() {
        return counterClass;
    }

    public void setCounterClass(Integer counterClass) {
        this.counterClass = counterClass;
    }

    public WebVisorLog withCounterClass(Integer counterClass) {
        this.counterClass = counterClass;
        return this;
    }

    public Integer getAntivirusYes() {
        return antivirusYes;
    }

    public void setAntivirusYes(Integer antivirusYes) {
        this.antivirusYes = antivirusYes;
    }

    public WebVisorLog withAntivirusYes(Integer antivirusYes) {
        this.antivirusYes = antivirusYes;
        return this;
    }

    public String getBrowserInfo() {
        return browserInfo;
    }

    public void setBrowserInfo(String browserInfo) {
        this.browserInfo = browserInfo;
    }

    public WebVisorLog withBrowserInfo(String browserInfo) {
        this.browserInfo = browserInfo;
        return this;
    }

    public String getURL() {
        return URL;
    }

    public void setURL(String URL) {
        this.URL = URL;
    }

    public WebVisorLog withURL(String URL) {
        this.URL = URL;
        return this;
    }

    public BigInteger getFuniqID() {
        return funiqID;
    }

    public void setFuniqID(BigInteger funiqID) {
        this.funiqID = funiqID;
    }

    public WebVisorLog withFuniqID(BigInteger funiqID) {
        this.funiqID = funiqID;
        return this;
    }

    public BigInteger getHit() {
        return hit;
    }

    public void setHit(BigInteger hit) {
        this.hit = hit;
    }

    public WebVisorLog withHit(BigInteger hit) {
        this.hit = hit;
        return this;
    }

    public Integer getPart() {
        return part;
    }

    public void setPart(Integer part) {
        this.part = part;
    }

    public WebVisorLog withPart(Integer part) {
        this.part = part;
        return this;
    }

    public Long getChecksum() {
        return checksum;
    }

    public void setChecksum(Long checksum) {
        this.checksum = checksum;
    }

    public WebVisorLog withChecksum(Long checksum) {
        this.checksum = checksum;
        return this;
    }

    public ByteString getData() {
        return data;
    }

    public void setData(ByteString data) {
        this.data = data;
    }

    public WebVisorLog withData(ByteString data) {
        this.data = data;
        return this;
    }

    public Integer getType() {
        return type;
    }

    public void setType(Integer type) {
        this.type = type;
    }

    public WebVisorLog withType(Integer type) {
        this.type = type;
        return this;
    }

    public String getSourceID() {
        return sourceID;
    }

    public void setSourceID(String sourceID) {
        this.sourceID = sourceID;
    }

    public WebVisorLog withSourceID(String sourceID) {
        this.sourceID = sourceID;
        return this;
    }

    public BigInteger getSeqNo() {
        return seqNo;
    }

    public void setSeqNo(BigInteger seqNo) {
        this.seqNo = seqNo;
    }

    public WebVisorLog withSeqNo(BigInteger seqNo) {
        this.seqNo = seqNo;
        return this;
    }

    public String getTopic() {
        return topic;
    }

    public void setTopic(String topic) {
        this.topic = topic;
    }

    public WebVisorLog withTopic(String topic) {
        this.topic = topic;
        return this;
    }

    public Integer getPartition() {
        return partition;
    }

    public void setPartition(Integer partition) {
        this.partition = partition;
    }

    public WebVisorLog withPartition(Integer partition) {
        this.partition = partition;
        return this;
    }

    public BigInteger getOffset() {
        return offset;
    }

    public void setOffset(BigInteger offset) {
        this.offset = offset;
    }

    public WebVisorLog withOffset(BigInteger offset) {
        this.offset = offset;
        return this;
    }

    public Long getCTime() {
        return CTime;
    }

    public void setCTime(Long CTime) {
        this.CTime = CTime;
    }

    public WebVisorLog withCTime(Long CTime) {
        this.CTime = CTime;
        return this;
    }

    public Long getWTime() {
        return WTime;
    }

    public void setWTime(Long WTime) {
        this.WTime = WTime;
    }

    public WebVisorLog withWTime(Long WTime) {
        this.WTime = WTime;
        return this;
    }

    public RecorderProto.BufferWrapper getUnserializedData() {
        return unserializedData;
    }

    public void setUnserializedData(RecorderProto.BufferWrapper unserializedData) {
        this.unserializedData = unserializedData;
    }

    public WebVisorLog withUnserializedData(RecorderProto.BufferWrapper unserializedData) {
        this.unserializedData = unserializedData;
        return this;
    }

    @Override
    public long getTime() {
        return 0;
    }

    @Override
    public ChunkDescriptor getInsertDescr() {
        return () -> stream(WebVisorLog.class.getDeclaredFields())
                .map(field -> field.getAnnotation(Column.class).name())
                .toArray(String[]::new);
    }

    @Override
    public void dumpFields(@NotNull CommandOutput output) {
        stream(WebVisorLog.class.getDeclaredFields())
                .forEach(field -> {
                    try {
                        if (isColumn(field)) {
                            output.out(Serialization.objectToBinary(field.get(this), field.getType(), field.getAnnotation(Column.class).type()));
                        }
                    } catch (IllegalAccessException e) {
                        propagate(e);
                    }
                });
    }

    public static String getCreateTableTemplate() {
        return format("CREATE TABLE IF NOT EXISTS %%s.%%s (%s) ENGINE = StripeLog;",
                stream(WebVisorLog.class.getDeclaredFields())
                        .filter(WebVisorLog::isColumn)
                        .map(field -> format("`%s` %s", field.getAnnotation(Column.class).name(), field.getAnnotation(Column.class).type()))
                        .collect(joining(", ")));
    }

    private static boolean isColumn(Field field) {
        return field.getAnnotation(Column.class) != null;
    }

    public byte[] toTskv() throws IOException {

        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        baos.write("tskv\ttskv_format=bs-watch-log\tlayerid=1".getBytes());

        if(getPart() != null) {
            baos.write(("\tpart=" + getPart().toString()).getBytes());
        }
        if(getHit() != null) {
            baos.write(("\thit=" + getHit().toString()).getBytes());
        }
        if (getCTime() != null) {
            baos.write(("\tunixtime=" + getCTime().toString()).getBytes());
        }
        if (getEventTime() != null) {
            baos.write(("\teventtime=" + getEventTime().toString()).getBytes());
        }
        if (getCounterID() != null) {
            baos.write(("\tcounterid=" + getCounterID().toString()).getBytes());
        }
        if (getUniqID() != null) {
            baos.write(("\tuniqid=" + getUniqID().toString()).getBytes());
        }
        if (getCounterClass() != null) {
            baos.write(("\tcounterclass=" + getCounterClass().toString()).getBytes());
        }
        if (getAntivirusYes() != null) {
            baos.write(("\tantivirusyes=" + getAntivirusYes().toString()).getBytes());
        }
        if (getBrowserInfo() != null) {
            baos.write(("\tbrowserinfo=" + getBrowserInfo()).getBytes());
        }
        if (getURL() != null) {
            baos.write(("\turl=" + getURL()).getBytes());
        }
        if (getChecksum() != null) {
            baos.write(("\tchecksum=" + getChecksum().toString()).getBytes());
        }
        if (getType() != null) {
            baos.write(("\ttype=" + getType().toString()).getBytes());
        }
        if (getData() != null) {
            baos.write("\tdata=".getBytes());
            baos.write(escape(getData().toBytes()));
        }
        baos.write("\n".getBytes());
        return baos.toByteArray();
    }

    private byte[] escape(byte[] data) throws IOException {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        for(byte b : data) {
            baos.write(escapeByte(b));
        }
        return baos.toByteArray();
    }

    private byte[] escapeByte(byte b) {
        switch (b) {
            case Ascii.BEL:
                return "\\a".getBytes();
            case '\b':
                return "\\b".getBytes();
            case Ascii.ESC:
                return "\\e".getBytes();
            case '\f':
                return "\\f".getBytes();
            case '\n':
                return "\\n".getBytes();
            case '\r':
                return "\\r".getBytes();
            case '\t':
                return "\\t".getBytes();
            case Ascii.VT:
                return "\\v".getBytes();
            case '\0':
                return "\\0".getBytes();
            case '\\':
                return "\\\\".getBytes();
            case '\"':
                return "\\\"".getBytes();
            default:
                return new byte[] {b};
        }
    }

    @Override
    public String toString() {
        return "WebVisorLog{" +
                "counterID=" + counterID +
                ", uniqID=" + uniqID +
                ", eventTime=" + eventTime +
                ", counterClass=" + counterClass +
                ", antivirusYes=" + antivirusYes +
                ", browserInfo='" + browserInfo + '\'' +
                ", URL='" + URL + '\'' +
                ", funiqID=" + funiqID +
                ", hit=" + hit +
                ", part=" + part +
                ", checksum=" + checksum +
                ", data=" + data +
                ", type=" + type +
                ", sourceID='" + sourceID + '\'' +
                ", seqNo=" + seqNo +
                ", topic='" + topic + '\'' +
                ", partition=" + partition +
                ", offset=" + offset +
                ", CTime=" + CTime +
                ", WTime=" + WTime +
                ", unserializedData=" + unserializedData +
                '}';
    }
}
