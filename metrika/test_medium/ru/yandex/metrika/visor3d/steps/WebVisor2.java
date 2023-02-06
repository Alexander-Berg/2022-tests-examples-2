package ru.yandex.metrika.visor3d.steps;

import java.math.BigInteger;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Objects;

import org.jetbrains.annotations.NotNull;

import ru.yandex.autotests.metrika.commons.beans.Column;
import ru.yandex.autotests.metrika.commons.beans.Serialization;
import ru.yandex.metrika.dbclients.mysql.ErrorCountMapper;
import ru.yandex.metrika.dbclients.mysql.ErrorCountMapperImpl;
import ru.yandex.metrika.util.chunk.ChunkDescriptor;
import ru.yandex.metrika.util.chunk.ChunkRow;
import ru.yandex.metrika.util.chunk.output.CommandOutput;
import ru.yandex.metrika.visord.process.clickhouse.ClickHouseFinalEvent;

import static com.google.common.base.Throwables.propagate;
import static java.util.Arrays.stream;

public class WebVisor2 implements ChunkRow {

    @Column(name = "CounterID", type = "UInt32")
    private Long counterID;

    @Column(name = "UserID", type = "UInt64")
    private BigInteger userID;

    @Column(name = "HID", type = "UInt32")
    private Long HID;

    @Column(name = "EventTime", type = "UInt32")
    private Long eventTime;

    @Column(name = "SeqNum", type = "UInt16")
    private Integer seqNum;

    @Column(name = "Activity", type = "UInt32")
    private Long activity;

    @Column(name = "Duration", type = "UInt32")
    private Long duration;

    @Column(name = "UniqContent", type = "UInt8")
    private Integer uniqContent;

    @Column(name = "HasEof", type = "UInt8")
    private Integer hasEof;

    @Column(name = "HasSubmits", type = "UInt8")
    private Integer hasSubmits;

    @Column(name = "TotalActivity", type = "UInt32")
    private Long totalActivity;

    public WebVisor2() {
    }

    public WebVisor2(WebVisor2 webVisor2) {
        this.counterID = webVisor2.counterID;
        this.userID = webVisor2.userID;
        this.HID = webVisor2.HID;
        this.eventTime = webVisor2.eventTime;
        this.seqNum = webVisor2.seqNum;
        this.activity = webVisor2.activity;
        this.duration = webVisor2.duration;
        this.uniqContent = webVisor2.uniqContent;
        this.hasEof = webVisor2.hasEof;
        this.hasSubmits = webVisor2.hasSubmits;
        this.totalActivity = webVisor2.totalActivity;
    }

    public WebVisor2(ResultSet resultSet) throws SQLException {
        this.counterID = resultSet.getLong("CounterID");
        this.userID = new BigInteger(resultSet.getString("UserID"));
        this.HID = resultSet.getLong("HID");
        this.eventTime = resultSet.getLong("EventTime");
        this.seqNum = resultSet.getInt("SeqNum");
        this.activity = resultSet.getLong("Activity");
        this.duration = resultSet.getLong("Duration");
        this.uniqContent = resultSet.getInt("UniqContent");
        this.hasEof = resultSet.getInt("HasEof");
        this.hasSubmits = resultSet.getInt("HasSubmits");
        this.totalActivity = resultSet.getLong("TotalActivity");
    }

    public WebVisor2(ClickHouseFinalEvent p) {
        this.counterID = Long.valueOf(Integer.toUnsignedString(p.getCounterId()));
        this.userID = new BigInteger(Long.toUnsignedString(p.getUserId()));
        this.HID = Long.valueOf(Integer.toUnsignedString(p.getClientHitId()));
        this.eventTime = p.getEventTime();
        this.seqNum = p.getSeqNumber();
        this.activity = 0L; //fix for old wv1 test data
        this.duration = Long.valueOf(Integer.toUnsignedString(p.getDuration()));
        this.uniqContent = p.isUniqContent()?1:0;
        this.hasEof = p.getHasEof();
        this.hasSubmits = p.isHasSubmits()?1:0;
        this.totalActivity = Long.valueOf(Integer.toUnsignedString(p.getTotalActivity()));
    }

    public Long getCounterID() {
        return counterID;
    }

    public void setCounterID(Long counterID) {
        this.counterID = counterID;
    }

    public WebVisor2 withCounterID(Long counterID) {
        this.counterID = counterID;
        return this;
    }

    public BigInteger getUserID() {
        return userID;
    }

    public void setUserID(BigInteger userID) {
        this.userID = userID;
    }

    public WebVisor2 withUserID(BigInteger userID) {
        this.userID = userID;
        return this;
    }

    public Long getHID() {
        return HID;
    }

    public void setHID(Long HID) {
        this.HID = HID;
    }

    public WebVisor2 withHID(Long HID) {
        this.HID = HID;
        return this;
    }

    public Long getEventTime() {
        return eventTime;
    }

    public void setEventTime(Long eventTime) {
        this.eventTime = eventTime;
    }

    public WebVisor2 withEventTime(Long eventTime) {
        this.eventTime = eventTime;
        return this;
    }

    public Integer getSeqNum() {
        return seqNum;
    }

    public void setSeqNum(Integer seqNum) {
        this.seqNum = seqNum;
    }

    public WebVisor2 withSeqNum(Integer seqNum) {
        this.seqNum = seqNum;
        return this;
    }

    public Long getActivity() {
        return activity;
    }

    public void setActivity(Long activity) {
        this.activity = activity;
    }

    public WebVisor2 withActivity(Long activity) {
        this.activity = activity;
        return this;
    }

    public Long getDuration() {
        return duration;
    }

    public void setDuration(Long duration) {
        this.duration = duration;
    }

    public WebVisor2 withDuration(Long duration) {
        this.duration = duration;
        return this;
    }

    public Integer getUniqContent() {
        return uniqContent;
    }

    public void setUniqContent(Integer uniqContent) {
        this.uniqContent = uniqContent;
    }

    public WebVisor2 withUniqContent(Integer uniqContent) {
        this.uniqContent = uniqContent;
        return this;
    }

    public Integer getHasEof() {
        return hasEof;
    }

    public void setHasEof(Integer hasEof) {
        this.hasEof = hasEof;
    }

    public WebVisor2 withHasEof(Integer hasEof) {
        this.hasEof = hasEof;
        return this;
    }

    public Integer getHasSubmits() {
        return hasSubmits;
    }

    public void setHasSubmits(Integer hasSubmits) {
        this.hasSubmits = hasSubmits;
    }

    public WebVisor2 withHasSubmits(Integer hasSubmits) {
        this.hasSubmits = hasSubmits;
        return this;
    }

    public Long getTotalActivity() {
        return totalActivity;
    }

    public void setTotalActivity(Long totalActivity) {
        this.totalActivity = totalActivity;
    }

    public WebVisor2 withTotalActivity(Long totalActivity) {
        this.totalActivity = totalActivity;
        return this;
    }

    @Override
    public long getTime() {
        return 0;
    }

    @Override
    public ChunkDescriptor getInsertDescr() {
        return () -> stream(WebVisor2.class.getDeclaredFields())
                .map(field -> field.getAnnotation(Column.class).name())
                .toArray(String[]::new);
    }

    @Override
    public void dumpFields(@NotNull CommandOutput output) {
        stream(WebVisor2.class.getDeclaredFields())
                .forEach(field -> {
                    try {
                        output.out(Serialization.objectToBinary(field.get(this), field.getType(), field.getAnnotation(Column.class).type()));
                    } catch (IllegalAccessException e) {
                        propagate(e);
                    }
                });
    }

    public static ErrorCountMapper<WebVisor2> getRowMapper() {
        return new ErrorCountMapperImpl<WebVisor2>((resultSet, rowNum) -> new WebVisor2(resultSet));
    }

    @Override
    public int hashCode() {
        return Objects.hash(counterID, userID, HID, eventTime, seqNum, activity, duration, uniqContent, hasEof, hasSubmits, totalActivity);
    }

    @Override
    public String toString() {
        return "WebVisor2{" +
                "counterID=" + counterID +
                ", userID=" + userID +
                ", HID=" + HID +
                ", eventTime=" + eventTime +
                ", seqNum=" + seqNum +
                ", activity=" + activity +
                ", duration=" + duration +
                ", uniqContent=" + uniqContent +
                ", hasEof=" + hasEof +
                ", hasSubmits=" + hasSubmits +
                ", totalActivity=" + totalActivity +
                '}';
    }
}
