#pragma once

#include <userver/utils/statistics/min_max_avg.hpp>
#include <userver/utils/statistics/percentile.hpp>
#include <userver/utils/statistics/recentperiod.hpp>

namespace metrix::types {

using AvgCounter = ::utils::statistics::RecentPeriod<
    ::utils::statistics::MinMaxAvg<std::uint64_t>,
    ::utils::statistics::MinMaxAvg<std::uint64_t>,
    ::utils::datetime::SteadyClock>;

using Counter =
    ::utils::statistics::RecentPeriod<std::uint64_t, std::uint64_t,
                                      ::utils::datetime::SteadyClock>;

using MilliLap = ::utils::statistics::RecentPeriod<
    ::utils::statistics::MinMaxAvg<std::uint64_t>,
    ::utils::statistics::MinMaxAvg<std::uint64_t>,
    ::utils::datetime::SteadyClock>;

using PercentileType = ::utils::statistics::Percentile<2048>;
using Percentile =
    ::utils::statistics::RecentPeriod<PercentileType, PercentileType,
                                      ::utils::datetime::SteadyClock>;

using PercentileLapType = ::utils::statistics::Percentile<2048>;
using PercentileLap =
    ::utils::statistics::RecentPeriod<PercentileLapType, PercentileLapType,
                                      ::utils::datetime::SteadyClock>;

using TimeCounter =
    ::utils::statistics::RecentPeriod<std::uint64_t, std::uint64_t,
                                      ::utils::datetime::SteadyClock>;

using TimePercentileType = ::utils::statistics::Percentile<2048>;
using TimePercentile =
    ::utils::statistics::RecentPeriod<TimePercentileType, TimePercentileType,
                                      ::utils::datetime::SteadyClock>;

}
