#include "load_signals_from_file.h"

#include <library/cpp/json/json_value.h>
#include <library/cpp/json/json_reader.h>

#include <util/stream/file.h>

namespace NTaxi::NGraph2 {
    std::vector<NTaxi::NGraph2::TGpsSignal> LoadSignalsFromFile(
        const TString& filename, bool noSpeed) {
        TFileInput file(filename);
        NJson::TJsonValue root;
        NJson::ReadJsonTree(&file, true, &root);

        std::vector<NTaxi::NGraph2::TGpsSignal> result;

        TString uid = "test-uid";
        TString clid = "test-clid";

        NJson::TJsonValue track = root["track"];
        for (const NJson::TJsonValue& signalJson : track.GetArraySafe()) {
            NTaxi::NGraph2::TGpsSignal gpsSignal;
            gpsSignal.SetLon(signalJson["lon"].GetDoubleSafe());
            gpsSignal.SetLat(signalJson["lat"].GetDoubleSafe());
            gpsSignal.SetTime(signalJson["timestamp"].GetUIntegerSafe());
            if (!noSpeed) {
                gpsSignal.SetAverageSpeed(signalJson["speed"].GetDoubleSafe());
            }

            result.emplace_back(std::move(gpsSignal));
        }

        return result;
    }

}
