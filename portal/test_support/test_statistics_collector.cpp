#include "test_statistics_collector.h"

#include <portal/morda/blocks/metrics/histogram.h>
#include <portal/morda/blocks/metrics/named_value_event.h>

#include <util/generic/yexception.h>

namespace NMordaBlocks {

    bool TTestStatisticsCollector::AddHistogramBaseIfNotCreated(
            const TString& name, const TString& description, TIntervalsHolderPtr intervals) {
        const auto createHistogram = [&name, &description, &intervals]() {
            return MakeIntrusive<THistogramBase>(name, description, intervals);
        };
        return AddHistogram(name, EHistogramType::Base, createHistogram);
    }

    bool TTestStatisticsCollector::AddHistogramIfNotCreated(const TString& name,
            const TString& description, double min, double max, size_t bucketCnt) {
        const auto createHistogram = [&name, &description, &min, &max, &bucketCnt]() {
            return MakeIntrusive<THistogram>(name, description, min, max, bucketCnt);
        };
        return AddHistogram(name, EHistogramType::Default, createHistogram);
    }

    bool TTestStatisticsCollector::AddLinearHistogramIfNotCreated(const TString& name,
            const TString& description, double min, double max, size_t bucketCnt) {
        const auto createHistogram = [&name, &description, &min, &max, &bucketCnt]() {
            return MakeIntrusive<TLinearHistogram>(name, description, min, max, bucketCnt);
        };
        return AddHistogram(name, EHistogramType::Linear, createHistogram);
    }

    bool TTestStatisticsCollector::AddBooleanHistogramIfNotCreated(
            const TString& name, const TString& description) {
        const auto createHistogram = [&name, &description]() {
            return MakeIntrusive<TBooleanHistogram>(name, description);
        };
        return AddHistogram(name, EHistogramType::Boolean, createHistogram);
    }

    void TTestStatisticsCollector::AddHistogramEvent(const TNamedValueEvent& event) {
        TWriteGuardBase<TLightRWLock> guard(RWLock_);
        Histograms_.at(event.Name)->Consume(event);
    }

    void TTestStatisticsCollector::AddSimpleEvent(const TString& eventName) {
        TWriteGuardBase<TLightRWLock> guard(RWLock_);
        auto it = SimpleEvents_.emplace(eventName, 0).first;
        ++(it->second);
    }

    void TTestStatisticsCollector::AddHistogram(THistogramBasePtr histogram) {
        TWriteGuardBase<TLightRWLock> guard(RWLock_);
        Histograms_[histogram->Name()] = histogram;
    }

    THistogramBasePtr TTestStatisticsCollector::GetHistogram(const TString& name) const {
        TReadGuardBase<TLightRWLock> guard(RWLock_);
        auto it = Histograms_.find(name);
        if (it == Histograms_.end()) {
            return nullptr;
        }
        return it->second;
    }

    size_t TTestStatisticsCollector::GetSimpleEventsCount(const TString& name) const {
        TReadGuardBase<TLightRWLock> guard(RWLock_);
        auto it = SimpleEvents_.find(name);
        if (it == SimpleEvents_.end()) {
            return 0;
        }
        return it->second;
    }

    bool TTestStatisticsCollector::AddHistogram(const TString& name, EHistogramType type,
            const std::function<THistogramBasePtr()> createHistogram) {
        TWriteGuardBase<TLightRWLock> guard(RWLock_);
        if (!Histograms_.contains(name)) {
            Histograms_.insert(std::make_pair(name, createHistogram()));
            return true;
        } else if (Histograms_.at(name)->Type() != type) {
            ythrow yexception() << "Attemt to add histogram with another type";
        }
        return false;
    }

}  // namespace NMordaBlocks
