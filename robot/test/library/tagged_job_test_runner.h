#pragma once

#include <robot/library/yt/static/tags.h>

namespace NJupiter {

/*
 * Utility test class to run TTaggedJob (mapper/reducer)
 * with specified test input and store output in specified output vectors
 *
 * The class is designed for a single use case. Feel free to refactor/extend it
 */
template<typename TTaggedJobImpl>
class TTaggedJobTestRunner {
    TTagedSchemeBuilder SchemeBuilder;
    TVector<TVector<THolder<NYT::Message>>> InputTables;
    TVector<std::function<void(const NYT::Message&)>> OutputTables;

public:
    template<typename TProto>
    TTaggedJobTestRunner& AddInputTable(const TVector<TProto>& rows, TInputTag<TProto> tag);

    template<typename TProto>
    TTaggedJobTestRunner& AddPrimaryInputTable(const TVector<TProto>& rows, TInputTag<TProto> tag);

    template<typename TProto>
    TTaggedJobTestRunner& AddOutputTable(TVector<TProto>& rows, TOutputTag<TProto> tag);

    TTaggedJobTestRunner& ReduceBy(const NYT::TSortColumns& keys);

    void Run(const TTaggedJobImpl& mapperOrReducer = TTaggedJobImpl());
};

template<typename TMapper>
using TMapperTestRunner = TTaggedJobTestRunner<TMapper>;

template<typename TReducer>
using TReducerTestRunner = TTaggedJobTestRunner<TReducer>;

}

#include "tagged_job_test_runner-inl.h"
