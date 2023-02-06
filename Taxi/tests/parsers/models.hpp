#pragma once

#include <userver/formats/json_fwd.hpp>

namespace models {

struct DbidUuid;

DbidUuid Parse(const ::formats::json::Value& value,
               formats::parse::To<DbidUuid>);

}  // namespace models

namespace shuttle_control::models {

struct RouteInfo;
struct SegmentIdT;
struct ShuttleDescriptor;
enum class DRWState;
enum class WorkModeType;
class Route;
struct ShuttleStatefulPosition;
struct ShuttleEnRoutePosition;
struct ShuttleTripState;
enum class DriverBlockReason;
struct ShortBookingInfo;
struct BookedSeatSegment;
struct ShuttleStopInfo;
struct ShuttleLoad;
struct PriceData;
struct GeoData;
enum class PauseState;

RouteInfo Parse(const ::formats::json::Value& value,
                formats::parse::To<RouteInfo>);

SegmentIdT Parse(const ::formats::json::Value& value,
                 formats::parse::To<SegmentIdT>);

ShuttleDescriptor Parse(const ::formats::json::Value& value,
                        formats::parse::To<ShuttleDescriptor>);

DRWState Parse(const ::formats::json::Value& value,
               formats::parse::To<DRWState>);

WorkModeType Parse(const ::formats::json::Value& value,
                   formats::parse::To<WorkModeType>);

Route Parse(const ::formats::json::Value& value, formats::parse::To<Route>);

ShuttleStatefulPosition Parse(const ::formats::json::Value& value,
                              formats::parse::To<ShuttleStatefulPosition>);

ShuttleEnRoutePosition Parse(const ::formats::json::Value& value,
                             formats::parse::To<ShuttleEnRoutePosition>);

ShuttleTripState Parse(const ::formats::json::Value& value,
                       formats::parse::To<ShuttleTripState>);

DriverBlockReason Parse(const ::formats::json::Value& value,
                        formats::parse::To<DriverBlockReason>);

ShortBookingInfo Parse(const ::formats::json::Value& value,
                       formats::parse::To<ShortBookingInfo>);

BookedSeatSegment Parse(const ::formats::json::Value& value,
                        formats::parse::To<BookedSeatSegment>);

ShuttleStopInfo Parse(const ::formats::json::Value& value,
                      formats::parse::To<ShuttleStopInfo>);

ShuttleLoad Parse(const ::formats::json::Value& value,
                  formats::parse::To<ShuttleLoad>);

PriceData Parse(const ::formats::json::Value& value,
                formats::parse::To<PriceData>);

GeoData Parse(const ::formats::json::Value& value, formats::parse::To<GeoData>);

PauseState Parse(const ::formats::json::Value& value,
                 formats::parse::To<PauseState>);

}  // namespace shuttle_control::models
