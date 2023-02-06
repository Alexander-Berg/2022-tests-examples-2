package ru.yandex.metrika.mobmet.crash.decoder.steps;

import java.math.BigInteger;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.stream.Stream;

import org.apache.commons.lang3.ArrayUtils;
import org.jetbrains.annotations.NotNull;
import org.joda.time.DateTime;

import ru.yandex.autotests.metrika.commons.beans.Column;
import ru.yandex.autotests.metrika.commons.beans.Serialization;
import ru.yandex.metrika.common.test.medium.ByteString;
import ru.yandex.metrika.common.test.medium.FixedString;
import ru.yandex.metrika.dbclients.mysql.ErrorCountMapper;
import ru.yandex.metrika.dbclients.mysql.ErrorCountMapperImpl;
import ru.yandex.metrika.util.chunk.ChunkDescriptor;
import ru.yandex.metrika.util.chunk.ChunkRow;
import ru.yandex.metrika.util.chunk.output.CommandOutput;

import static com.google.common.base.Throwables.propagate;
import static java.lang.String.format;
import static java.util.Arrays.stream;
import static java.util.stream.Collectors.joining;
import static ru.yandex.metrika.common.test.medium.MultiFormatter.dateFormatter;

public class MobileEvent implements ChunkRow {

    @Column(name = "APIKey", type = "UInt32")
    private Long APIKey;

    @Column(name = "APIKey128", type = "FixedString(36)")
    private FixedString APIKey128;

    @Column(name = "AttributionID", type = "UInt32")
    private Long attributionID;

    @Column(name = "AttributionIDUUIDHash", type = "UInt64")
    private BigInteger attributionIDUUIDHash;

    @Column(name = "StartDate", type = "Date")
    private DateTime startDate;

    @Column(name = "EventDate", type = "Date")
    private DateTime eventDate;

    @Column(name = "UUID", type = "String")
    private String UUID;

    @Column(name = "DeviceID", type = "String")
    private String deviceID;

    @Column(name = "UUIDHash", type = "UInt64")
    private BigInteger UUIDHash;

    @Column(name = "DeviceIDHash", type = "UInt64")
    private BigInteger deviceIDHash;

    @Column(name = "AppPlatform", type = "String")
    private String appPlatform;

    @Column(name = "OperatingSystem", type = "Enum8('unknown'=0, 'android'=1, 'ios'=2, 'windows'=3, 'macos'=4, 'linux'=5)")
    private String operatingSystem;

    @Column(name = "AppFramework", type = "UInt8")
    private Integer appFramework;

    @Column(name = "AppVersionName", type = "String")
    private String appVersionName;

    @Column(name = "AppBuildNumber", type = "UInt32")
    private Long appBuildNumber;

    @Column(name = "AppDebuggable", type = "Enum8('undefined'=-1, 'false'=0, 'true'=1)")
    private String appDebuggable;

    @Column(name = "KitVersion", type = "UInt32")
    private Long kitVersion;

    @Column(name = "Manufacturer", type = "String")
    private String manufacturer;

    @Column(name = "Model", type = "String")
    private String model;

    @Column(name = "OriginalManufacturer", type = "String")
    private String originalManufacturer;

    @Column(name = "OriginalModel", type = "String")
    private String originalModel;

    @Column(name = "OSVersion", type = "String")
    private String OSVersion;

    @Column(name = "OSApiLevel", type = "UInt32")
    private Long OSApiLevel;

    @Column(name = "ScreenWidth", type = "UInt32")
    private Long screenWidth;

    @Column(name = "ScreenHeight", type = "UInt32")
    private Long screenHeight;

    @Column(name = "ScreenDPI", type = "UInt32")
    private Long screenDPI;

    @Column(name = "ScaleFactor", type = "Float64")
    private java.lang.Double scaleFactor;

    @Column(name = "Imei", type = "Array(String)")
    private String[] imei;

    @Column(name = "LimitAdTracking", type = "Enum8('undefined'=-1, 'false'=0, 'true'=1)")
    private String limitAdTracking;

    @Column(name = "ClientKitVersion", type = "UInt32")
    private Long clientKitVersion;

    @Column(name = "KitBuildType", type = "UInt16")
    private Integer kitBuildType;

    @Column(name = "KitBuildNumber", type = "UInt32")
    private Long kitBuildNumber;

    @Column(name = "SendTimestamp", type = "UInt64")
    private BigInteger sendTimestamp;

    @Column(name = "SendTimeZone", type = "Int32")
    private Integer sendTimeZone;

    @Column(name = "ReceiveDate", type = "Date")
    private DateTime receiveDate;

    @Column(name = "ReceiveTimestamp", type = "UInt64")
    private BigInteger receiveTimestamp;

    @Column(name = "SessionID", type = "UInt64")
    private BigInteger sessionID;

    @Column(name = "SessionType", type = "UInt8")
    private Integer sessionType;

    @Column(name = "DeviceIDSessionIDHash", type = "UInt64")
    private BigInteger deviceIDSessionIDHash;

    @Column(name = "StartTime", type = "DateTime")
    private DateTime startTime;

    @Column(name = "StartTimestamp", type = "UInt64")
    private BigInteger startTimestamp;

    @Column(name = "StartTimeZone", type = "Int32")
    private Integer startTimeZone;

    @Column(name = "StartTimeCorrected", type = "UInt8")
    private Boolean startTimeCorrected;

    @Column(name = "StartTimeObtainedBeforeSynchronization", type = "UInt8")
    private Boolean startTimeObtainedBeforeSynchronization;

    @Column(name = "RegionTimeZone", type = "Int32")
    private Integer regionTimeZone;

    @Column(name = "Locale", type = "String")
    private String locale;

    @Column(name = "LocaleLanguage", type = "String")
    private String localeLanguage;

    @Column(name = "LocaleScript", type = "String")
    private String localeScript;

    @Column(name = "LocaleRegion", type = "String")
    private String localeRegion;

    @Column(name = "LocationSource", type = "UInt8")
    private Integer locationSource;

    @Column(name = "Latitude", type = "Float64")
    private java.lang.Double latitude;

    @Column(name = "Longitude", type = "Float64")
    private java.lang.Double longitude;

    @Column(name = "LocationTimestamp", type = "UInt64")
    private BigInteger locationTimestamp;

    @Column(name = "LocationPrecision", type = "UInt32")
    private Long locationPrecision;

    @Column(name = "LocationDirection", type = "UInt32")
    private Long locationDirection;

    @Column(name = "LocationSpeed", type = "UInt32")
    private Long locationSpeed;

    @Column(name = "LocationAltitude", type = "Int32")
    private Integer locationAltitude;

    @Column(name = "LocationEnabled", type = "Enum8('undefined'=-1, 'false'=0, 'true'=1)")
    private String locationEnabled;

    @Column(name = "WifiAccessPointSsid", type = "String")
    private String wifiAccessPointSsid;

    @Column(name = "WifiAccessPointState", type = "UInt8")
    private Integer wifiAccessPointState;

    @Column(name = "ConnectionType", type = "UInt8")
    private Integer connectionType;

    @Column(name = "NetworkType", type = "String")
    private String networkType;

    @Column(name = "CountryCode", type = "UInt32")
    private Long countryCode;

    @Column(name = "OperatorID", type = "UInt32")
    private Long operatorID;

    @Column(name = "OperatorName", type = "String")
    private String operatorName;

    @Column(name = "SimCards.CountriesCodes", type = "Array(UInt32)")
    private Long[] simCardsCountriesCodes;

    @Column(name = "SimCards.OperatorsIDs", type = "Array(UInt32)")
    private Long[] simCardsOperatorsIDs;

    @Column(name = "SimCards.OperatorsNames", type = "Array(String)")
    private String[] simCardsOperatorsNames;

    @Column(name = "SimCards.AreRoaming", type = "Array(UInt8)")
    private Integer[] simCardsAreRoaming;

    @Column(name = "SimCards.IccIDs", type = "Array(String)")
    private String[] simCardsIccIDs;

    @Column(name = "NetworksInterfaces.Names", type = "Array(String)")
    private String[] networksInterfacesNames;

    @Column(name = "NetworksInterfaces.Macs", type = "Array(String)")
    private String[] networksInterfacesMacs;

    @Column(name = "DeviceType", type = "UInt8")
    private Integer deviceType;

    @Column(name = "IsRooted", type = "UInt8")
    private Boolean isRooted;

    @Column(name = "EventID", type = "UInt64")
    private BigInteger eventID;

    @Column(name = "EventNumber", type = "UInt64")
    private BigInteger eventNumber;

    @Column(name = "EventSource", type = "Enum8('sdk'=0, 'import_api'=1)")
    private String eventSource;

    @Column(name = "EventFirstOccurrence", type = "Enum8('undefined'=-1, 'false'=0, 'true'=1)")
    private String eventFirstOccurrence;

    @Column(name = "EventType", type = "UInt8")
    private Integer eventType;

    @Column(name = "EventName", type = "String")
    private String eventName;

    @Column(name = "EventValue", type = "String")
    private ByteString eventValue;

    @Column(name = "EventValueJsonReference", type = "String")
    private String eventValueJsonReference;

    @Column(name = "EventValueCrash", type = "String")
    private String eventValueCrash;

    @Column(name = "EventValueReferrer", type = "String")
    private String eventValueReferrer;

    @Column(name = "EventValueError", type = "String")
    private String eventValueError;

    @Column(name = "CrashID", type = "UInt64")
    private BigInteger crashID;

    @Column(name = "CrashGroupID", type = "UInt64")
    private BigInteger crashGroupID;

    @Column(name = "ErrorID", type = "UInt64")
    private BigInteger errorID;

    @Column(name = "ErrorGroupID", type = "UInt64")
    private BigInteger errorGroupID;

    @Column(name = "EventEnvironment", type = "String")
    private String eventEnvironment;

    @Column(name = "EventEnvironmentParsedParams.Key1", type = "Array(String)")
    private String[] eventEnvironmentParsedParamsKey1;

    @Column(name = "EventEnvironmentParsedParams.Key2", type = "Array(String)")
    private String[] eventEnvironmentParsedParamsKey2;

    @Column(name = "ReportEnvironment.Keys", type = "Array(String)")
    private String[] reportEnvironmentKeys;

    @Column(name = "ReportEnvironment.Values", type = "Array(String)")
    private String[] reportEnvironmentValues;

    @Column(name = "RegionID", type = "UInt32")
    private Long regionID;

    @Column(name = "AppID", type = "String")
    private String appID;

    @Column(name = "ClientIP", type = "FixedString(16)")
    private FixedString clientIP;

    @Column(name = "ClientIPHash", type = "UInt64")
    private BigInteger clientIPHash;

    @Column(name = "ClientPort", type = "UInt16")
    private Integer clientPort;

    @Column(name = "Sex", type = "UInt8")
    private Integer sex;

    @Column(name = "Age", type = "UInt8")
    private Integer age;

    @Column(name = "ProfileID", type = "String")
    private String profileID;

    @Column(name = "ProfileIDHash", type = "UInt64")
    private BigInteger profileIDHash;

    @Column(name = "AccountID", type = "String")
    private String accountID;

    @Column(name = "AccountIDHash", type = "UInt64")
    private BigInteger accountIDHash;

    @Column(name = "AccountType", type = "String")
    private String accountType;

    @Column(name = "AccountOptions.Keys", type = "Array(String)")
    private String[] accountOptionsKeys;

    @Column(name = "AccountOptions.Values", type = "Array(String)")
    private String[] accountOptionsValues;

    @Column(name = "Clids.Names", type = "Array(String)")
    private String[] clidsNames;

    @Column(name = "Clids.Values", type = "Array(UInt64)")
    private BigInteger[] clidsValues;

    @Column(name = "InvalidationReasons", type = "Array(String)")
    private String[] invalidationReasons;

    @Column(name = "OSBuild", type = "String")
    private String OSBuild;

    @Column(name = "DecodeGroupID", type = "UInt64")
    private BigInteger decodeGroupID;

    @Column(name = "CrashEncodeType", type = "Enum8('unknown'=0, 'proguard'=1, 'kscrash'=2, 'breakpad'=3)")
    private String crashEncodeType;

    @Column(name = "CrashBinaryName", type = "String")
    private String crashBinaryName;

    @Column(name = "CrashFileName", type = "String")
    private String crashFileName;

    @Column(name = "CrashMethodName", type = "String")
    private String crashMethodName;

    @Column(name = "CrashSourceLine", type = "UInt64")
    private BigInteger crashSourceLine;

    @Column(name = "CrashThreadContent", type = "String")
    private String crashThreadContent;

    @Column(name = "CrashDecodedEventValue", type = "String")
    private String crashDecodedEventValue;

    @Column(name = "CrashReasonType", type = "String")
    private String crashReasonType;

    @Column(name = "CrashReason", type = "String")
    private String crashReason;

    @Column(name = "CrashReasonMessage", type = "String")
    private String crashReasonMessage;

    @Column(name = "ErrorMessage", type = "String")
    private String errorMessage;

    @Column(name = "DecodeTimestamp", type = "UInt64")
    private BigInteger decodeTimestamp;

    @Column(name = "DecodeRequiredSymbolsId", type = "String")
    private String decodeRequiredSymbolsId;

    @Column(name = "DecodeUsedSymbolsIds", type = "Array(String)")
    private String[] decodeUsedSymbolsIds;

    @Column(name = "DecodeMissedSymbolsIds", type = "Array(String)")
    private String[] decodeMissedSymbolsIds;

    @Column(name = "DecodeUsedSystemSymbolsIds", type = "Array(String)")
    private String[] decodeUsedSystemSymbolsIds;

    @Column(name = "DecodeMissedSystemSymbolsIds", type = "Array(String)")
    private String[] decodeMissedSystemSymbolsIds;

    @Column(name = "DecodeStatus", type = "Enum8('unknown'=0, 'parse_error'=1, 'parse_success'=2, 'decode_success'=3, 'decode_error'=4)")
    private String decodeStatus;

    @Column(name = "DecodeErrorDetails", type = "String")
    private String decodeErrorDetails;

    @Column(name = "DecodeOriginalAPIKey", type = "UInt32")
    private Long decodeOriginalAPIKey;

    @Column(name = "DecodeOriginalEventID", type = "UInt64")
    private BigInteger decodeOriginalEventID;

    @Column(name = "Sign", type = "Int8")
    private Integer sign;

    @Column(name = "Version", type = "UInt64")
    private BigInteger version;

    public MobileEvent() {
    }

    public MobileEvent(MobileEvent mobileEvent) {
        this.APIKey = mobileEvent.APIKey;
        this.APIKey128 = mobileEvent.APIKey128;
        this.attributionID = mobileEvent.attributionID;
        this.attributionIDUUIDHash = mobileEvent.attributionIDUUIDHash;
        this.startDate = mobileEvent.startDate;
        this.eventDate = mobileEvent.eventDate;
        this.UUID = mobileEvent.UUID;
        this.deviceID = mobileEvent.deviceID;
        this.UUIDHash = mobileEvent.UUIDHash;
        this.deviceIDHash = mobileEvent.deviceIDHash;
        this.appPlatform = mobileEvent.appPlatform;
        this.operatingSystem = mobileEvent.operatingSystem;
        this.appFramework = mobileEvent.appFramework;
        this.appVersionName = mobileEvent.appVersionName;
        this.appBuildNumber = mobileEvent.appBuildNumber;
        this.appDebuggable = mobileEvent.appDebuggable;
        this.kitVersion = mobileEvent.kitVersion;
        this.manufacturer = mobileEvent.manufacturer;
        this.model = mobileEvent.model;
        this.originalManufacturer = mobileEvent.originalManufacturer;
        this.originalModel = mobileEvent.originalModel;
        this.OSVersion = mobileEvent.OSVersion;
        this.OSApiLevel = mobileEvent.OSApiLevel;
        this.screenWidth = mobileEvent.screenWidth;
        this.screenHeight = mobileEvent.screenHeight;
        this.screenDPI = mobileEvent.screenDPI;
        this.scaleFactor = mobileEvent.scaleFactor;
        this.imei = mobileEvent.imei;
        this.limitAdTracking = mobileEvent.limitAdTracking;
        this.clientKitVersion = mobileEvent.clientKitVersion;
        this.kitBuildType = mobileEvent.kitBuildType;
        this.kitBuildNumber = mobileEvent.kitBuildNumber;
        this.sendTimestamp = mobileEvent.sendTimestamp;
        this.sendTimeZone = mobileEvent.sendTimeZone;
        this.receiveDate = mobileEvent.receiveDate;
        this.receiveTimestamp = mobileEvent.receiveTimestamp;
        this.sessionID = mobileEvent.sessionID;
        this.sessionType = mobileEvent.sessionType;
        this.deviceIDSessionIDHash = mobileEvent.deviceIDSessionIDHash;
        this.startTime = mobileEvent.startTime;
        this.startTimestamp = mobileEvent.startTimestamp;
        this.startTimeZone = mobileEvent.startTimeZone;
        this.startTimeCorrected = mobileEvent.startTimeCorrected;
        this.startTimeObtainedBeforeSynchronization = mobileEvent.startTimeObtainedBeforeSynchronization;
        this.regionTimeZone = mobileEvent.regionTimeZone;
        this.locale = mobileEvent.locale;
        this.localeLanguage = mobileEvent.localeLanguage;
        this.localeScript = mobileEvent.localeScript;
        this.localeRegion = mobileEvent.localeRegion;
        this.locationSource = mobileEvent.locationSource;
        this.latitude = mobileEvent.latitude;
        this.longitude = mobileEvent.longitude;
        this.locationTimestamp = mobileEvent.locationTimestamp;
        this.locationPrecision = mobileEvent.locationPrecision;
        this.locationDirection = mobileEvent.locationDirection;
        this.locationSpeed = mobileEvent.locationSpeed;
        this.locationAltitude = mobileEvent.locationAltitude;
        this.locationEnabled = mobileEvent.locationEnabled;
        this.wifiAccessPointSsid = mobileEvent.wifiAccessPointSsid;
        this.wifiAccessPointState = mobileEvent.wifiAccessPointState;
        this.connectionType = mobileEvent.connectionType;
        this.networkType = mobileEvent.networkType;
        this.countryCode = mobileEvent.countryCode;
        this.operatorID = mobileEvent.operatorID;
        this.operatorName = mobileEvent.operatorName;
        this.simCardsCountriesCodes = mobileEvent.simCardsCountriesCodes;
        this.simCardsOperatorsIDs = mobileEvent.simCardsOperatorsIDs;
        this.simCardsOperatorsNames = mobileEvent.simCardsOperatorsNames;
        this.simCardsAreRoaming = mobileEvent.simCardsAreRoaming;
        this.simCardsIccIDs = mobileEvent.simCardsIccIDs;
        this.networksInterfacesNames = mobileEvent.networksInterfacesNames;
        this.networksInterfacesMacs = mobileEvent.networksInterfacesMacs;
        this.deviceType = mobileEvent.deviceType;
        this.isRooted = mobileEvent.isRooted;
        this.eventID = mobileEvent.eventID;
        this.eventNumber = mobileEvent.eventNumber;
        this.eventSource = mobileEvent.eventSource;
        this.eventFirstOccurrence = mobileEvent.eventFirstOccurrence;
        this.eventType = mobileEvent.eventType;
        this.eventName = mobileEvent.eventName;
        this.eventValue = mobileEvent.eventValue;
        this.eventValueJsonReference = mobileEvent.eventValueJsonReference;
        this.eventValueCrash = mobileEvent.eventValueCrash;
        this.eventValueReferrer = mobileEvent.eventValueReferrer;
        this.eventValueError = mobileEvent.eventValueError;
        this.crashID = mobileEvent.crashID;
        this.crashGroupID = mobileEvent.crashGroupID;
        this.errorID = mobileEvent.errorID;
        this.errorGroupID = mobileEvent.errorGroupID;
        this.eventEnvironment = mobileEvent.eventEnvironment;
        this.eventEnvironmentParsedParamsKey1 = mobileEvent.eventEnvironmentParsedParamsKey1;
        this.eventEnvironmentParsedParamsKey2 = mobileEvent.eventEnvironmentParsedParamsKey2;
        this.reportEnvironmentKeys = mobileEvent.reportEnvironmentKeys;
        this.reportEnvironmentValues = mobileEvent.reportEnvironmentValues;
        this.regionID = mobileEvent.regionID;
        this.appID = mobileEvent.appID;
        this.clientIP = mobileEvent.clientIP;
        this.clientIPHash = mobileEvent.clientIPHash;
        this.clientPort = mobileEvent.clientPort;
        this.sex = mobileEvent.sex;
        this.age = mobileEvent.age;
        this.profileID = mobileEvent.profileID;
        this.profileIDHash = mobileEvent.profileIDHash;
        this.accountID = mobileEvent.accountID;
        this.accountIDHash = mobileEvent.accountIDHash;
        this.accountType = mobileEvent.accountType;
        this.accountOptionsKeys = mobileEvent.accountOptionsKeys;
        this.accountOptionsValues = mobileEvent.accountOptionsValues;
        this.clidsNames = mobileEvent.clidsNames;
        this.clidsValues = mobileEvent.clidsValues;
        this.invalidationReasons = mobileEvent.invalidationReasons;
        this.OSBuild = mobileEvent.OSBuild;
        this.decodeGroupID = mobileEvent.decodeGroupID;
        this.crashEncodeType = mobileEvent.crashEncodeType;
        this.crashBinaryName = mobileEvent.crashBinaryName;
        this.crashFileName = mobileEvent.crashFileName;
        this.crashMethodName = mobileEvent.crashMethodName;
        this.crashSourceLine = mobileEvent.crashSourceLine;
        this.crashThreadContent = mobileEvent.crashThreadContent;
        this.crashDecodedEventValue = mobileEvent.crashDecodedEventValue;
        this.crashReasonType = mobileEvent.crashReasonType;
        this.crashReason = mobileEvent.crashReason;
        this.crashReasonMessage = mobileEvent.crashReasonMessage;
        this.errorMessage = mobileEvent.errorMessage;
        this.decodeTimestamp = mobileEvent.decodeTimestamp;
        this.decodeRequiredSymbolsId = mobileEvent.decodeRequiredSymbolsId;
        this.decodeUsedSymbolsIds = mobileEvent.decodeUsedSymbolsIds;
        this.decodeMissedSymbolsIds = mobileEvent.decodeMissedSymbolsIds;
        this.decodeUsedSystemSymbolsIds = mobileEvent.decodeUsedSystemSymbolsIds;
        this.decodeMissedSystemSymbolsIds = mobileEvent.decodeMissedSystemSymbolsIds;
        this.decodeStatus = mobileEvent.decodeStatus;
        this.decodeErrorDetails = mobileEvent.decodeErrorDetails;
        this.decodeOriginalAPIKey = mobileEvent.decodeOriginalAPIKey;
        this.decodeOriginalEventID = mobileEvent.decodeOriginalEventID;
        this.sign = mobileEvent.sign;
        this.version = mobileEvent.version;
    }

    public MobileEvent(ResultSet resultSet) throws SQLException {
        this.APIKey = resultSet.getLong("APIKey");
        this.APIKey128 = new FixedString(resultSet.getBytes("APIKey128"));
        this.attributionID = resultSet.getLong("AttributionID");
        this.attributionIDUUIDHash = new BigInteger(resultSet.getString("AttributionIDUUIDHash"));
        this.startDate = DateTime.parse(resultSet.getString("StartDate"), dateFormatter);
        this.eventDate = DateTime.parse(resultSet.getString("EventDate"), dateFormatter);
        this.UUID = resultSet.getString("UUID");
        this.deviceID = resultSet.getString("DeviceID");
        this.UUIDHash = new BigInteger(resultSet.getString("UUIDHash"));
        this.deviceIDHash = new BigInteger(resultSet.getString("DeviceIDHash"));
        this.appPlatform = resultSet.getString("AppPlatform");
        this.operatingSystem = resultSet.getString("OperatingSystem");
        this.appFramework = resultSet.getInt("AppFramework");
        this.appVersionName = resultSet.getString("AppVersionName");
        this.appBuildNumber = resultSet.getLong("AppBuildNumber");
        this.appDebuggable = resultSet.getString("AppDebuggable");
        this.kitVersion = resultSet.getLong("KitVersion");
        this.manufacturer = resultSet.getString("Manufacturer");
        this.model = resultSet.getString("Model");
        this.originalManufacturer = resultSet.getString("OriginalManufacturer");
        this.originalModel = resultSet.getString("OriginalModel");
        this.OSVersion = resultSet.getString("OSVersion");
        this.OSApiLevel = resultSet.getLong("OSApiLevel");
        this.screenWidth = resultSet.getLong("ScreenWidth");
        this.screenHeight = resultSet.getLong("ScreenHeight");
        this.screenDPI = resultSet.getLong("ScreenDPI");
        this.scaleFactor = resultSet.getDouble("ScaleFactor");
        this.imei = (String[]) resultSet.getArray("Imei").getArray();
        this.limitAdTracking = resultSet.getString("LimitAdTracking");
        this.clientKitVersion = resultSet.getLong("ClientKitVersion");
        this.kitBuildType = resultSet.getInt("KitBuildType");
        this.kitBuildNumber = resultSet.getLong("KitBuildNumber");
        this.sendTimestamp = new BigInteger(resultSet.getString("SendTimestamp"));
        this.sendTimeZone = resultSet.getInt("SendTimeZone");
        this.receiveDate = DateTime.parse(resultSet.getString("ReceiveDate"), dateFormatter);
        this.receiveTimestamp = new BigInteger(resultSet.getString("ReceiveTimestamp"));
        this.sessionID = new BigInteger(resultSet.getString("SessionID"));
        this.sessionType = resultSet.getInt("SessionType");
        this.deviceIDSessionIDHash = new BigInteger(resultSet.getString("DeviceIDSessionIDHash"));
        this.startTime = new DateTime(resultSet.getTimestamp("StartTime"));
        this.startTimestamp = new BigInteger(resultSet.getString("StartTimestamp"));
        this.startTimeZone = resultSet.getInt("StartTimeZone");
        this.startTimeCorrected = resultSet.getBoolean("StartTimeCorrected");
        this.startTimeObtainedBeforeSynchronization = resultSet.getBoolean("StartTimeObtainedBeforeSynchronization");
        this.regionTimeZone = resultSet.getInt("RegionTimeZone");
        this.locale = resultSet.getString("Locale");
        this.localeLanguage = resultSet.getString("LocaleLanguage");
        this.localeScript = resultSet.getString("LocaleScript");
        this.localeRegion = resultSet.getString("LocaleRegion");
        this.locationSource = resultSet.getInt("LocationSource");
        this.latitude = resultSet.getDouble("Latitude");
        this.longitude = resultSet.getDouble("Longitude");
        this.locationTimestamp = new BigInteger(resultSet.getString("LocationTimestamp"));
        this.locationPrecision = resultSet.getLong("LocationPrecision");
        this.locationDirection = resultSet.getLong("LocationDirection");
        this.locationSpeed = resultSet.getLong("LocationSpeed");
        this.locationAltitude = resultSet.getInt("LocationAltitude");
        this.locationEnabled = resultSet.getString("LocationEnabled");
        this.wifiAccessPointSsid = resultSet.getString("WifiAccessPointSsid");
        this.wifiAccessPointState = resultSet.getInt("WifiAccessPointState");
        this.connectionType = resultSet.getInt("ConnectionType");
        this.networkType = resultSet.getString("NetworkType");
        this.countryCode = resultSet.getLong("CountryCode");
        this.operatorID = resultSet.getLong("OperatorID");
        this.operatorName = resultSet.getString("OperatorName");
        this.simCardsCountriesCodes = ArrayUtils.toObject((long[]) resultSet.getArray("SimCards.CountriesCodes").getArray());
        this.simCardsOperatorsIDs = ArrayUtils.toObject((long[]) resultSet.getArray("SimCards.OperatorsIDs").getArray());
        this.simCardsOperatorsNames = (String[]) resultSet.getArray("SimCards.OperatorsNames").getArray();
        this.simCardsAreRoaming = Stream.of(ArrayUtils.toObject((int[]) resultSet.getArray("SimCards.AreRoaming").getArray())).toArray(Integer[]::new);
        this.simCardsIccIDs = (String[]) resultSet.getArray("SimCards.IccIDs").getArray();
        this.networksInterfacesNames = (String[]) resultSet.getArray("NetworksInterfaces.Names").getArray();
        this.networksInterfacesMacs = (String[]) resultSet.getArray("NetworksInterfaces.Macs").getArray();
        this.deviceType = resultSet.getInt("DeviceType");
        this.isRooted = resultSet.getBoolean("IsRooted");
        this.eventID = new BigInteger(resultSet.getString("EventID"));
        this.eventNumber = new BigInteger(resultSet.getString("EventNumber"));
        this.eventSource = resultSet.getString("EventSource");
        this.eventFirstOccurrence = resultSet.getString("EventFirstOccurrence");
        this.eventType = resultSet.getInt("EventType");
        this.eventName = resultSet.getString("EventName");
        this.eventValue = new ByteString(resultSet.getBytes("EventValue"));
        this.eventValueJsonReference = resultSet.getString("EventValueJsonReference");
        this.eventValueCrash = resultSet.getString("EventValueCrash");
        this.eventValueReferrer = resultSet.getString("EventValueReferrer");
        this.eventValueError = resultSet.getString("EventValueError");
        this.crashID = new BigInteger(resultSet.getString("CrashID"));
        this.crashGroupID = new BigInteger(resultSet.getString("CrashGroupID"));
        this.errorID = new BigInteger(resultSet.getString("ErrorID"));
        this.errorGroupID = new BigInteger(resultSet.getString("ErrorGroupID"));
        this.eventEnvironment = resultSet.getString("EventEnvironment");
        this.eventEnvironmentParsedParamsKey1 = (String[]) resultSet.getArray("EventEnvironmentParsedParams.Key1").getArray();
        this.eventEnvironmentParsedParamsKey2 = (String[]) resultSet.getArray("EventEnvironmentParsedParams.Key2").getArray();
        this.reportEnvironmentKeys = (String[]) resultSet.getArray("ReportEnvironment.Keys").getArray();
        this.reportEnvironmentValues = (String[]) resultSet.getArray("ReportEnvironment.Values").getArray();
        this.regionID = resultSet.getLong("RegionID");
        this.appID = resultSet.getString("AppID");
        this.clientIP = new FixedString(resultSet.getBytes("ClientIP"));
        this.clientIPHash = new BigInteger(resultSet.getString("ClientIPHash"));
        this.clientPort = resultSet.getInt("ClientPort");
        this.sex = resultSet.getInt("Sex");
        this.age = resultSet.getInt("Age");
        this.profileID = resultSet.getString("ProfileID");
        this.profileIDHash = new BigInteger(resultSet.getString("ProfileIDHash"));
        this.accountID = resultSet.getString("AccountID");
        this.accountIDHash = new BigInteger(resultSet.getString("AccountIDHash"));
        this.accountType = resultSet.getString("AccountType");
        this.accountOptionsKeys = (String[]) resultSet.getArray("AccountOptions.Keys").getArray();
        this.accountOptionsValues = (String[]) resultSet.getArray("AccountOptions.Values").getArray();
        this.clidsNames = (String[]) resultSet.getArray("Clids.Names").getArray();
        this.clidsValues = (BigInteger[]) resultSet.getArray("Clids.Values").getArray();
        this.invalidationReasons = (String[]) resultSet.getArray("InvalidationReasons").getArray();
        this.OSBuild = resultSet.getString("OSBuild");
        this.decodeGroupID = new BigInteger(resultSet.getString("DecodeGroupID"));
        this.crashEncodeType = resultSet.getString("CrashEncodeType");
        this.crashBinaryName = resultSet.getString("CrashBinaryName");
        this.crashFileName = resultSet.getString("CrashFileName");
        this.crashMethodName = resultSet.getString("CrashMethodName");
        this.crashSourceLine = new BigInteger(resultSet.getString("CrashSourceLine"));
        this.crashThreadContent = resultSet.getString("CrashThreadContent");
        this.crashDecodedEventValue = resultSet.getString("CrashDecodedEventValue");
        this.crashReasonType = resultSet.getString("CrashReasonType");
        this.crashReason = resultSet.getString("CrashReason");
        this.crashReasonMessage = resultSet.getString("CrashReasonMessage");
        this.errorMessage = resultSet.getString("ErrorMessage");
        this.decodeTimestamp = new BigInteger(resultSet.getString("DecodeTimestamp"));
        this.decodeRequiredSymbolsId = resultSet.getString("DecodeRequiredSymbolsId");
        this.decodeUsedSymbolsIds = (String[]) resultSet.getArray("DecodeUsedSymbolsIds").getArray();
        this.decodeMissedSymbolsIds = (String[]) resultSet.getArray("DecodeMissedSymbolsIds").getArray();
        this.decodeUsedSystemSymbolsIds = (String[]) resultSet.getArray("DecodeUsedSystemSymbolsIds").getArray();
        this.decodeMissedSystemSymbolsIds = (String[]) resultSet.getArray("DecodeMissedSystemSymbolsIds").getArray();
        this.decodeStatus = resultSet.getString("DecodeStatus");
        this.decodeErrorDetails = resultSet.getString("DecodeErrorDetails");
        this.decodeOriginalAPIKey = resultSet.getLong("DecodeOriginalAPIKey");
        this.decodeOriginalEventID = new BigInteger(resultSet.getString("DecodeOriginalEventID"));
        this.sign = resultSet.getInt("Sign");
        this.version = new BigInteger(resultSet.getString("Version"));
    }

    public Long getAPIKey() {
        return APIKey;
    }

    public void setAPIKey(Long APIKey) {
        this.APIKey = APIKey;
    }

    public MobileEvent withAPIKey(Long APIKey) {
        this.APIKey = APIKey;
        return this;
    }

    public FixedString getAPIKey128() {
        return APIKey128;
    }

    public void setAPIKey128(FixedString APIKey128) {
        this.APIKey128 = APIKey128;
    }

    public MobileEvent withAPIKey128(FixedString APIKey128) {
        this.APIKey128 = APIKey128;
        return this;
    }

    public Long getAttributionID() {
        return attributionID;
    }

    public void setAttributionID(Long attributionID) {
        this.attributionID = attributionID;
    }

    public MobileEvent withAttributionID(Long attributionID) {
        this.attributionID = attributionID;
        return this;
    }

    public BigInteger getAttributionIDUUIDHash() {
        return attributionIDUUIDHash;
    }

    public void setAttributionIDUUIDHash(BigInteger attributionIDUUIDHash) {
        this.attributionIDUUIDHash = attributionIDUUIDHash;
    }

    public MobileEvent withAttributionIDUUIDHash(BigInteger attributionIDUUIDHash) {
        this.attributionIDUUIDHash = attributionIDUUIDHash;
        return this;
    }

    public DateTime getStartDate() {
        return startDate;
    }

    public void setStartDate(DateTime startDate) {
        this.startDate = startDate;
    }

    public MobileEvent withStartDate(DateTime startDate) {
        this.startDate = startDate;
        return this;
    }

    public DateTime getEventDate() {
        return eventDate;
    }

    public void setEventDate(DateTime eventDate) {
        this.eventDate = eventDate;
    }

    public MobileEvent withEventDate(DateTime eventDate) {
        this.eventDate = eventDate;
        return this;
    }

    public String getUUID() {
        return UUID;
    }

    public void setUUID(String UUID) {
        this.UUID = UUID;
    }

    public MobileEvent withUUID(String UUID) {
        this.UUID = UUID;
        return this;
    }

    public String getDeviceID() {
        return deviceID;
    }

    public void setDeviceID(String deviceID) {
        this.deviceID = deviceID;
    }

    public MobileEvent withDeviceID(String deviceID) {
        this.deviceID = deviceID;
        return this;
    }

    public BigInteger getUUIDHash() {
        return UUIDHash;
    }

    public void setUUIDHash(BigInteger UUIDHash) {
        this.UUIDHash = UUIDHash;
    }

    public MobileEvent withUUIDHash(BigInteger UUIDHash) {
        this.UUIDHash = UUIDHash;
        return this;
    }

    public BigInteger getDeviceIDHash() {
        return deviceIDHash;
    }

    public void setDeviceIDHash(BigInteger deviceIDHash) {
        this.deviceIDHash = deviceIDHash;
    }

    public MobileEvent withDeviceIDHash(BigInteger deviceIDHash) {
        this.deviceIDHash = deviceIDHash;
        return this;
    }

    public String getAppPlatform() {
        return appPlatform;
    }

    public void setAppPlatform(String appPlatform) {
        this.appPlatform = appPlatform;
    }

    public MobileEvent withAppPlatform(String appPlatform) {
        this.appPlatform = appPlatform;
        return this;
    }

    public String getOperatingSystem() {
        return operatingSystem;
    }

    public void setOperatingSystem(String operatingSystem) {
        this.operatingSystem = operatingSystem;
    }

    public MobileEvent withOperatingSystem(String operatingSystem) {
        this.operatingSystem = operatingSystem;
        return this;
    }

    public Integer getAppFramework() {
        return appFramework;
    }

    public void setAppFramework(Integer appFramework) {
        this.appFramework = appFramework;
    }

    public MobileEvent withAppFramework(Integer appFramework) {
        this.appFramework = appFramework;
        return this;
    }

    public String getAppVersionName() {
        return appVersionName;
    }

    public void setAppVersionName(String appVersionName) {
        this.appVersionName = appVersionName;
    }

    public MobileEvent withAppVersionName(String appVersionName) {
        this.appVersionName = appVersionName;
        return this;
    }

    public Long getAppBuildNumber() {
        return appBuildNumber;
    }

    public void setAppBuildNumber(Long appBuildNumber) {
        this.appBuildNumber = appBuildNumber;
    }

    public MobileEvent withAppBuildNumber(Long appBuildNumber) {
        this.appBuildNumber = appBuildNumber;
        return this;
    }

    public String getAppDebuggable() {
        return appDebuggable;
    }

    public void setAppDebuggable(String appDebuggable) {
        this.appDebuggable = appDebuggable;
    }

    public MobileEvent withAppDebuggable(String appDebuggable) {
        this.appDebuggable = appDebuggable;
        return this;
    }

    public Long getKitVersion() {
        return kitVersion;
    }

    public void setKitVersion(Long kitVersion) {
        this.kitVersion = kitVersion;
    }

    public MobileEvent withKitVersion(Long kitVersion) {
        this.kitVersion = kitVersion;
        return this;
    }

    public String getManufacturer() {
        return manufacturer;
    }

    public void setManufacturer(String manufacturer) {
        this.manufacturer = manufacturer;
    }

    public MobileEvent withManufacturer(String manufacturer) {
        this.manufacturer = manufacturer;
        return this;
    }

    public String getModel() {
        return model;
    }

    public void setModel(String model) {
        this.model = model;
    }

    public MobileEvent withModel(String model) {
        this.model = model;
        return this;
    }

    public String getOriginalManufacturer() {
        return originalManufacturer;
    }

    public void setOriginalManufacturer(String originalManufacturer) {
        this.originalManufacturer = originalManufacturer;
    }

    public MobileEvent withOriginalManufacturer(String originalManufacturer) {
        this.originalManufacturer = originalManufacturer;
        return this;
    }

    public String getOriginalModel() {
        return originalModel;
    }

    public void setOriginalModel(String originalModel) {
        this.originalModel = originalModel;
    }

    public MobileEvent withOriginalModel(String originalModel) {
        this.originalModel = originalModel;
        return this;
    }

    public String getOSVersion() {
        return OSVersion;
    }

    public void setOSVersion(String OSVersion) {
        this.OSVersion = OSVersion;
    }

    public MobileEvent withOSVersion(String OSVersion) {
        this.OSVersion = OSVersion;
        return this;
    }

    public Long getOSApiLevel() {
        return OSApiLevel;
    }

    public void setOSApiLevel(Long OSApiLevel) {
        this.OSApiLevel = OSApiLevel;
    }

    public MobileEvent withOSApiLevel(Long OSApiLevel) {
        this.OSApiLevel = OSApiLevel;
        return this;
    }

    public Long getScreenWidth() {
        return screenWidth;
    }

    public void setScreenWidth(Long screenWidth) {
        this.screenWidth = screenWidth;
    }

    public MobileEvent withScreenWidth(Long screenWidth) {
        this.screenWidth = screenWidth;
        return this;
    }

    public Long getScreenHeight() {
        return screenHeight;
    }

    public void setScreenHeight(Long screenHeight) {
        this.screenHeight = screenHeight;
    }

    public MobileEvent withScreenHeight(Long screenHeight) {
        this.screenHeight = screenHeight;
        return this;
    }

    public Long getScreenDPI() {
        return screenDPI;
    }

    public void setScreenDPI(Long screenDPI) {
        this.screenDPI = screenDPI;
    }

    public MobileEvent withScreenDPI(Long screenDPI) {
        this.screenDPI = screenDPI;
        return this;
    }

    public java.lang.Double getScaleFactor() {
        return scaleFactor;
    }

    public void setScaleFactor(java.lang.Double scaleFactor) {
        this.scaleFactor = scaleFactor;
    }

    public MobileEvent withScaleFactor(java.lang.Double scaleFactor) {
        this.scaleFactor = scaleFactor;
        return this;
    }

    public String[] getImei() {
        return imei;
    }

    public void setImei(String[] imei) {
        this.imei = imei;
    }

    public MobileEvent withImei(String[] imei) {
        this.imei = imei;
        return this;
    }

    public String getLimitAdTracking() {
        return limitAdTracking;
    }

    public void setLimitAdTracking(String limitAdTracking) {
        this.limitAdTracking = limitAdTracking;
    }

    public MobileEvent withLimitAdTracking(String limitAdTracking) {
        this.limitAdTracking = limitAdTracking;
        return this;
    }

    public Long getClientKitVersion() {
        return clientKitVersion;
    }

    public void setClientKitVersion(Long clientKitVersion) {
        this.clientKitVersion = clientKitVersion;
    }

    public MobileEvent withClientKitVersion(Long clientKitVersion) {
        this.clientKitVersion = clientKitVersion;
        return this;
    }

    public Integer getKitBuildType() {
        return kitBuildType;
    }

    public void setKitBuildType(Integer kitBuildType) {
        this.kitBuildType = kitBuildType;
    }

    public MobileEvent withKitBuildType(Integer kitBuildType) {
        this.kitBuildType = kitBuildType;
        return this;
    }

    public Long getKitBuildNumber() {
        return kitBuildNumber;
    }

    public void setKitBuildNumber(Long kitBuildNumber) {
        this.kitBuildNumber = kitBuildNumber;
    }

    public MobileEvent withKitBuildNumber(Long kitBuildNumber) {
        this.kitBuildNumber = kitBuildNumber;
        return this;
    }

    public BigInteger getSendTimestamp() {
        return sendTimestamp;
    }

    public void setSendTimestamp(BigInteger sendTimestamp) {
        this.sendTimestamp = sendTimestamp;
    }

    public MobileEvent withSendTimestamp(BigInteger sendTimestamp) {
        this.sendTimestamp = sendTimestamp;
        return this;
    }

    public Integer getSendTimeZone() {
        return sendTimeZone;
    }

    public void setSendTimeZone(Integer sendTimeZone) {
        this.sendTimeZone = sendTimeZone;
    }

    public MobileEvent withSendTimeZone(Integer sendTimeZone) {
        this.sendTimeZone = sendTimeZone;
        return this;
    }

    public DateTime getReceiveDate() {
        return receiveDate;
    }

    public void setReceiveDate(DateTime receiveDate) {
        this.receiveDate = receiveDate;
    }

    public MobileEvent withReceiveDate(DateTime receiveDate) {
        this.receiveDate = receiveDate;
        return this;
    }

    public BigInteger getReceiveTimestamp() {
        return receiveTimestamp;
    }

    public void setReceiveTimestamp(BigInteger receiveTimestamp) {
        this.receiveTimestamp = receiveTimestamp;
    }

    public MobileEvent withReceiveTimestamp(BigInteger receiveTimestamp) {
        this.receiveTimestamp = receiveTimestamp;
        return this;
    }

    public BigInteger getSessionID() {
        return sessionID;
    }

    public void setSessionID(BigInteger sessionID) {
        this.sessionID = sessionID;
    }

    public MobileEvent withSessionID(BigInteger sessionID) {
        this.sessionID = sessionID;
        return this;
    }

    public Integer getSessionType() {
        return sessionType;
    }

    public void setSessionType(Integer sessionType) {
        this.sessionType = sessionType;
    }

    public MobileEvent withSessionType(Integer sessionType) {
        this.sessionType = sessionType;
        return this;
    }

    public BigInteger getDeviceIDSessionIDHash() {
        return deviceIDSessionIDHash;
    }

    public void setDeviceIDSessionIDHash(BigInteger deviceIDSessionIDHash) {
        this.deviceIDSessionIDHash = deviceIDSessionIDHash;
    }

    public MobileEvent withDeviceIDSessionIDHash(BigInteger deviceIDSessionIDHash) {
        this.deviceIDSessionIDHash = deviceIDSessionIDHash;
        return this;
    }

    public DateTime getStartTime() {
        return startTime;
    }

    public void setStartTime(DateTime startTime) {
        this.startTime = startTime;
    }

    public MobileEvent withStartTime(DateTime startTime) {
        this.startTime = startTime;
        return this;
    }

    public BigInteger getStartTimestamp() {
        return startTimestamp;
    }

    public void setStartTimestamp(BigInteger startTimestamp) {
        this.startTimestamp = startTimestamp;
    }

    public MobileEvent withStartTimestamp(BigInteger startTimestamp) {
        this.startTimestamp = startTimestamp;
        return this;
    }

    public Integer getStartTimeZone() {
        return startTimeZone;
    }

    public void setStartTimeZone(Integer startTimeZone) {
        this.startTimeZone = startTimeZone;
    }

    public MobileEvent withStartTimeZone(Integer startTimeZone) {
        this.startTimeZone = startTimeZone;
        return this;
    }

    public Boolean getStartTimeCorrected() {
        return startTimeCorrected;
    }

    public void setStartTimeCorrected(Boolean startTimeCorrected) {
        this.startTimeCorrected = startTimeCorrected;
    }

    public MobileEvent withStartTimeCorrected(Boolean startTimeCorrected) {
        this.startTimeCorrected = startTimeCorrected;
        return this;
    }

    public Boolean getStartTimeObtainedBeforeSynchronization() {
        return startTimeObtainedBeforeSynchronization;
    }

    public void setStartTimeObtainedBeforeSynchronization(Boolean startTimeObtainedBeforeSynchronization) {
        this.startTimeObtainedBeforeSynchronization = startTimeObtainedBeforeSynchronization;
    }

    public MobileEvent withStartTimeObtainedBeforeSynchronization(Boolean startTimeObtainedBeforeSynchronization) {
        this.startTimeObtainedBeforeSynchronization = startTimeObtainedBeforeSynchronization;
        return this;
    }

    public Integer getRegionTimeZone() {
        return regionTimeZone;
    }

    public void setRegionTimeZone(Integer regionTimeZone) {
        this.regionTimeZone = regionTimeZone;
    }

    public MobileEvent withRegionTimeZone(Integer regionTimeZone) {
        this.regionTimeZone = regionTimeZone;
        return this;
    }

    public String getLocale() {
        return locale;
    }

    public void setLocale(String locale) {
        this.locale = locale;
    }

    public MobileEvent withLocale(String locale) {
        this.locale = locale;
        return this;
    }

    public String getLocaleLanguage() {
        return localeLanguage;
    }

    public void setLocaleLanguage(String localeLanguage) {
        this.localeLanguage = localeLanguage;
    }

    public MobileEvent withLocaleLanguage(String localeLanguage) {
        this.localeLanguage = localeLanguage;
        return this;
    }

    public String getLocaleScript() {
        return localeScript;
    }

    public void setLocaleScript(String localeScript) {
        this.localeScript = localeScript;
    }

    public MobileEvent withLocaleScript(String localeScript) {
        this.localeScript = localeScript;
        return this;
    }

    public String getLocaleRegion() {
        return localeRegion;
    }

    public void setLocaleRegion(String localeRegion) {
        this.localeRegion = localeRegion;
    }

    public MobileEvent withLocaleRegion(String localeRegion) {
        this.localeRegion = localeRegion;
        return this;
    }

    public Integer getLocationSource() {
        return locationSource;
    }

    public void setLocationSource(Integer locationSource) {
        this.locationSource = locationSource;
    }

    public MobileEvent withLocationSource(Integer locationSource) {
        this.locationSource = locationSource;
        return this;
    }

    public java.lang.Double getLatitude() {
        return latitude;
    }

    public void setLatitude(java.lang.Double latitude) {
        this.latitude = latitude;
    }

    public MobileEvent withLatitude(java.lang.Double latitude) {
        this.latitude = latitude;
        return this;
    }

    public java.lang.Double getLongitude() {
        return longitude;
    }

    public void setLongitude(java.lang.Double longitude) {
        this.longitude = longitude;
    }

    public MobileEvent withLongitude(java.lang.Double longitude) {
        this.longitude = longitude;
        return this;
    }

    public BigInteger getLocationTimestamp() {
        return locationTimestamp;
    }

    public void setLocationTimestamp(BigInteger locationTimestamp) {
        this.locationTimestamp = locationTimestamp;
    }

    public MobileEvent withLocationTimestamp(BigInteger locationTimestamp) {
        this.locationTimestamp = locationTimestamp;
        return this;
    }

    public Long getLocationPrecision() {
        return locationPrecision;
    }

    public void setLocationPrecision(Long locationPrecision) {
        this.locationPrecision = locationPrecision;
    }

    public MobileEvent withLocationPrecision(Long locationPrecision) {
        this.locationPrecision = locationPrecision;
        return this;
    }

    public Long getLocationDirection() {
        return locationDirection;
    }

    public void setLocationDirection(Long locationDirection) {
        this.locationDirection = locationDirection;
    }

    public MobileEvent withLocationDirection(Long locationDirection) {
        this.locationDirection = locationDirection;
        return this;
    }

    public Long getLocationSpeed() {
        return locationSpeed;
    }

    public void setLocationSpeed(Long locationSpeed) {
        this.locationSpeed = locationSpeed;
    }

    public MobileEvent withLocationSpeed(Long locationSpeed) {
        this.locationSpeed = locationSpeed;
        return this;
    }

    public Integer getLocationAltitude() {
        return locationAltitude;
    }

    public void setLocationAltitude(Integer locationAltitude) {
        this.locationAltitude = locationAltitude;
    }

    public MobileEvent withLocationAltitude(Integer locationAltitude) {
        this.locationAltitude = locationAltitude;
        return this;
    }

    public String getLocationEnabled() {
        return locationEnabled;
    }

    public void setLocationEnabled(String locationEnabled) {
        this.locationEnabled = locationEnabled;
    }

    public MobileEvent withLocationEnabled(String locationEnabled) {
        this.locationEnabled = locationEnabled;
        return this;
    }

    public String getWifiAccessPointSsid() {
        return wifiAccessPointSsid;
    }

    public void setWifiAccessPointSsid(String wifiAccessPointSsid) {
        this.wifiAccessPointSsid = wifiAccessPointSsid;
    }

    public MobileEvent withWifiAccessPointSsid(String wifiAccessPointSsid) {
        this.wifiAccessPointSsid = wifiAccessPointSsid;
        return this;
    }

    public Integer getWifiAccessPointState() {
        return wifiAccessPointState;
    }

    public void setWifiAccessPointState(Integer wifiAccessPointState) {
        this.wifiAccessPointState = wifiAccessPointState;
    }

    public MobileEvent withWifiAccessPointState(Integer wifiAccessPointState) {
        this.wifiAccessPointState = wifiAccessPointState;
        return this;
    }

    public Integer getConnectionType() {
        return connectionType;
    }

    public void setConnectionType(Integer connectionType) {
        this.connectionType = connectionType;
    }

    public MobileEvent withConnectionType(Integer connectionType) {
        this.connectionType = connectionType;
        return this;
    }

    public String getNetworkType() {
        return networkType;
    }

    public void setNetworkType(String networkType) {
        this.networkType = networkType;
    }

    public MobileEvent withNetworkType(String networkType) {
        this.networkType = networkType;
        return this;
    }

    public Long getCountryCode() {
        return countryCode;
    }

    public void setCountryCode(Long countryCode) {
        this.countryCode = countryCode;
    }

    public MobileEvent withCountryCode(Long countryCode) {
        this.countryCode = countryCode;
        return this;
    }

    public Long getOperatorID() {
        return operatorID;
    }

    public void setOperatorID(Long operatorID) {
        this.operatorID = operatorID;
    }

    public MobileEvent withOperatorID(Long operatorID) {
        this.operatorID = operatorID;
        return this;
    }

    public String getOperatorName() {
        return operatorName;
    }

    public void setOperatorName(String operatorName) {
        this.operatorName = operatorName;
    }

    public MobileEvent withOperatorName(String operatorName) {
        this.operatorName = operatorName;
        return this;
    }

    public Long[] getSimCardsCountriesCodes() {
        return simCardsCountriesCodes;
    }

    public void setSimCardsCountriesCodes(Long[] simCardsCountriesCodes) {
        this.simCardsCountriesCodes = simCardsCountriesCodes;
    }

    public MobileEvent withSimCardsCountriesCodes(Long[] simCardsCountriesCodes) {
        this.simCardsCountriesCodes = simCardsCountriesCodes;
        return this;
    }

    public Long[] getSimCardsOperatorsIDs() {
        return simCardsOperatorsIDs;
    }

    public void setSimCardsOperatorsIDs(Long[] simCardsOperatorsIDs) {
        this.simCardsOperatorsIDs = simCardsOperatorsIDs;
    }

    public MobileEvent withSimCardsOperatorsIDs(Long[] simCardsOperatorsIDs) {
        this.simCardsOperatorsIDs = simCardsOperatorsIDs;
        return this;
    }

    public String[] getSimCardsOperatorsNames() {
        return simCardsOperatorsNames;
    }

    public void setSimCardsOperatorsNames(String[] simCardsOperatorsNames) {
        this.simCardsOperatorsNames = simCardsOperatorsNames;
    }

    public MobileEvent withSimCardsOperatorsNames(String[] simCardsOperatorsNames) {
        this.simCardsOperatorsNames = simCardsOperatorsNames;
        return this;
    }

    public Integer[] getSimCardsAreRoaming() {
        return simCardsAreRoaming;
    }

    public void setSimCardsAreRoaming(Integer[] simCardsAreRoaming) {
        this.simCardsAreRoaming = simCardsAreRoaming;
    }

    public MobileEvent withSimCardsAreRoaming(Integer[] simCardsAreRoaming) {
        this.simCardsAreRoaming = simCardsAreRoaming;
        return this;
    }

    public String[] getSimCardsIccIDs() {
        return simCardsIccIDs;
    }

    public void setSimCardsIccIDs(String[] simCardsIccIDs) {
        this.simCardsIccIDs = simCardsIccIDs;
    }

    public MobileEvent withSimCardsIccIDs(String[] simCardsIccIDs) {
        this.simCardsIccIDs = simCardsIccIDs;
        return this;
    }

    public String[] getNetworksInterfacesNames() {
        return networksInterfacesNames;
    }

    public void setNetworksInterfacesNames(String[] networksInterfacesNames) {
        this.networksInterfacesNames = networksInterfacesNames;
    }

    public MobileEvent withNetworksInterfacesNames(String[] networksInterfacesNames) {
        this.networksInterfacesNames = networksInterfacesNames;
        return this;
    }

    public String[] getNetworksInterfacesMacs() {
        return networksInterfacesMacs;
    }

    public void setNetworksInterfacesMacs(String[] networksInterfacesMacs) {
        this.networksInterfacesMacs = networksInterfacesMacs;
    }

    public MobileEvent withNetworksInterfacesMacs(String[] networksInterfacesMacs) {
        this.networksInterfacesMacs = networksInterfacesMacs;
        return this;
    }

    public Integer getDeviceType() {
        return deviceType;
    }

    public void setDeviceType(Integer deviceType) {
        this.deviceType = deviceType;
    }

    public MobileEvent withDeviceType(Integer deviceType) {
        this.deviceType = deviceType;
        return this;
    }

    public Boolean getIsRooted() {
        return isRooted;
    }

    public void setIsRooted(Boolean isRooted) {
        this.isRooted = isRooted;
    }

    public MobileEvent withIsRooted(Boolean isRooted) {
        this.isRooted = isRooted;
        return this;
    }

    public BigInteger getEventID() {
        return eventID;
    }

    public void setEventID(BigInteger eventID) {
        this.eventID = eventID;
    }

    public MobileEvent withEventID(BigInteger eventID) {
        this.eventID = eventID;
        return this;
    }

    public BigInteger getEventNumber() {
        return eventNumber;
    }

    public void setEventNumber(BigInteger eventNumber) {
        this.eventNumber = eventNumber;
    }

    public MobileEvent withEventNumber(BigInteger eventNumber) {
        this.eventNumber = eventNumber;
        return this;
    }

    public String getEventSource() {
        return eventSource;
    }

    public void setEventSource(String eventSource) {
        this.eventSource = eventSource;
    }

    public MobileEvent withEventSource(String eventSource) {
        this.eventSource = eventSource;
        return this;
    }

    public String getEventFirstOccurrence() {
        return eventFirstOccurrence;
    }

    public void setEventFirstOccurrence(String eventFirstOccurrence) {
        this.eventFirstOccurrence = eventFirstOccurrence;
    }

    public MobileEvent withEventFirstOccurrence(String eventFirstOccurrence) {
        this.eventFirstOccurrence = eventFirstOccurrence;
        return this;
    }

    public Integer getEventType() {
        return eventType;
    }

    public void setEventType(Integer eventType) {
        this.eventType = eventType;
    }

    public MobileEvent withEventType(Integer eventType) {
        this.eventType = eventType;
        return this;
    }

    public String getEventName() {
        return eventName;
    }

    public void setEventName(String eventName) {
        this.eventName = eventName;
    }

    public MobileEvent withEventName(String eventName) {
        this.eventName = eventName;
        return this;
    }

    public ByteString getEventValue() {
        return eventValue;
    }

    public void setEventValue(ByteString eventValue) {
        this.eventValue = eventValue;
    }

    public MobileEvent withEventValue(ByteString eventValue) {
        this.eventValue = eventValue;
        return this;
    }

    public String getEventValueJsonReference() {
        return eventValueJsonReference;
    }

    public void setEventValueJsonReference(String eventValueJsonReference) {
        this.eventValueJsonReference = eventValueJsonReference;
    }

    public MobileEvent withEventValueJsonReference(String eventValueJsonReference) {
        this.eventValueJsonReference = eventValueJsonReference;
        return this;
    }

    public String getEventValueCrash() {
        return eventValueCrash;
    }

    public void setEventValueCrash(String eventValueCrash) {
        this.eventValueCrash = eventValueCrash;
    }

    public MobileEvent withEventValueCrash(String eventValueCrash) {
        this.eventValueCrash = eventValueCrash;
        return this;
    }

    public String getEventValueReferrer() {
        return eventValueReferrer;
    }

    public void setEventValueReferrer(String eventValueReferrer) {
        this.eventValueReferrer = eventValueReferrer;
    }

    public MobileEvent withEventValueReferrer(String eventValueReferrer) {
        this.eventValueReferrer = eventValueReferrer;
        return this;
    }

    public String getEventValueError() {
        return eventValueError;
    }

    public void setEventValueError(String eventValueError) {
        this.eventValueError = eventValueError;
    }

    public MobileEvent withEventValueError(String eventValueError) {
        this.eventValueError = eventValueError;
        return this;
    }

    public BigInteger getCrashID() {
        return crashID;
    }

    public void setCrashID(BigInteger crashID) {
        this.crashID = crashID;
    }

    public MobileEvent withCrashID(BigInteger crashID) {
        this.crashID = crashID;
        return this;
    }

    public BigInteger getCrashGroupID() {
        return crashGroupID;
    }

    public void setCrashGroupID(BigInteger crashGroupID) {
        this.crashGroupID = crashGroupID;
    }

    public MobileEvent withCrashGroupID(BigInteger crashGroupID) {
        this.crashGroupID = crashGroupID;
        return this;
    }

    public BigInteger getErrorID() {
        return errorID;
    }

    public void setErrorID(BigInteger errorID) {
        this.errorID = errorID;
    }

    public MobileEvent withErrorID(BigInteger errorID) {
        this.errorID = errorID;
        return this;
    }

    public BigInteger getErrorGroupID() {
        return errorGroupID;
    }

    public void setErrorGroupID(BigInteger errorGroupID) {
        this.errorGroupID = errorGroupID;
    }

    public MobileEvent withErrorGroupID(BigInteger errorGroupID) {
        this.errorGroupID = errorGroupID;
        return this;
    }

    public String getEventEnvironment() {
        return eventEnvironment;
    }

    public void setEventEnvironment(String eventEnvironment) {
        this.eventEnvironment = eventEnvironment;
    }

    public MobileEvent withEventEnvironment(String eventEnvironment) {
        this.eventEnvironment = eventEnvironment;
        return this;
    }

    public String[] getEventEnvironmentParsedParamsKey1() {
        return eventEnvironmentParsedParamsKey1;
    }

    public void setEventEnvironmentParsedParamsKey1(String[] eventEnvironmentParsedParamsKey1) {
        this.eventEnvironmentParsedParamsKey1 = eventEnvironmentParsedParamsKey1;
    }

    public MobileEvent withEventEnvironmentParsedParamsKey1(String[] eventEnvironmentParsedParamsKey1) {
        this.eventEnvironmentParsedParamsKey1 = eventEnvironmentParsedParamsKey1;
        return this;
    }

    public String[] getEventEnvironmentParsedParamsKey2() {
        return eventEnvironmentParsedParamsKey2;
    }

    public void setEventEnvironmentParsedParamsKey2(String[] eventEnvironmentParsedParamsKey2) {
        this.eventEnvironmentParsedParamsKey2 = eventEnvironmentParsedParamsKey2;
    }

    public MobileEvent withEventEnvironmentParsedParamsKey2(String[] eventEnvironmentParsedParamsKey2) {
        this.eventEnvironmentParsedParamsKey2 = eventEnvironmentParsedParamsKey2;
        return this;
    }

    public String[] getReportEnvironmentKeys() {
        return reportEnvironmentKeys;
    }

    public void setReportEnvironmentKeys(String[] reportEnvironmentKeys) {
        this.reportEnvironmentKeys = reportEnvironmentKeys;
    }

    public MobileEvent withReportEnvironmentKeys(String[] reportEnvironmentKeys) {
        this.reportEnvironmentKeys = reportEnvironmentKeys;
        return this;
    }

    public String[] getReportEnvironmentValues() {
        return reportEnvironmentValues;
    }

    public void setReportEnvironmentValues(String[] reportEnvironmentValues) {
        this.reportEnvironmentValues = reportEnvironmentValues;
    }

    public MobileEvent withReportEnvironmentValues(String[] reportEnvironmentValues) {
        this.reportEnvironmentValues = reportEnvironmentValues;
        return this;
    }

    public Long getRegionID() {
        return regionID;
    }

    public void setRegionID(Long regionID) {
        this.regionID = regionID;
    }

    public MobileEvent withRegionID(Long regionID) {
        this.regionID = regionID;
        return this;
    }

    public String getAppID() {
        return appID;
    }

    public void setAppID(String appID) {
        this.appID = appID;
    }

    public MobileEvent withAppID(String appID) {
        this.appID = appID;
        return this;
    }

    public FixedString getClientIP() {
        return clientIP;
    }

    public void setClientIP(FixedString clientIP) {
        this.clientIP = clientIP;
    }

    public MobileEvent withClientIP(FixedString clientIP) {
        this.clientIP = clientIP;
        return this;
    }

    public BigInteger getClientIPHash() {
        return clientIPHash;
    }

    public void setClientIPHash(BigInteger clientIPHash) {
        this.clientIPHash = clientIPHash;
    }

    public MobileEvent withClientIPHash(BigInteger clientIPHash) {
        this.clientIPHash = clientIPHash;
        return this;
    }

    public Integer getClientPort() {
        return clientPort;
    }

    public void setClientPort(Integer clientPort) {
        this.clientPort = clientPort;
    }

    public MobileEvent withClientPort(Integer clientPort) {
        this.clientPort = clientPort;
        return this;
    }

    public Integer getSex() {
        return sex;
    }

    public void setSex(Integer sex) {
        this.sex = sex;
    }

    public MobileEvent withSex(Integer sex) {
        this.sex = sex;
        return this;
    }

    public Integer getAge() {
        return age;
    }

    public void setAge(Integer age) {
        this.age = age;
    }

    public MobileEvent withAge(Integer age) {
        this.age = age;
        return this;
    }

    public String getProfileID() {
        return profileID;
    }

    public void setProfileID(String profileID) {
        this.profileID = profileID;
    }

    public MobileEvent withProfileID(String profileID) {
        this.profileID = profileID;
        return this;
    }

    public BigInteger getProfileIDHash() {
        return profileIDHash;
    }

    public void setProfileIDHash(BigInteger profileIDHash) {
        this.profileIDHash = profileIDHash;
    }

    public MobileEvent withProfileIDHash(BigInteger profileIDHash) {
        this.profileIDHash = profileIDHash;
        return this;
    }

    public String getAccountID() {
        return accountID;
    }

    public void setAccountID(String accountID) {
        this.accountID = accountID;
    }

    public MobileEvent withAccountID(String accountID) {
        this.accountID = accountID;
        return this;
    }

    public BigInteger getAccountIDHash() {
        return accountIDHash;
    }

    public void setAccountIDHash(BigInteger accountIDHash) {
        this.accountIDHash = accountIDHash;
    }

    public MobileEvent withAccountIDHash(BigInteger accountIDHash) {
        this.accountIDHash = accountIDHash;
        return this;
    }

    public String getAccountType() {
        return accountType;
    }

    public void setAccountType(String accountType) {
        this.accountType = accountType;
    }

    public MobileEvent withAccountType(String accountType) {
        this.accountType = accountType;
        return this;
    }

    public String[] getAccountOptionsKeys() {
        return accountOptionsKeys;
    }

    public void setAccountOptionsKeys(String[] accountOptionsKeys) {
        this.accountOptionsKeys = accountOptionsKeys;
    }

    public MobileEvent withAccountOptionsKeys(String[] accountOptionsKeys) {
        this.accountOptionsKeys = accountOptionsKeys;
        return this;
    }

    public String[] getAccountOptionsValues() {
        return accountOptionsValues;
    }

    public void setAccountOptionsValues(String[] accountOptionsValues) {
        this.accountOptionsValues = accountOptionsValues;
    }

    public MobileEvent withAccountOptionsValues(String[] accountOptionsValues) {
        this.accountOptionsValues = accountOptionsValues;
        return this;
    }

    public String[] getClidsNames() {
        return clidsNames;
    }

    public void setClidsNames(String[] clidsNames) {
        this.clidsNames = clidsNames;
    }

    public MobileEvent withClidsNames(String[] clidsNames) {
        this.clidsNames = clidsNames;
        return this;
    }

    public BigInteger[] getClidsValues() {
        return clidsValues;
    }

    public void setClidsValues(BigInteger[] clidsValues) {
        this.clidsValues = clidsValues;
    }

    public MobileEvent withClidsValues(BigInteger[] clidsValues) {
        this.clidsValues = clidsValues;
        return this;
    }

    public String[] getInvalidationReasons() {
        return invalidationReasons;
    }

    public void setInvalidationReasons(String[] invalidationReasons) {
        this.invalidationReasons = invalidationReasons;
    }

    public MobileEvent withInvalidationReasons(String[] invalidationReasons) {
        this.invalidationReasons = invalidationReasons;
        return this;
    }

    public String getOSBuild() {
        return OSBuild;
    }

    public void setOSBuild(String OSBuild) {
        this.OSBuild = OSBuild;
    }

    public MobileEvent withOSBuild(String OSBuild) {
        this.OSBuild = OSBuild;
        return this;
    }

    public BigInteger getDecodeGroupID() {
        return decodeGroupID;
    }

    public void setDecodeGroupID(BigInteger decodeGroupID) {
        this.decodeGroupID = decodeGroupID;
    }

    public MobileEvent withDecodeGroupID(BigInteger decodeGroupID) {
        this.decodeGroupID = decodeGroupID;
        return this;
    }

    public String getCrashEncodeType() {
        return crashEncodeType;
    }

    public void setCrashEncodeType(String crashEncodeType) {
        this.crashEncodeType = crashEncodeType;
    }

    public MobileEvent withCrashEncodeType(String crashEncodeType) {
        this.crashEncodeType = crashEncodeType;
        return this;
    }

    public String getCrashBinaryName() {
        return crashBinaryName;
    }

    public void setCrashBinaryName(String crashBinaryName) {
        this.crashBinaryName = crashBinaryName;
    }

    public MobileEvent withCrashBinaryName(String crashBinaryName) {
        this.crashBinaryName = crashBinaryName;
        return this;
    }

    public String getCrashFileName() {
        return crashFileName;
    }

    public void setCrashFileName(String crashFileName) {
        this.crashFileName = crashFileName;
    }

    public MobileEvent withCrashFileName(String crashFileName) {
        this.crashFileName = crashFileName;
        return this;
    }

    public String getCrashMethodName() {
        return crashMethodName;
    }

    public void setCrashMethodName(String crashMethodName) {
        this.crashMethodName = crashMethodName;
    }

    public MobileEvent withCrashMethodName(String crashMethodName) {
        this.crashMethodName = crashMethodName;
        return this;
    }

    public BigInteger getCrashSourceLine() {
        return crashSourceLine;
    }

    public void setCrashSourceLine(BigInteger crashSourceLine) {
        this.crashSourceLine = crashSourceLine;
    }

    public MobileEvent withCrashSourceLine(BigInteger crashSourceLine) {
        this.crashSourceLine = crashSourceLine;
        return this;
    }

    public String getCrashThreadContent() {
        return crashThreadContent;
    }

    public void setCrashThreadContent(String crashThreadContent) {
        this.crashThreadContent = crashThreadContent;
    }

    public MobileEvent withCrashThreadContent(String crashThreadContent) {
        this.crashThreadContent = crashThreadContent;
        return this;
    }

    public String getCrashDecodedEventValue() {
        return crashDecodedEventValue;
    }

    public void setCrashDecodedEventValue(String crashDecodedEventValue) {
        this.crashDecodedEventValue = crashDecodedEventValue;
    }

    public MobileEvent withCrashDecodedEventValue(String crashDecodedEventValue) {
        this.crashDecodedEventValue = crashDecodedEventValue;
        return this;
    }

    public String getCrashReasonType() {
        return crashReasonType;
    }

    public void setCrashReasonType(String crashReasonType) {
        this.crashReasonType = crashReasonType;
    }

    public MobileEvent withCrashReasonType(String crashReasonType) {
        this.crashReasonType = crashReasonType;
        return this;
    }

    public String getCrashReason() {
        return crashReason;
    }

    public void setCrashReason(String crashReason) {
        this.crashReason = crashReason;
    }

    public MobileEvent withCrashReason(String crashReason) {
        this.crashReason = crashReason;
        return this;
    }

    public String getCrashReasonMessage() {
        return crashReasonMessage;
    }

    public void setCrashReasonMessage(String crashReasonMessage) {
        this.crashReasonMessage = crashReasonMessage;
    }

    public MobileEvent withCrashReasonMessage(String crashReasonMessage) {
        this.crashReasonMessage = crashReasonMessage;
        return this;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    public MobileEvent withErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
        return this;
    }

    public BigInteger getDecodeTimestamp() {
        return decodeTimestamp;
    }

    public void setDecodeTimestamp(BigInteger decodeTimestamp) {
        this.decodeTimestamp = decodeTimestamp;
    }

    public MobileEvent withDecodeTimestamp(BigInteger decodeTimestamp) {
        this.decodeTimestamp = decodeTimestamp;
        return this;
    }

    public String getDecodeRequiredSymbolsId() {
        return decodeRequiredSymbolsId;
    }

    public void setDecodeRequiredSymbolsId(String decodeRequiredSymbolsId) {
        this.decodeRequiredSymbolsId = decodeRequiredSymbolsId;
    }

    public MobileEvent withDecodeRequiredSymbolsId(String decodeRequiredSymbolsId) {
        this.decodeRequiredSymbolsId = decodeRequiredSymbolsId;
        return this;
    }

    public String[] getDecodeUsedSymbolsIds() {
        return decodeUsedSymbolsIds;
    }

    public void setDecodeUsedSymbolsIds(String[] decodeUsedSymbolsIds) {
        this.decodeUsedSymbolsIds = decodeUsedSymbolsIds;
    }

    public MobileEvent withDecodeUsedSymbolsIds(String[] decodeUsedSymbolsIds) {
        this.decodeUsedSymbolsIds = decodeUsedSymbolsIds;
        return this;
    }

    public String[] getDecodeMissedSymbolsIds() {
        return decodeMissedSymbolsIds;
    }

    public void setDecodeMissedSymbolsIds(String[] decodeMissedSymbolsIds) {
        this.decodeMissedSymbolsIds = decodeMissedSymbolsIds;
    }

    public MobileEvent withDecodeMissedSymbolsIds(String[] decodeMissedSymbolsIds) {
        this.decodeMissedSymbolsIds = decodeMissedSymbolsIds;
        return this;
    }

    public String[] getDecodeUsedSystemSymbolsIds() {
        return decodeUsedSystemSymbolsIds;
    }

    public void setDecodeUsedSystemSymbolsIds(String[] decodeUsedSystemSymbolsIds) {
        this.decodeUsedSystemSymbolsIds = decodeUsedSystemSymbolsIds;
    }

    public MobileEvent withDecodeUsedSystemSymbolsIds(String[] decodeUsedSystemSymbolsIds) {
        this.decodeUsedSystemSymbolsIds = decodeUsedSystemSymbolsIds;
        return this;
    }

    public String[] getDecodeMissedSystemSymbolsIds() {
        return decodeMissedSystemSymbolsIds;
    }

    public void setDecodeMissedSystemSymbolsIds(String[] decodeMissedSystemSymbolsIds) {
        this.decodeMissedSystemSymbolsIds = decodeMissedSystemSymbolsIds;
    }

    public MobileEvent withDecodeMissedSystemSymbolsIds(String[] decodeMissedSystemSymbolsIds) {
        this.decodeMissedSystemSymbolsIds = decodeMissedSystemSymbolsIds;
        return this;
    }

    public String getDecodeStatus() {
        return decodeStatus;
    }

    public void setDecodeStatus(String decodeStatus) {
        this.decodeStatus = decodeStatus;
    }

    public MobileEvent withDecodeStatus(String decodeStatus) {
        this.decodeStatus = decodeStatus;
        return this;
    }

    public String getDecodeErrorDetails() {
        return decodeErrorDetails;
    }

    public void setDecodeErrorDetails(String decodeErrorDetails) {
        this.decodeErrorDetails = decodeErrorDetails;
    }

    public MobileEvent withDecodeErrorDetails(String decodeErrorDetails) {
        this.decodeErrorDetails = decodeErrorDetails;
        return this;
    }

    public Long getDecodeOriginalAPIKey() {
        return decodeOriginalAPIKey;
    }

    public void setDecodeOriginalAPIKey(Long decodeOriginalAPIKey) {
        this.decodeOriginalAPIKey = decodeOriginalAPIKey;
    }

    public MobileEvent withDecodeOriginalAPIKey(Long decodeOriginalAPIKey) {
        this.decodeOriginalAPIKey = decodeOriginalAPIKey;
        return this;
    }

    public BigInteger getDecodeOriginalEventID() {
        return decodeOriginalEventID;
    }

    public void setDecodeOriginalEventID(BigInteger decodeOriginalEventID) {
        this.decodeOriginalEventID = decodeOriginalEventID;
    }

    public MobileEvent withDecodeOriginalEventID(BigInteger decodeOriginalEventID) {
        this.decodeOriginalEventID = decodeOriginalEventID;
        return this;
    }

    public Integer getSign() {
        return sign;
    }

    public void setSign(Integer sign) {
        this.sign = sign;
    }

    public MobileEvent withSign(Integer sign) {
        this.sign = sign;
        return this;
    }

    public BigInteger getVersion() {
        return version;
    }

    public void setVersion(BigInteger version) {
        this.version = version;
    }

    public MobileEvent withVersion(BigInteger version) {
        this.version = version;
        return this;
    }

    @Override
    public long getTime() {
        return 0;
    }

    @Override
    public ChunkDescriptor getInsertDescr() {
        return () -> stream(MobileEvent.class.getDeclaredFields())
                .map(field -> field.getAnnotation(Column.class).name())
                .toArray(String[]::new);
    }

    @Override
    public void dumpFields(@NotNull CommandOutput output) {
        stream(MobileEvent.class.getDeclaredFields())
                .forEach(field -> {
                    try {
                        output.out(Serialization.objectToBinary(field.get(this), field.getType(), field.getAnnotation(Column.class).type()));
                    } catch (IllegalAccessException e) {
                        propagate(e);
                    }
                });
    }

    public static ErrorCountMapper<MobileEvent> getRowMapper() {
        return new ErrorCountMapperImpl<MobileEvent>((resultSet, rowNum) -> new MobileEvent(resultSet));
    }

    public static String getCreateTableTemplate() {
        return format("CREATE TABLE IF NOT EXISTS %%s.%%s (%s) ENGINE = StripeLog;",
                stream(MobileEvent.class.getDeclaredFields())
                        .map(field -> format("`%s` %s", field.getAnnotation(Column.class).name(), field.getAnnotation(Column.class).type()))
                        .collect(joining(", ")));
    }

}
