CREATE TABLE basic_counter_stat
(
    `CounterID` UInt32,
    `StartDate` Date,
    `Visits` AggregateFunction(sum, Int8),
    `PageViewsSum` AggregateFunction(sum, Int64),
    `SumTime` AggregateFunction(sum, Int64),
    `OneHour` AggregateFunction(sumIf, Int8, UInt8),
    `NewUsers` AggregateFunction(uniqIf, UInt64, UInt8),
    `Users` AggregateFunction(uniq, UInt64),
    `GoalsReached` AggregateFunction(sum, Int64),
    `RecountRequestID` SimpleAggregateFunction(max, String),
    `IsRobot` UInt8,
    `NoRobotVisits` AggregateFunction(sum, Int8) DEFAULT Visits,
    `NoRobotPageViewsSum` AggregateFunction(sum, Int64) DEFAULT PageViewsSum,
    `NoRobotSumTime` AggregateFunction(sum, Int64) DEFAULT SumTime,
    `NoRobotOneHour` AggregateFunction(sumIf, Int8, UInt8) DEFAULT OneHour,
    `NoRobotNewUsers` AggregateFunction(uniqIf, UInt64, UInt8) DEFAULT NewUsers,
    `NoRobotUsers` AggregateFunction(uniqIf, UInt64, UInt8) DEFAULT CAST(CAST(Users, 'String'), 'AggregateFunction(uniqIf, UInt64, UInt8)'),
    `NoRobotGoalsReached` AggregateFunction(sum, Int64),
    `HttpVisits` AggregateFunction(sumIf, Int8, UInt8),
    `HttpsVisits` AggregateFunction(sumIf, Int8, UInt8),
    `NoRobotHttpVisits` AggregateFunction(sumIf, Int8, UInt8),
    `NoRobotHttpsVisits` AggregateFunction(sumIf, Int8, UInt8)
)
ENGINE = AggregatingMergeTree()
PARTITION BY toStartOfMonth(StartDate)
PRIMARY KEY (CounterID, StartDate)
ORDER BY (CounterID, StartDate, IsRobot)
SETTINGS index_granularity = 256;
