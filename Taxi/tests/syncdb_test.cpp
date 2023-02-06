#include "syncdb.hpp"

#include <userver/fs/blocking/temp_file.hpp>

#include <boost/filesystem/operations.hpp>
#include <fstream>

#include <userver/utest/utest.hpp>

UTEST(SyncDB, ReopenEmpty) {
  auto tmp_file = fs::blocking::TempFile::Create();
  pilorama::syncdb::SyncDb(tmp_file.GetPath());

  EXPECT_NO_THROW(pilorama::syncdb::SyncDb(tmp_file.GetPath()));
}

UTEST(SyncDB, OpenNew) {
  std::string tmp_file = "./new_syncdb_file.db";

  {
    pilorama::syncdb::SyncDb db(tmp_file);
    EXPECT_TRUE(db.IsNewlyCreated());
  }

  const auto guard = fs::blocking::TempFile::Adopt(tmp_file);
  {
    pilorama::syncdb::SyncDb db(tmp_file);
    EXPECT_FALSE(db.IsNewlyCreated());
  }
}

UTEST(SyncDB, IsFileWasMet) {
  auto tmp_file = fs::blocking::TempFile::Create();

  pilorama::syncdb::SyncDb db(tmp_file.GetPath());
  using utils::FileId;

  EXPECT_TRUE(!db.GetBytesProcessed(FileId{1, 1}));
  EXPECT_TRUE(!db.GetBytesProcessed(FileId{1, 2}));
  EXPECT_TRUE(!db.GetBytesProcessed(FileId{2, 1}));

  db.AddProcessedBytes(FileId{1, 2}, 200);

  EXPECT_TRUE(!db.GetBytesProcessed(FileId{1, 1}));
  EXPECT_TRUE(db.GetBytesProcessed(FileId{1, 2}));
  EXPECT_TRUE(!db.GetBytesProcessed(FileId{2, 1}));

  db.AddProcessedBytes(FileId{1, 1}, 100);
  db.AddProcessedBytes(FileId{1, 2}, 200);
  db.AddProcessedBytes(FileId{2, 1}, 300);

  EXPECT_TRUE(db.GetBytesProcessed(FileId{1, 1}));
  EXPECT_TRUE(db.GetBytesProcessed(FileId{1, 2}));
  EXPECT_TRUE(db.GetBytesProcessed(FileId{2, 1}));
}

UTEST(SyncDB, Erase) {
  auto tmp_file = fs::blocking::TempFile::Create();

  pilorama::syncdb::SyncDb db(tmp_file.GetPath());
  using utils::FileId;

  db.AddProcessedBytes(FileId{1, 2}, 200);

  db.Erase(FileId{1, 2});
  EXPECT_TRUE(!db.GetBytesProcessed(FileId{1, 1}));
  EXPECT_TRUE(!db.GetBytesProcessed(FileId{1, 2}));
  EXPECT_TRUE(!db.GetBytesProcessed(FileId{2, 1}));

  db.AddProcessedBytes(FileId{1, 1}, 100);
  db.AddProcessedBytes(FileId{1, 2}, 200);
  db.AddProcessedBytes(FileId{2, 1}, 300);
  db.Erase(FileId{2, 1});

  EXPECT_TRUE(db.GetBytesProcessed(FileId{1, 1}));
  EXPECT_TRUE(db.GetBytesProcessed(FileId{1, 2}));
  EXPECT_TRUE(!db.GetBytesProcessed(FileId{2, 1}));

  db.Erase(FileId{1, 1});
  db.Erase(FileId{1, 2});

  EXPECT_TRUE(!db.GetBytesProcessed(FileId{1, 1}));
  EXPECT_TRUE(!db.GetBytesProcessed(FileId{1, 2}));
  EXPECT_TRUE(!db.GetBytesProcessed(FileId{2, 1}));
}

UTEST(SyncDB, NoWrite) {
  auto tmp_file = fs::blocking::TempFile::Create();

  pilorama::syncdb::SyncDb db(tmp_file.GetPath());
  using utils::FileId;
  db.AddProcessedBytes(FileId{1, 1}, 100);
  db.AddProcessedBytes(FileId{1, 2}, 200);
  db.AddProcessedBytes(FileId{2, 1}, 300);

  EXPECT_EQ(db.GetBytesProcessed(FileId{1, 1}).value_or(0), 100u);
  EXPECT_EQ(db.GetBytesProcessed(FileId{1, 2}).value_or(0), 200u);
  EXPECT_EQ(db.GetBytesProcessed(FileId{2, 1}).value_or(0), 300u);
}

UTEST(SyncDB, Reset) {
  auto tmp_file = fs::blocking::TempFile::Create();

  pilorama::syncdb::SyncDb db(tmp_file.GetPath());
  using utils::FileId;
  db.AddProcessedBytes(FileId{1, 1}, 100);
  EXPECT_EQ(db.GetBytesProcessed(FileId{1, 1}).value_or(0), 100u);
  db.Reset(FileId{1, 1});
  ASSERT_TRUE(db.GetBytesProcessed(FileId{1, 1}));
  EXPECT_EQ(*db.GetBytesProcessed(FileId{1, 1}), 0);
}

UTEST(SyncDB, WithFileWrite) {
  auto tmp_file = fs::blocking::TempFile::Create();

  using utils::FileId;

  {
    pilorama::syncdb::SyncDb db(tmp_file.GetPath());
    db.AddProcessedBytes(FileId{1, 1}, 1000100);
    db.AddProcessedBytes(FileId{1, 2}, 1000200);
    db.AddProcessedBytes(FileId{2, 1}, 1000300);
  }

  pilorama::syncdb::SyncDb db(tmp_file.GetPath());
  EXPECT_EQ(db.GetBytesProcessed(FileId{1, 1}).value_or(0), 1000100u);
  EXPECT_EQ(db.GetBytesProcessed(FileId{1, 2}).value_or(0), 1000200u);
  EXPECT_EQ(db.GetBytesProcessed(FileId{2, 1}).value_or(0), 1000300u);
}

UTEST(SyncDB, CorruptedFileDetection) {
  auto tmp_file = fs::blocking::TempFile::Create();
  { pilorama::syncdb::SyncDb db(tmp_file.GetPath()); }
  { std::ofstream(tmp_file.GetPath().c_str()) << "1 1 1 z"; }

  EXPECT_ANY_THROW(pilorama::syncdb::SyncDb(tmp_file.GetPath()));
}

UTEST(SyncDB, SyncCalls) {
  using utils::FileId;

  auto tmp_file = fs::blocking::TempFile::Create();
  pilorama::syncdb::SyncDb db(tmp_file.GetPath());
  db.AddProcessedBytes(FileId{1, 1}, 100);
  db.AddProcessedBytes(FileId{1, 2}, 200);
  db.AddProcessedBytes(FileId{2, 1}, 300);

  db.Sync();
  EXPECT_TRUE(boost::filesystem::exists(tmp_file.GetPath()));

  boost::filesystem::remove(tmp_file.GetPath());
  db.Sync();
  EXPECT_FALSE(boost::filesystem::exists(tmp_file.GetPath()));

  db.AddProcessedBytes(FileId{2, 1}, 50);
  EXPECT_FALSE(boost::filesystem::exists(tmp_file.GetPath()));
  EXPECT_EQ(db.GetBytesProcessed(FileId{1, 2}).value_or(0), 200u);
  db.Sync();
  EXPECT_TRUE(boost::filesystem::exists(tmp_file.GetPath()));

  pilorama::syncdb::SyncDb db_second(tmp_file.GetPath());
  EXPECT_EQ(db.GetBytesProcessed(FileId{1, 1}).value_or(0), 100u);
  EXPECT_EQ(db.GetBytesProcessed(FileId{1, 2}).value_or(0), 200u);
  EXPECT_EQ(db_second.GetBytesProcessed(FileId{2, 1}).value_or(0), 350u);
}
