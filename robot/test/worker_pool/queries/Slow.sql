$next_time = ($d) -> { return Unwrap(cast(CurrentUtcDatetime($d) + Interval("PT5S") as uint64) * 1000000); };
SELECT CAST(Common::SleepUntil($next_time(Data)) AS Utf8) || Data as Data FROM Input;
