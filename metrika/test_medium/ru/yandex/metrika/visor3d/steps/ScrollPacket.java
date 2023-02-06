package ru.yandex.metrika.visor3d.steps;

import java.math.BigInteger;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Arrays;
import java.util.Objects;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonProperty;
import org.jetbrains.annotations.NotNull;

import ru.yandex.autotests.metrika.commons.beans.Column;
import ru.yandex.autotests.metrika.commons.beans.Serialization;
import ru.yandex.metrika.common.test.medium.ByteString;
import ru.yandex.metrika.dbclients.mysql.ErrorCountMapper;
import ru.yandex.metrika.dbclients.mysql.ErrorCountMapperImpl;
import ru.yandex.metrika.util.chunk.ChunkDescriptor;
import ru.yandex.metrika.util.chunk.ChunkRow;
import ru.yandex.metrika.util.chunk.output.CommandOutput;

import static com.google.common.base.Throwables.propagate;
import static java.util.Arrays.stream;

public class ScrollPacket implements ChunkRow {

    @JsonProperty("EventDate")
    @Column(name = "EventDate", type = "String")
    private String eventDate;

    @JsonProperty("CounterID")
    @Column(name = "CounterID", type = "UInt32")
    private long counterId;

    @JsonProperty("HID")
    @Column(name = "HID", type = "UInt32")
    private long hid;

    @JsonProperty("UserID")
    @Column(name = "UserID", type = "UInt64")
    private BigInteger userId;

    @JsonProperty("URLNormalizedHash")
    @Column(name = "URLNormalizedHash", type = "UInt64")
    private BigInteger urlNormalizedHash;

    @JsonProperty("URLNormalized")
    @Column(name = "URLNormalized", type = "String")
    private String urlNormalized;

    @JsonProperty("Sec")
    @Column(name = "Sec", type = "UInt16")
    private int sec;

    @JsonProperty("BufferType")
    @Column(name = "BufferType", type = "UInt8")
    private int bufferType;

    @JsonIgnore
    @Column(name = "EventData", type = "String")
    private ByteString eventData;

    @JsonProperty("ScrollCount")
    @Column(name = "ScrollCount", type = "UInt32")
    private long scrollCount;

    @JsonProperty("EventData")
    private byte[] events;

    private String table;

    public ScrollPacket() {
    }

    public ScrollPacket(ScrollPacket scrollPacket) {
        this.eventDate = scrollPacket.eventDate;
        this.counterId = scrollPacket.counterId;
        this.hid = scrollPacket.hid;
        this.userId = scrollPacket.userId;
        this.urlNormalizedHash = scrollPacket.urlNormalizedHash;
        this.urlNormalized = scrollPacket.urlNormalized;
        this.sec = scrollPacket.sec;
        this.bufferType = scrollPacket.bufferType;
        this.eventData = scrollPacket.eventData;
        this.scrollCount = scrollPacket.scrollCount;
        this.events = scrollPacket.events;
        this.table = scrollPacket.table;
    }

    public ScrollPacket(ResultSet resultSet) throws SQLException {
        this.eventDate = resultSet.getString("EventDate");
        this.counterId = resultSet.getLong("CounterID");
        this.hid = resultSet.getLong("HID");
        this.userId = new BigInteger(resultSet.getString("UserID"));
        this.urlNormalizedHash = new BigInteger(resultSet.getString("URLNormalizedHash"));
        this.urlNormalized = resultSet.getString("URLNormalized");
        this.sec = resultSet.getInt("Sec");
        this.bufferType = resultSet.getInt("BufferType");
        this.eventData = new ByteString(resultSet.getBytes("EventData"));
        this.scrollCount = resultSet.getLong("ScrollCount");
    }

    public String getEventDate() {
        return eventDate;
    }

    public void setEventDate(String eventDate) {
        this.eventDate = eventDate;
    }

    public ScrollPacket withEventDate(String eventDate) {
        this.eventDate = eventDate;
        return this;
    }

    public long getCounterId() {
        return counterId;
    }

    public void setCounterId(long counterId) {
        this.counterId = counterId;
    }

    public ScrollPacket withCounterId(long counterId) {
        this.counterId = counterId;
        return this;
    }

    public long getHid() {
        return hid;
    }

    public void setHid(long hid) {
        this.hid = hid;
    }

    public ScrollPacket withHid(long hid) {
        this.hid = hid;
        return this;
    }

    public BigInteger getUserId() {
        return userId;
    }

    public void setUserId(BigInteger userId) {
        this.userId = userId;
    }

    public ScrollPacket withUserId(BigInteger userId) {
        this.userId = userId;
        return this;
    }

    public BigInteger getUrlNormalizedHash() {
        return urlNormalizedHash;
    }

    public void setUrlNormalizedHash(BigInteger urlNormalizedHash) {
        this.urlNormalizedHash = urlNormalizedHash;
    }

    public ScrollPacket withUrlNormalizedHash(BigInteger urlNormalizedHash) {
        this.urlNormalizedHash = urlNormalizedHash;
        return this;
    }

    public String getUrlNormalized() {
        return urlNormalized;
    }

    public void setUrlNormalized(String urlNormalized) {
        this.urlNormalized = urlNormalized;
    }

    public ScrollPacket withUrlNormalized(String urlNormalized) {
        this.urlNormalized = urlNormalized;
        return this;
    }

    public int getSec() {
        return sec;
    }

    public void setSec(int sec) {
        this.sec = sec;
    }

    public ScrollPacket withSec(int sec) {
        this.sec = sec;
        return this;
    }

    public int getBufferType() {
        return bufferType;
    }

    public void setBufferType(int bufferType) {
        this.bufferType = bufferType;
    }

    public ScrollPacket withBufferType(int bufferType) {
        this.bufferType = bufferType;
        return this;
    }

    public ByteString getEventData() {
        if (eventData != null && !"".equals(eventData.toString()))
            return eventData;
        else
            return events == null ? null : new ByteString(events);
    }

    public void setEventData(ByteString eventData) {
        this.eventData = eventData;
    }

    public ScrollPacket withEventData(ByteString eventData) {
        this.eventData = eventData;
        return this;
    }

    public long getScrollCount() {
        return scrollCount;
    }

    public void setScrollCount(long scrollCount) {
        this.scrollCount = scrollCount;
    }

    public ScrollPacket withScrollCount(long scrollCount) {
        this.scrollCount = scrollCount;
        return this;
    }

    public byte[] getEvents() {
        return events;
    }

    public void setEvents(byte[] events) {
        this.events = events;
    }

    public ScrollPacket withEvents(byte[] events) {
        this.events = events;
        return this;
    }

    public String getTable() {
        return table;
    }

    public void setTable(String table) {
        this.table = table;
    }

    public ScrollPacket withTable(String table) {
        this.table = table;
        return this;
    }

    @Override
    public long getTime() {
        return 0;
    }

    @Override
    public ChunkDescriptor getInsertDescr() {
        return () -> stream(ScrollPacket.class.getDeclaredFields())
                .map(field -> field.getAnnotation(Column.class).name())
                .toArray(String[]::new);
    }

    @Override
    public void dumpFields(@NotNull CommandOutput output) {
        stream(ScrollPacket.class.getDeclaredFields())
                .forEach(field -> {
                    try {
                        output.out(Serialization.objectToBinary(field.get(this), field.getType(), field.getAnnotation(Column.class).type()));
                    } catch (IllegalAccessException e) {
                        propagate(e);
                    }
                });
    }

    public static ErrorCountMapper<ScrollPacket> getRowMapper() {
        return new ErrorCountMapperImpl<ScrollPacket>((resultSet, rowNum) -> new ScrollPacket(resultSet));
    }

    @Override
    public int hashCode() {
        return Objects.hash(counterId, hid, userId, sec, scrollCount);
    }

    @Override
    public String toString() {
        return "ScrollPacket{" +
                "eventDate='" + eventDate + '\'' +
                ", counterId=" + counterId +
                ", hid=" + hid +
                ", userId=" + userId +
                ", urlNormalizedHash=" + urlNormalizedHash +
                ", urlNormalized='" + urlNormalized + '\'' +
                ", sec=" + sec +
                ", bufferType=" + bufferType +
                ", eventData=" + eventData +
                ", scrollCount=" + scrollCount +
                ", events=" + Arrays.toString(events) +
                ", table='" + table + '\'' +
                '}';
    }
}
