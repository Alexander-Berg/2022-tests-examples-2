package ru.yandex.metrika.segments.core.meta;

import java.util.List;

import com.google.common.collect.Lists;
import org.apache.commons.lang3.tuple.Pair;
import org.junit.Test;

/**
 * @author jkee
 */

public class ColumnMetaTest {

    List<Pair<String, String>> columns = Lists.newArrayList();

    @Test
    public void testParse() throws Exception {
        initTable();
        for (Pair<String, String> column : columns) {
            ColumnMeta meta = ColumnMeta.parseColumnMeta(column.getLeft(), column.getRight());
            System.out.println(meta);
        }
    }

    private void initTable() {
        put("CounterID                          ", "UInt32          ");
        put("StartDate                          ", "Date            ");
        put("Sign                               ", "Int8            ");
        put("IsNew                              ", "UInt8           ");
        put("VisitID                            ", "UInt64          ");
        put("UserID                             ", "UInt64          ");
        put("StartTime                          ", "DateTime        ");
        put("Duration                           ", "UInt32          ");
        put("UTCStartTime                       ", "DateTime        ");
        put("PageViews                          ", "Int32           ");
        put("Hits                               ", "Int32           ");
        put("IsBounce                           ", "UInt8           ");
        put("Referer                            ", "String          ");
        put("StartURL                           ", "String          ");
        put("EndURL                             ", "String          ");
        put("LinkURL                            ", "String          ");
        put("IsDownload                         ", "UInt8           ");
        put("TraficSourceID                     ", "Int8            ");
        put("SearchEngineID                     ", "UInt16          ");
        put("SearchPhrase                       ", "String          ");
        put("AdvEngineID                        ", "UInt8           ");
        put("PlaceID                            ", "Int32           ");
        put("RefererCategoryID                  ", "UInt16          ");
        put("RefererRegionID                    ", "UInt32          ");
        put("URLCategoryID                      ", "UInt16          ");
        put("URLRegionID                        ", "UInt32          ");
        put("IsYandex                           ", "UInt8           ");
        put("GoalReachesDepth                   ", "Int32           ");
        put("GoalReachesURL                     ", "Int32           ");
        put("GoalReachesAny                     ", "Int32           ");
        put("SocialSourceNetworkID              ", "UInt8           ");
        put("SocialSourcePage                   ", "String          ");
        put("MobilePhoneModel                   ", "String          ");
        put("ClientEventTime                    ", "DateTime        ");
        put("RegionID                           ", "UInt32          ");
        put("ClientIP                           ", "UInt32          ");
        put("RemoteIP                           ", "UInt32          ");
        put("IPNetworkID                        ", "UInt32          ");
        put("SilverlightVersion3                ", "UInt32          ");
        put("CodeVersion                        ", "UInt32          ");
        put("ResolutionWidth                    ", "UInt16          ");
        put("ResolutionHeight                   ", "UInt16          ");
        put("UserAgentMajor                     ", "UInt16          ");
        put("UserAgentMinor                     ", "UInt16          ");
        put("WindowClientWidth                  ", "UInt16          ");
        put("WindowClientHeight                 ", "UInt16          ");
        put("SilverlightVersion2                ", "UInt8           ");
        put("SilverlightVersion4                ", "UInt16          ");
        put("FlashVersion3                      ", "UInt16          ");
        put("FlashVersion4                      ", "UInt16          ");
        put("ClientTimeZone                     ", "Int16           ");
        put("OS                                 ", "UInt8           ");
        put("UserAgent                          ", "UInt8           ");
        put("ResolutionDepth                    ", "UInt8           ");
        put("FlashMajor                         ", "UInt8           ");
        put("FlashMinor                         ", "UInt8           ");
        put("NetMajor                           ", "UInt8           ");
        put("NetMinor                           ", "UInt8           ");
        put("SilverlightVersion1                ", "UInt8           ");
        put("Age                                ", "UInt8           ");
        put("Gender                             ", "UInt8           ");
        put("Income                             ", "UInt8           ");
        put("JavaEnable                         ", "UInt8           ");
        put("CookieEnable                       ", "UInt8           ");
        put("JavascriptEnable                   ", "UInt8           ");
        put("IsMobile                           ", "UInt8           ");
        put("BrowserLanguage                    ", "UInt16          ");
        put("BrowserCountry                     ", "UInt16          ");
        put("Interests                          ", "UInt16          ");
        put("Robotness                          ", "UInt8           ");
        put("Goals.ID                           ", "Array(UInt32)   ");
        put("Goals.Serial                       ", "Array(UInt32)   ");
        put("Goals.EventTime                    ", "Array(DateTime) ");
        put("Goals.Price                        ", "Array(Int64)    ");
        put("Goals.OrderID                      ", "Array(String)   ");
        put("Goals.CurrencyID                   ", "Array(UInt32)   ");
        put("WatchIDs                           ", "Array(UInt64)   ");
        put("ParamSumPrice                      ", "Int64           ");
        put("ParamCurrency                      ", "FixedString(3)  ");
        put("ParamCurrencyID                    ", "UInt16          ");
        put("Clicks.LogID                       ", "Array(UInt64)   ");
        put("Clicks.EventID                     ", "Array(Int32)    ");
        put("Clicks.GoodEvent                   ", "Array(Int32)    ");
        put("Clicks.EventTime                   ", "Array(DateTime) ");
        put("Clicks.PriorityID                  ", "Array(Int32)    ");
        put("Clicks.PhraseID                    ", "Array(Int32)    ");
        put("Clicks.PageID                      ", "Array(Int32)    ");
        put("Clicks.PlaceID                     ", "Array(Int32)    ");
        put("Clicks.TypeID                      ", "Array(Int32)    ");
        put("Clicks.ResourceID                  ", "Array(Int32)    ");
        put("Clicks.Cost                        ", "Array(UInt32)   ");
        put("Clicks.ClientIP                    ", "Array(UInt32)   ");
        put("Clicks.DomainID                    ", "Array(UInt32)   ");
        put("Clicks.URL                         ", "Array(String)   ");
        put("Clicks.Attempt                     ", "Array(UInt8)    ");
        put("Clicks.OrderID                     ", "Array(UInt32)   ");
        put("Clicks.BannerID                    ", "Array(UInt32)   ");
        put("Clicks.MarketCategoryID            ", "Array(UInt32)   ");
        put("Clicks.MarketPP                    ", "Array(UInt32)   ");
        put("Clicks.MarketCategoryName          ", "Array(String)   ");
        put("Clicks.MarketPPName                ", "Array(String)   ");
        put("Clicks.AWAPSCampaignName           ", "Array(String)   ");
        put("Clicks.PageName                    ", "Array(String)   ");
        put("Clicks.TargetType                  ", "Array(UInt16)   ");
        put("Clicks.TargetPhraseID              ", "Array(UInt64)   ");
        put("Clicks.ContextType                 ", "Array(UInt8)    ");
        put("Clicks.SelectType                  ", "Array(Int8)     ");
        put("Clicks.Options                     ", "Array(String)   ");
        put("OpenstatServiceName                ", "String          ");
        put("OpenstatCampaignID                 ", "String          ");
        put("OpenstatAdID                       ", "String          ");
        put("OpenstatSourceID                   ", "String          ");
        put("UTMSource                          ", "String          ");
        put("UTMMedium                          ", "String          ");
        put("UTMCampaign                        ", "String          ");
        put("UTMContent                         ", "String          ");
        put("UTMTerm                            ", "String          ");
        put("FromTag                            ", "String          ");
        put("HasGCLID                           ", "UInt8           ");
        put("FirstVisit                         ", "DateTime        ");
        put("PredLastVisit                      ", "Date            ");
        put("LastVisit                          ", "Date            ");
        put("TotalVisits                        ", "UInt32          ");
        put("TraficSource.ID                    ", "Array(Int8)     ");
        put("TraficSource.SearchEngineID        ", "Array(UInt16)   ");
        put("TraficSource.AdvEngineID           ", "Array(UInt8)    ");
        put("TraficSource.PlaceID               ", "Array(UInt16)   ");
        put("TraficSource.SocialSourceNetworkID ", "Array(UInt8)    ");
        put("TraficSource.Domain                ", "Array(String)   ");
        put("TraficSource.SearchPhrase          ", "Array(String)   ");
        put("TraficSource.SocialSourcePage      ", "Array(String)   ");
        put("Attendance                         ", "FixedString(16) ");
        put("CLID                               ", "UInt32          ");
        put("NormalizedRefererHash              ", "UInt64          ");
        put("NormalizedEndURLHash               ", "UInt64          ");
        put("TopLevelDomain                     ", "UInt64          ");
        put("URLScheme                          ", "UInt64          ");
        put("OpenstatServiceNameHash            ", "UInt64          ");
        put("OpenstatCampaignIDHash             ", "UInt64          ");
        put("OpenstatAdIDHash                   ", "UInt64          ");
        put("OpenstatSourceIDHash               ", "UInt64          ");
        put("UTMSourceHash                      ", "UInt64          ");
        put("UTMMediumHash                      ", "UInt64          ");
        put("UTMCampaignHash                    ", "UInt64          ");
        put("UTMContentHash                     ", "UInt64          ");
        put("UTMTermHash                        ", "UInt64          ");
        put("FromHash                           ", "UInt64          ");
        put("WebVisorEnabled                    ", "UInt8           ");
        put("WebVisorActivity                   ", "UInt32          ");
        put("ParsedParams.Key1                  ", "Array(String)   ");
        put("ParsedParams.Key2                  ", "Array(String)   ");
        put("ParsedParams.Key3                  ", "Array(String)   ");
        put("ParsedParams.Key4                  ", "Array(String)   ");
        put("ParsedParams.Key5                  ", "Array(String)   ");
        put("ParsedParams.ValueString           ", "Array(String)   ");
        put("ParsedParams.ValueDouble           ", "Array(Float64)  ");
        put("Market.Type                        ", "Array(UInt8)    ");
        put("Market.GoalID                      ", "Array(UInt32)   ");
        put("Market.OrderID                     ", "Array(String)   ");
        put("Market.OrderPrice                  ", "Array(Int64)    ");
        put("Market.PP                          ", "Array(UInt32)   ");
        put("Market.DirectPlaceID               ", "Array(UInt32)   ");
        put("Market.DirectOrderID               ", "Array(UInt32)   ");
        put("Market.GoodID                      ", "Array(String)   ");
        put("Market.GoodName                    ", "Array(String)   ");
        put("Market.GoodQuantity                ", "Array(Int32)    ");
        put("Market.GoodPrice                   ", "Array(Int64)    ");
    }

    private void put(String name, String type) {
        columns.add(Pair.of(name.trim(), type.trim()));
    }
}
