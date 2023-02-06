create table hour2
(
    CounterID           UInt32,
    StartDate           Date,
    Hour                UInt8,
    Visits              AggregateFunction(sum, Int8),
    PageViewsSum        AggregateFunction(sum, Int64),
    SumTime             AggregateFunction(sum, Int64),
    OneHour             AggregateFunction(sumIf, Int8, UInt8),
    Users               AggregateFunction(uniq, UInt64),
    RecountRequestID    SimpleAggregateFunction(max, String),
    IsRobot             UInt8,
    NoRobotVisits       AggregateFunction(sum, Int8)             default Visits,
    NoRobotPageViewsSum AggregateFunction(sum, Int64)            default PageViewsSum,
    NoRobotSumTime      AggregateFunction(sum, Int64)            default SumTime,
    NoRobotOneHour      AggregateFunction(sumIf, Int8, UInt8)    default OneHour,
    NoRobotUsers        AggregateFunction(uniqIf, UInt64, UInt8) default CAST(CAST(Users, 'String'),
        'AggregateFunction(uniqIf, UInt64, UInt8)')
)
engine = AggregatingMergeTree()
PARTITION BY toStartOfMonth(StartDate)
PRIMARY KEY (CounterID, StartDate, Hour)
ORDER BY (CounterID, StartDate, Hour, IsRobot)
SETTINGS index_granularity = 256;

