package ru.yandex.metrika.mobmet.crash.decoder.steps;

import java.math.BigInteger;
import java.util.Collections;
import java.util.List;

/**
 * Поля Clickhouse заполняемые mobmet-crash-decoder.
 * Некоторые поля гигантские, поэтому раскладываем маленькие поля в processing_fields.json,
 * а большие в отдельные файлы.
 */
public class CrashProcessingFields {

    // поля из processing_fields.json
    private BigInteger eventID;
    private String crashEncodeType = "unknown";
    private String decodeStatus = "unknown";
    private BigInteger decodeGroupId = BigInteger.valueOf(0);
    private String osBuild = "";
    private String decodeRequiredSymbolsId = "";
    private List<String> decodeUsedSymbolsIds = Collections.emptyList();
    private List<String> decodeMissedSymbolsIds = Collections.emptyList();
    private List<String> decodeUsedSystemSymbolsIds = Collections.emptyList();
    private List<String> decodeMissedSystemSymbolsIds = Collections.emptyList();
    private String crashReasonType = "";
    private String crashReason = "";
    private String crashReasonMessage = "";
    private String crashBinaryName = "";
    private String crashFileName = "";
    private String crashMethodName = "";
    private Long crashSourceLine = 0L;
    // поля из дополнительных файлов
    private String crashDecodedEventValue = "";
    private String crashThreadContent = "";
    private long apiKey = 0;
    private long decodeOriginalAPIKey = 0;
    private long decodeOriginalEventID = 0;

    public BigInteger getEventID() {
        return eventID;
    }

    public void setEventID(BigInteger eventID) {
        this.eventID = eventID;
    }

    public String getCrashEncodeType() {
        return crashEncodeType;
    }

    public void setCrashEncodeType(String crashEncodeType) {
        this.crashEncodeType = crashEncodeType;
    }

    public String getDecodeStatus() {
        return decodeStatus;
    }

    public void setDecodeStatus(String decodeStatus) {
        this.decodeStatus = decodeStatus;
    }

    public BigInteger getDecodeGroupId() {
        return decodeGroupId;
    }

    public void setDecodeGroupId(BigInteger decodeGroupId) {
        this.decodeGroupId = decodeGroupId;
    }

    public String getOsBuild() {
        return osBuild;
    }

    public void setOsBuild(String osBuild) {
        this.osBuild = osBuild;
    }

    public String getDecodeRequiredSymbolsId() {
        return decodeRequiredSymbolsId;
    }

    public void setDecodeRequiredSymbolsId(String decodeRequiredSymbolsId) {
        this.decodeRequiredSymbolsId = decodeRequiredSymbolsId;
    }

    public List<String> getDecodeUsedSymbolsIds() {
        return decodeUsedSymbolsIds;
    }

    public void setDecodeUsedSymbolsIds(List<String> decodeUsedSymbolsIds) {
        this.decodeUsedSymbolsIds = decodeUsedSymbolsIds;
    }

    public List<String> getDecodeMissedSymbolsIds() {
        return decodeMissedSymbolsIds;
    }

    public void setDecodeMissedSymbolsIds(List<String> decodeMissedSymbolsIds) {
        this.decodeMissedSymbolsIds = decodeMissedSymbolsIds;
    }

    public List<String> getDecodeUsedSystemSymbolsIds() {
        return decodeUsedSystemSymbolsIds;
    }

    public void setDecodeUsedSystemSymbolsIds(List<String> decodeUsedSystemSymbolsIds) {
        this.decodeUsedSystemSymbolsIds = decodeUsedSystemSymbolsIds;
    }

    public List<String> getDecodeMissedSystemSymbolsIds() {
        return decodeMissedSystemSymbolsIds;
    }

    public void setDecodeMissedSystemSymbolsIds(List<String> decodeMissedSystemSymbolsIds) {
        this.decodeMissedSystemSymbolsIds = decodeMissedSystemSymbolsIds;
    }

    public String getCrashReasonType() {
        return crashReasonType;
    }

    public void setCrashReasonType(String crashReasonType) {
        this.crashReasonType = crashReasonType;
    }

    public String getCrashReason() {
        return crashReason;
    }

    public void setCrashReason(String crashReason) {
        this.crashReason = crashReason;
    }

    public String getCrashReasonMessage() {
        return crashReasonMessage;
    }

    public void setCrashReasonMessage(String crashReasonMessage) {
        this.crashReasonMessage = crashReasonMessage;
    }

    public String getCrashBinaryName() {
        return crashBinaryName;
    }

    public void setCrashBinaryName(String crashBinaryName) {
        this.crashBinaryName = crashBinaryName;
    }

    public String getCrashFileName() {
        return crashFileName;
    }

    public void setCrashFileName(String crashFileName) {
        this.crashFileName = crashFileName;
    }

    public String getCrashMethodName() {
        return crashMethodName;
    }

    public void setCrashMethodName(String crashMethodName) {
        this.crashMethodName = crashMethodName;
    }

    public Long getCrashSourceLine() {
        return crashSourceLine;
    }

    public void setCrashSourceLine(Long crashSourceLine) {
        this.crashSourceLine = crashSourceLine;
    }

    public String getCrashDecodedEventValue() {
        return crashDecodedEventValue;
    }

    public void setCrashDecodedEventValue(String crashDecodedEventValue) {
        this.crashDecodedEventValue = crashDecodedEventValue;
    }

    public String getCrashThreadContent() {
        return crashThreadContent;
    }

    public void setCrashThreadContent(String crashThreadContent) {
        this.crashThreadContent = crashThreadContent;
    }

    public long getApiKey() {
        return apiKey;
    }

    public void setApiKey(long apiKey) {
        this.apiKey = apiKey;
    }

    public long getDecodeOriginalAPIKey() {
        return decodeOriginalAPIKey;
    }

    public void setDecodeOriginalAPIKey(long decodeOriginalAPIKey) {
        this.decodeOriginalAPIKey = decodeOriginalAPIKey;
    }

    public long getDecodeOriginalEventID() {
        return decodeOriginalEventID;
    }

    public void setDecodeOriginalEventID(long decodeOriginalEventID) {
        this.decodeOriginalEventID = decodeOriginalEventID;
    }

}
