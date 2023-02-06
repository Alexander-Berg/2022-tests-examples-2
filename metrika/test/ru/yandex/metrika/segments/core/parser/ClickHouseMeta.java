package ru.yandex.metrika.segments.core.parser;

import ru.yandex.metrika.segments.clickhouse.ast.Field;
import ru.yandex.metrika.segments.clickhouse.ast.Nested;
import ru.yandex.metrika.segments.clickhouse.ast.Table;
import ru.yandex.metrika.segments.clickhouse.types.TArray;
import ru.yandex.metrika.segments.clickhouse.types.TDate;
import ru.yandex.metrika.segments.clickhouse.types.TDateTime;
import ru.yandex.metrika.segments.clickhouse.types.TInt8;
import ru.yandex.metrika.segments.clickhouse.types.TString;
import ru.yandex.metrika.segments.clickhouse.types.TTuple2;
import ru.yandex.metrika.segments.clickhouse.types.TUInt32;
import ru.yandex.metrika.segments.clickhouse.types.TUInt64;
import ru.yandex.metrika.segments.clickhouse.types.TUInt8;
import ru.yandex.metrika.segments.core.schema.Dictionary;

import static ru.yandex.metrika.segments.clickhouse.ClickHouse.Array;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.Date;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.DateTime;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.Int8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.String;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.UInt32;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.UInt64;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.UInt8;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.field;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.n;
import static ru.yandex.metrika.segments.clickhouse.ClickHouse.tuple;


public class ClickHouseMeta {

    public static final Table visits = new Table("visits");

    public static final Table visits_all = new Table(visits, "default.visits_all");

    public static final Table hits = new Table("hits");

    public static final Table hits_all = new Table(visits, "default.hits_all");


    /** VISITS **/
    public static final Field<TUInt32> CounterID = field(visits, "CounterID", UInt32());
    public static final Field<TDate> StartDate = field(visits, "StartDate", Date());
    public static final Field<TInt8> Sign = field(visits, "Sign", Int8());
    public static final Field<TUInt64> VisitID = field(visits, "VisitID", UInt64());
    public static final Field<TUInt64> UserID = field(visits, "UserID", UInt64());
    public static final Field<TDateTime> StartTime = field(visits, "StartTime", DateTime());
    public static final Field<TUInt32> Duration = field(visits, "Duration", UInt32());
    public static final Field<TInt8> TrafficSourceID = field(visits, "TraficSourceID", Int8());
    public static final Field<TString> StartURL = field(visits, "StartURL", String());
    public static final Field<TUInt32> RegionID = field(visits, "RegionID", UInt32());

    public static final Nested Event = new Nested(visits, "Event", "Ewv");
    public static final Nested Adfox = new Nested(visits, "Adfox", "Adfox_alias");
    public static final Nested AdfoxPuid = new Nested(visits, "AdfoxPuid", "AdfPu");
    public static final Nested AdfoxEvent = new Nested(visits, "AdfoxEvent", "AdfE");
    public static final Nested FakeTuple = new Nested(visits, "FakeTuple", "FakeTupleAlias");

    public static final Field<TArray<TUInt64>> Event_ID = field(visits, "Event.ID", Event, Array(UInt64()));
    public static final Field<TUInt64> Ewv_ID = field(visits, "Ewv.ID", Event, UInt64());

    public static final Field<TArray<TUInt64>> Adfox_OwnerID = field(visits, "Adfox.OwnerID", Adfox, Array(UInt64()));
    public static final Field<TArray<TUInt64>> Adfox_BannerID = field(visits, "Adfox.BannerID", Adfox, Array(UInt64()));
    public static final Field<TArray<TUInt8>> Adfox_Load = field(visits, "Adfox.Load", Adfox, Array(UInt8()));
    public static final Field<TArray<TArray<TUInt32>>> Adfox_EventID = field(visits, "Adfox.EventID", Adfox, Array(Array(UInt32())));
    public static final Field<TArray<TArray<TUInt8>>> Adfox_PuidKey = field(visits, "Adfox.PuidKey", Adfox, Array(Array(UInt8())));
    public static final Field<TArray<TArray<TUInt32>>> Adfox_PuidVal = field(visits, "Adfox.PuidVal", Adfox, Array(Array(UInt32())));

    public static final Field<TUInt64> Adfox_alias_OwnerID = field(visits, "Adfox_alias.OwnerID", Adfox, UInt64());
    public static final Field<TUInt64> Adfox_alias_BannerID = field(visits, "Adfox_alias.BannerID", Adfox, UInt64());
    public static final Field<TUInt8> Adfox_alias_Load = field(visits, "Adfox_alias.Load", Adfox, UInt8());
    public static final Field<TArray<TUInt32>> Adfox_alias_EventID = field(visits, "Adfox_alias.EventID", Adfox, Array(UInt32()));
    public static final Field<TArray<TUInt8>> Adfox_alias_PuidKey = field(visits, "Adfox_alias.PuidKey", Adfox, Array(UInt8()));
    public static final Field<TArray<TUInt32>> Adfox_alias_PuidVal = field(visits, "Adfox_alias.PuidVal", Adfox, Array(UInt32()));

    public static final Field<TUInt32> AdfE_alias_EventID = field(visits, "AdfE_alias.EventID", AdfoxEvent, UInt32());
    public static final Field<TUInt8> AdfPu_alias_PuidKey = field(visits, "AdfPu_alias.PuidKey", AdfoxPuid, UInt8());
    public static final Field<TUInt32> AdfPu_alias_PuidVal = field(visits, "AdfPu_alias.PuidVal", AdfoxPuid, UInt32());

    public static final Field<TArray<TString>> FakeTuple_String = field(visits, "FakeTuple.String", FakeTuple, Array(String()));
    public static final Field<TString> FakeTuple_alias_String = field(visits, "FakeTuple_alias.String", FakeTuple, String());

    public static final Field<TString> NotStreamableField = field(visits, "NotStreamableField", String());

    public static final Field<TUInt32> IntField = field(visits, "IntField", UInt32());
    public static final Field<TUInt64> LongField = field(visits, "LongField", UInt64());
    public static final Field<TDate> DateField = field(visits, "DateField", Date());

    /** HITS **/
    public static final Field<TUInt32> HitsCounterID = field(hits, "CounterID", UInt32());
    public static final Field<TUInt64> WatchID = field(hits, "WatchID", UInt64());
    public static final Field<TDate> EventDate = field(hits, "EventDate", Date());
    public static final Field<TString> URL = field(hits, "URL", String());

    static {
        Event.put(Event_ID, Ewv_ID);
    }

    static {
        Adfox.put(Adfox_OwnerID, Adfox_alias_OwnerID);
        Adfox.put(Adfox_BannerID, Adfox_alias_BannerID);
        Adfox.put(Adfox_Load, Adfox_alias_Load);
        Adfox.put(Adfox_EventID, Adfox_alias_EventID);
        Adfox.put(Adfox_PuidKey, Adfox_alias_PuidKey);
        Adfox.put(Adfox_PuidVal, Adfox_alias_PuidVal);

        AdfoxPuid.put(Adfox_alias_PuidKey, AdfPu_alias_PuidKey);
        AdfoxPuid.put(Adfox_alias_PuidVal, AdfPu_alias_PuidVal);

        AdfoxEvent.put(Adfox_alias_EventID, AdfE_alias_EventID);
    }

    static {
        FakeTuple.put(FakeTuple_String, FakeTuple_alias_String);
    }


    public static final AdfoxPuidKeyDictionary adfox_puid_key = new AdfoxPuidKeyDictionary();
    public static final AdfoxPuidValDictionary adfox_puid_val = new AdfoxPuidValDictionary();

    public static class AdfoxPuidKeyDictionary extends Dictionary<TTuple2<TUInt64, TUInt64>> {
        public final Value<TTuple2<TUInt64, TUInt64>, TString> name = v("name");

        protected AdfoxPuidKeyDictionary() {
            super("adfox_puid_key", tuple(n("owner_id"), n("id")));
        }
    }

    public static class AdfoxPuidValDictionary extends Dictionary<TUInt64> {
        public final Value<TUInt64, TString> name = v("name");

        protected AdfoxPuidValDictionary() {
            super("adfox_puid_val", n("id"));
        }
    }

}
