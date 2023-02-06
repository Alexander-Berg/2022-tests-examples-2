#pragma once

#include <portal/morda/blocks/metrics/histogram_base.h>
#include <portal/morda/blocks/metrics/statistics_collector.h>

#include <library/cpp/threading/light_rw_lock/lightrwlock.h>

#include <util/generic/hash.h>
#include <util/generic/ptr.h>
#include <util/generic/string.h>

namespace NMordaBlocks {

    class TNamedValueEvent;

    class TTestStatisticsCollector : public IStatisticsCollector {
    public:
        TTestStatisticsCollector() = default;
        ~TTestStatisticsCollector() override = default;

        bool AddHistogramBaseIfNotCreated(const TString& name,
                const TString& description, TIntervalsHolderPtr intervals) override;

        bool AddHistogramIfNotCreated(const TString& name,
                const TString& description, double min, double max, size_t bucketCnt) override;

        bool AddLinearHistogramIfNotCreated(const TString& name,
                const TString& description, double min, double max, size_t bucketCnt) override;

        bool AddBooleanHistogramIfNotCreated(
                const TString& name, const TString& description) override;

        void AddSimpleEvent(const TString& eventName) override;

        void AddHistogramEvent(const TNamedValueEvent& event) override;

        void AddHistogram(THistogramBasePtr metric);
        THistogramBasePtr GetHistogram(const TString& name) const;
        size_t GetSimpleEventsCount(const TString& name) const;

    private:
        bool AddHistogram(const TString& name, EHistogramType type,
                const std::function<THistogramBasePtr()> createHistogram);

    private:
        mutable TLightRWLock RWLock_;
        THashMap<TString, THistogramBasePtr> Histograms_;
        THashMap<TString, size_t> SimpleEvents_;
    };

}  // namespace NMordaBlocks
