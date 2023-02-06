package ru.yandex.metrika.visor3d.steps;

import java.util.Arrays;
import java.util.Objects;

import ru.yandex.autotests.metrika.commons.beans.Column;
import ru.yandex.inside.yt.kosher.impl.ytree.object.annotation.YTreeField;
import ru.yandex.inside.yt.kosher.impl.ytree.object.annotation.YTreeObject;

@YTreeObject
public class EventPacket {

    @YTreeField(key = "userIdHash")
    @Column(type = "int64", order = "ascending")
    private Long userIdHash;

    @YTreeField(key = "counterId")
    @Column(type = "int64", order = "ascending")
    private Long counterId;

    @YTreeField(key = "hit")
    @Column(type = "int64", order = "ascending")
    private Long hit;

    @YTreeField(key = "date")
    @Column(type = "string", order = "ascending")
    private String date;

    @YTreeField(key = "part")
    @Column(type = "int64", order = "ascending")
    private Integer part;

    @YTreeField(key = "index")
    @Column(type = "int64", order = "ascending")
    private Integer index;

    @YTreeField(key = "bufferType")
    @Column(type = "int64", order = "ascending")
    private Integer bufferType;

    @YTreeField(key = "userId")
    @Column(type = "int64")
    private Long userId;

    @YTreeField(key = "type")
    @Column(type = "string")
    private String type;

    @YTreeField(key = "serialization")
    @Column(type = "int64")
    private Integer serialization;

    @YTreeField(key = "compression")
    @Column(type = "int64")
    private Integer compression;

    @YTreeField(key = "data")
    @Column(type = "string")
    private byte[] data;

    @YTreeField(key = "dataPart")
    @Column(type = "int64")
    private Integer dataPart;

    @YTreeField(key = "isDataLastPart")
    @Column(type = "boolean")
    private Boolean isDataLastPart;

    @YTreeField(key = "time1")
    @Column(type = "int64")
    private Integer time1;

    @YTreeField(key = "time2")
    @Column(type = "int64")
    private Integer time2;

    @YTreeField(key = "time3")
    @Column(type = "int64")
    private Integer time3;

    @YTreeField(key = "time4")
    @Column(type = "int64")
    private Integer time4;

    @YTreeField(key = "codeVersion")
    @Column(type = "int64")
    private long codeVersion;

    @YTreeField(key = "codeFeatures")
    @Column(type = "string")
    private String codeFeatures;


    public EventPacket() {
    }

    public long getCodeVersion() {
        return codeVersion;
    }

    public void setCodeVersion(long codeVersion) {
        this.codeVersion = codeVersion;
    }

    public String getCodeFeatures() {
        return codeFeatures;
    }

    public void setCodeFeatures(String codeFeatures) {
        this.codeFeatures = codeFeatures;
    }

    public Long getUserIdHash() {
        return userIdHash;
    }

    public void setUserIdHash(Long userIdHash) {
        this.userIdHash = userIdHash;
    }

    public EventPacket withUserIdHash(Long userIdHash) {
        this.userIdHash = userIdHash;
        return this;
    }

    public Long getCounterId() {
        return counterId;
    }

    public void setCounterId(Long counterId) {
        this.counterId = counterId;
    }

    public EventPacket withCounterId(Long counterId) {
        this.counterId = counterId;
        return this;
    }

    public Long getHit() {
        return hit;
    }

    public void setHit(Long hit) {
        this.hit = hit;
    }

    public EventPacket withHit(Long hit) {
        this.hit = hit;
        return this;
    }

    public String getDate() {
        return date;
    }

    public void setDate(String date) {
        this.date = date;
    }

    public EventPacket withDate(String date) {
        this.date = date;
        return this;
    }

    public Integer getPart() {
        return part;
    }

    public void setPart(Integer part) {
        this.part = part;
    }

    public EventPacket withPart(Integer part) {
        this.part = part;
        return this;
    }

    public Integer getIndex() {
        return index;
    }

    public void setIndex(Integer index) {
        this.index = index;
    }

    public EventPacket withIndex(Integer index) {
        this.index = index;
        return this;
    }

    public Integer getBufferType() {
        return bufferType;
    }

    public void setBufferType(Integer bufferType) {
        this.bufferType = bufferType;
    }

    public EventPacket withBufferType(Integer bufferType) {
        this.bufferType = bufferType;
        return this;
    }

    public Long getUserId() {
        return userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

    public EventPacket withUserId(Long userId) {
        this.userId = userId;
        return this;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public EventPacket withType(String type) {
        this.type = type;
        return this;
    }

    public Integer getSerialization() {
        return serialization;
    }

    public void setSerialization(Integer serialization) {
        this.serialization = serialization;
    }

    public EventPacket withSerialization(Integer serialization) {
        this.serialization = serialization;
        return this;
    }

    public Integer getCompression() {
        return compression;
    }

    public void setCompression(Integer compression) {
        this.compression = compression;
    }

    public EventPacket withCompression(Integer compression) {
        this.compression = compression;
        return this;
    }

    public byte[] getData() {
        return data;
    }

    public void setData(byte[] data) {
        this.data = data;
    }

    public EventPacket withData(byte[] data) {
        this.data = data;
        return this;
    }

    public Integer getDataPart() {
        return dataPart;
    }

    public void setDataPart(Integer dataPart) {
        this.dataPart = dataPart;
    }

    public EventPacket withDataPart(Integer dataPart) {
        this.dataPart = dataPart;
        return this;
    }

    public Boolean getIsDataLastPart() {
        return isDataLastPart;
    }

    public void setIsDataLastPart(Boolean isDataLastPart) {
        this.isDataLastPart = isDataLastPart;
    }

    public EventPacket withIsDataLastPart(Boolean isDataLastPart) {
        this.isDataLastPart = isDataLastPart;
        return this;
    }

    public Integer getTime1() {
        return time1;
    }

    public void setTime1(Integer time1) {
        this.time1 = time1;
    }

    public EventPacket withTime1(Integer time1) {
        this.time1 = time1;
        return this;
    }

    public Integer getTime2() {
        return time2;
    }

    public void setTime2(Integer time2) {
        this.time2 = time2;
    }

    public EventPacket withTime2(Integer time2) {
        this.time2 = time2;
        return this;
    }

    public Integer getTime3() {
        return time3;
    }

    public void setTime3(Integer time3) {
        this.time3 = time3;
    }

    public EventPacket withTime3(Integer time3) {
        this.time3 = time3;
        return this;
    }

    public Integer getTime4() {
        return time4;
    }

    public void setTime4(Integer time4) {
        this.time4 = time4;
    }

    public EventPacket withTime4(Integer time4) {
        this.time4 = time4;
        return this;
    }

    @Override
    public int hashCode() {
        return Objects.hash(counterId, hit, part, index, bufferType, userId, dataPart, isDataLastPart, time1, time2, time3, time4, codeVersion, codeFeatures);
    }

    @Override
    public String toString() {
        return "EventPacket{" +
                "userIdHash=" + userIdHash +
                ", counterId=" + counterId +
                ", hit=" + hit +
                ", date='" + date + '\'' +
                ", part=" + part +
                ", index=" + index +
                ", bufferType=" + bufferType +
                ", userId=" + userId +
                ", type='" + type + '\'' +
                ", serialization=" + serialization +
                ", compression=" + compression +
                ", data=" + Arrays.toString(data) +
                ", dataPart=" + dataPart +
                ", isDataLastPart=" + isDataLastPart +
                ", time1=" + time1 +
                ", time2=" + time2 +
                ", time3=" + time3 +
                ", time4=" + time4 +
                ", codeVersion=" + codeVersion +
                ", codeFeatures='" + codeFeatures + '\'' +
                '}';
    }
}
