#pragma once

#include <robot/quality/robotrank/rr_tool/proto/schema.pb.h>

#include <mapreduce/yt/interface/client.h>
#include <mapreduce/yt/util/temp_table.h>

#include <robot/lemur/protos/schema.pb.h>
#include <yweb/robot/ukrop/algo/exportparsers/extdatarank_export_parser.h>
#include <yweb/robot/ukrop/fresh/algo/filters/filters.h>

#include <library/cpp/getopt/last_getopt.h>
#include <library/cpp/getopt/modchooser.h>

#include <google/protobuf/messagext.h>

#include <util/draft/datetime.h>
#include <util/random/random.h>
#include <library/cpp/string_utils/url/url.h>


void AddEdrLabels(const NUkrop::TZoneConfigPtr& zoneConfig, const NUkrop::TEDRSample& edrSample, NRRProto::TLabels* result);
