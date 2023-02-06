#pragma once

#include "tagged_job_test_runner.h"

namespace NJupiter {

    namespace {

        class TStubReader : public NYT::IProtoReaderImpl {
        private:
            const TVector<TVector<THolder<NYT::Message>>>& InputTables;
            ui32 TableIndex;
            ui32 RowIndex;

        public:
            explicit TStubReader(const TVector<TVector<THolder<NYT::Message>>>& tables);

            bool IsValid() const override;
            void Next() override;
            ui32 GetTableIndex() const override;
            ui32 GetRangeIndex() const override;
            ui64 GetRowIndex() const override;
            void NextKey() override;
            TMaybe<size_t> GetReadByteCount() const override;
            void ReadRow(NYT::Message* row) override;
        };

        class TStubWriter : public NYT::IProtoWriterImpl {
            const TVector<std::function<void(const NYT::Message&)>>& OutputTables;

        public:
            explicit TStubWriter(const TVector<std::function<void(const NYT::Message&)>>& outputTables);
            size_t GetTableCount() const override;
            void FinishTable(size_t tableIndex) override;
            void Abort() override;
            void AddRow(const Message& row, size_t tableIndex) override;
            void AddRow(Message&& row, size_t tableIndex) override;
        };

        template<typename TProto>
        TVector<THolder<NYT::Message>> CopyInputVector(const TVector<TProto>& rows) {
            auto rowsCopy = TVector<THolder<NYT::Message>>();
            rowsCopy.reserve(rows.size());

            for (const auto& row : rows) {
                rowsCopy.push_back(MakeHolder<TProto>(row));
            }

            return rowsCopy;
        }

    } // namespace

    template<typename TTaggedJobImpl>
    template<typename TProto>
    TTaggedJobTestRunner<TTaggedJobImpl>& TTaggedJobTestRunner<TTaggedJobImpl>::AddInputTable(const TVector<TProto>& rows, TInputTag<TProto> tag) {
        static_assert(std::is_base_of<NYT::Message, TProto>::value);

        InputTables.push_back(CopyInputVector(rows));
        SchemeBuilder.AddInput(tag);
        return *this;
    }

    template<typename TTaggedJobImpl>
    template<typename TProto>
    TTaggedJobTestRunner<TTaggedJobImpl>&
    TTaggedJobTestRunner<TTaggedJobImpl>::AddPrimaryInputTable(const TVector<TProto>& rows, TInputTag<TProto> tag) {
        static_assert(std::is_base_of<NYT::Message, TProto>::value);

        InputTables.push_back(CopyInputVector(rows));
        SchemeBuilder.AddInputPrimary(tag, TProto().GetDescriptor());
        return *this;
    }

    template<typename TTaggedJobImpl>
    template<typename TProto>
    TTaggedJobTestRunner<TTaggedJobImpl>& TTaggedJobTestRunner<TTaggedJobImpl>::AddOutputTable(TVector<TProto>& rows, TOutputTag<TProto> tag) {
        static_assert(std::is_base_of<NYT::Message, TProto>::value);

        OutputTables.push_back([&rows](const Message& row) {
            Y_ENSURE(row.GetDescriptor() == TProto::descriptor(), "Invalid row type");
            rows.push_back(static_cast<const TProto&>(row));
        });

        SchemeBuilder.AddOutput(tag);
        return *this;
    }

    template<typename TTaggedJobImpl>
    TTaggedJobTestRunner<TTaggedJobImpl>& TTaggedJobTestRunner<TTaggedJobImpl>::ReduceBy(const NYT::TSortColumns& keys) {
        SchemeBuilder.SetReduceKey(keys);
        return *this;
    }

    template<typename TTaggedJobImpl>
    void TTaggedJobTestRunner<TTaggedJobImpl>::Run(const TTaggedJobImpl& mapperOrReducer) {
        TBufferStream stream;
        mapperOrReducer.Save(stream);

        auto deserialized = TTaggedJobImpl();
        deserialized.Load(stream);
        deserialized.SetScheme(SchemeBuilder.GetScheme());

        NYT::TTableReader<NYT::Message> reader(MakeIntrusive<TStubReader>(InputTables));
        NYT::TTableWriter<NYT::Message> writer(MakeIntrusive<TStubWriter>(OutputTables));

        deserialized.Start(&writer);
        deserialized.Do(&reader, &writer);
        deserialized.Finish(&writer);
    }


    TStubReader::TStubReader(const TVector<TVector<THolder<NYT::Message>>>& tables)
        : InputTables(tables)
        , TableIndex(0)
        , RowIndex(0)
    {
    }

    bool TStubReader::IsValid() const {
        return TableIndex < InputTables.size() && RowIndex < InputTables[TableIndex].size();
    }

    void TStubReader::Next() {
        Y_ENSURE(IsValid(), "Reader is not valid");

        if (++RowIndex < InputTables[TableIndex].size()) {
            return;
        }

        RowIndex = 0;
        do {
            ++TableIndex;
        }
        while (TableIndex < InputTables.size() && InputTables[TableIndex].empty());
    }

    ui32 TStubReader::GetTableIndex() const {
        Y_ENSURE(IsValid(), "Reader is not valid");
        return TableIndex;
    }

    ui64 TStubReader::GetRowIndex() const {
        Y_ENSURE(IsValid(), "Reader is not valid");
        return RowIndex;
    }

    void TStubReader::ReadRow(NYT::Message* row) {
        Y_ENSURE(IsValid(), "Reader is not valid");
        row->CopyFrom(*InputTables[TableIndex][RowIndex]);
    }

    TMaybe<size_t> TStubReader::GetReadByteCount() const {
        return Nothing();
    }

    ui32 TStubReader::GetRangeIndex() const {
        Y_FAIL("Not supported yet");
        return 0;
    }

    void TStubReader::NextKey() {
        Y_FAIL("Not supported yet");
    }


    TStubWriter::TStubWriter(const TVector<std::function<void(const NYT::Message&)>>& outputTables)
        : OutputTables(outputTables)
    {
    }

    size_t TStubWriter::GetTableCount() const {
        return OutputTables.size();
    }

    void TStubWriter::FinishTable(size_t tableIndex) {
        Y_UNUSED(tableIndex);
    }

    void TStubWriter::Abort()
    {
    }

    void TStubWriter::AddRow(const NYT::Message& row, size_t tableIndex) {
        Y_ENSURE(tableIndex < OutputTables.size(), "Invalid output table");
        OutputTables[tableIndex](row);
    }

    void TStubWriter::AddRow(NYT::Message&& row, size_t tableIndex) {
        AddRow(static_cast<const NYT::Message&>(row), tableIndex);
    }

} /* namespace NJupiter */
