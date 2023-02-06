#pragma once

#include "server.h"
#include "config.h"

#include <taxi/logistic-dispatcher/common_server/server/server.h>

#include <library/cpp/testing/unittest/registar.h>
#include <library/cpp/testing/unittest/tests_data.h>
#include <library/cpp/yconf/patcher/unstrict_config.h>
#include <library/cpp/mediator/messenger.h>
#include <taxi/logistic-dispatcher/library/storage/structured.h>
#include <taxi/logistic-dispatcher/common_server/tags/manager.h>


namespace NServerTest {

    class TTestWithDatabase: public NUnitTest::TBaseFixture, public IMessageProcessor {
        CS_ACCESS(TTestWithDatabase, TAtomic, IsActive, 0);
        TString DBScheme;
        TThreadPool RegularTestThreadPool;
    public:
        TTestWithDatabase() {
            RegisterGlobalMessageProcessor(this);
        }

        ~TTestWithDatabase() {
            AtomicSet(IsActive, 0);
            RegularTestThreadPool.Stop();
            UnregisterGlobalMessageProcessor(this);
        }

        TString Name() const override {
            return "TTestWithDatabase";
        }

        virtual bool Process(IMessage* message) override {
            const TMessageOnAfterDatabaseConstructed* messEvent = dynamic_cast<const TMessageOnAfterDatabaseConstructed*>(message);
            if (messEvent) {
                BuildDatabase(messEvent->GetDatabase("main-db"));
                return true;
            }
            return false;
        }

    private:
        class TRegularTestChecker: public IObjectInQueue {
        private:
            const TTestWithDatabase* Owner = nullptr;
        public:
            TRegularTestChecker(const TTestWithDatabase* owner)
                    : Owner(owner) {

            }
            virtual void Process(void* /*threadSpecificResource*/) override {
                while (AtomicGet(Owner->GetIsActive())) {
                    Owner->RegularTestCheck();
                    Sleep(TDuration::Seconds(1));
                }
            }
        };

        virtual void DoRegularTestCheck() const {}

        void BuildDatabase(const TDatabasePtr db) {
            AtomicSet(IsActive, 1);
            CHECK_WITH_LOG(!!db);
            RegularTestThreadPool.Start(1);
            RegularTestThreadPool.SafeAddAndOwn(MakeHolder<TRegularTestChecker>(this));

            const TString migrationPath = GetEnv("PG_MIGRATIONS_DIR");


            DBScheme = TString("test_") + ::ToString(Now().Seconds()) + "_" + ToLowerUTF8(Name_) + "_" + ::ToString(RandomNumber<ui64>());
            WARNING_LOG << "CURRENT_SCHEMA: " << DBScheme << Endl;
            {
                auto lock = db->Lock("clear_old", true, TDuration::Zero());
                if (!!lock) {
                    TRecordsSet records;
                    {
                        NStorage::ITransaction::TPtr transaction = db->CreateTransaction(false);
                        CHECK_WITH_LOG(transaction->Exec("select nspname from pg_catalog.pg_namespace; ", &records)->IsSucceed());
                    }
                    TVector<TString> schemasForRemove;
                    ui32 idx = 0;
                    for (auto&& i : records) {
                        if (i.Get("nspname").StartsWith("test_") || i.Get("nspname").StartsWith("test001_")) {
                            const TVector<TString> parts = StringSplitter(i.Get("nspname")).SplitBySet("_").SkipEmpty().ToList<TString>();
                            CHECK_WITH_LOG(parts.size() > 2);
                            ui64 secondsTs;
                            CHECK_WITH_LOG(TryFromString(parts[1], secondsTs));
                            if (Now() - TInstant::Seconds(secondsTs) > TDuration::Hours(3)) {
                                schemasForRemove.emplace_back(i.Get("nspname"));
                            }
                        }
                        if (schemasForRemove.size() >= 50 || ++idx == records.size()) {
                            NStorage::ITransaction::TPtr transaction = db->CreateTransaction(false);
                            WARNING_LOG << schemasForRemove.size() << " schemas removing..." << Endl;
                            TStringStream ss;
                            for (auto&& iRequestScheme : schemasForRemove) {
                                ss << "DROP SCHEMA \"" << iRequestScheme << "\" CASCADE;";
                            }

                            if (!transaction->Exec(ss.Str())->IsSucceed() || !transaction->Commit()) {
                                ERROR_LOG << transaction->GetStringReport() << Endl;
                            } else {
                                WARNING_LOG << schemasForRemove.size() << " schemas removed OK" << Endl;
                            }
                            schemasForRemove.clear();
                        }
                    }
                }
            }

            {
                NStorage::ITransaction::TPtr transaction = db->CreateTransaction(false);
                CHECK_WITH_LOG(transaction->Exec("CREATE SCHEMA " + DBScheme, nullptr)->IsSucceed());
                CHECK_WITH_LOG(transaction->Commit()) << transaction->GetStringReport() << Endl;
            }
            Singleton<TDatabaseNamespace>()->SetOverridenNamespace(DBScheme + ",public");
            db->ApplyMigrations(migrationPath, 1);
            while (true) {
                NStorage::ITransaction::TPtr transaction = db->CreateTransaction(true);
                Sleep(TDuration::Seconds(1));
                if (transaction->Exec("SELECT * FROM server_settings")->IsSucceed()) {
                    break;
                }
            }
        }

        virtual void RegularTestCheck() const final {
            INFO_LOG << LogColorBlue << "CURRENT_SCHEME: " << DBScheme << LogColorNo << Endl;
            DoRegularTestCheck();
        }
    };

    template<class TServerGuard>
    class TAbstractTestCase: public TTestWithDatabase {
    private:
        THolder<typename TServerGuard::TConfig> Config;
        THolder<TServerGuard> Server;
        THolder<TSimpleClient> Client;

        bool Initialized = false;

        NRTProc::TAbstractLock::TPtr TestLock;

    public:
        TAbstractTestCase() {
            THistoryConfig::DefaultPingPeriod = TDuration::Seconds(3);
        }

        ~TAbstractTestCase() {
        }

        virtual bool FillSpecialDBFeatures(TConfigGenerator& /*configGenerator*/) const {
            return false;
        }

        void Initialize(TConfigGenerator& configGenerator) {
            NStorage::ITransaction::NeedAssertOnTransactionFail = true;
            NStorage::AssertOnParsingNewObjects = true;
            if (GetEnv("POSTGRES_RECIPE_HOST")) {
                configGenerator.SetDBHost(GetEnv("POSTGRES_RECIPE_HOST"));
                configGenerator.SetDBPort(FromString<ui64>(GetEnv("POSTGRES_RECIPE_PORT")));
                configGenerator.SetDBName(GetEnv("POSTGRES_RECIPE_DBNAME"));
                configGenerator.SetDBUser(GetEnv("POSTGRES_RECIPE_USER"));
            } else {
                CHECK_WITH_LOG(FillSpecialDBFeatures(configGenerator));
                CHECK_WITH_LOG(TFsPath(GetEnv("PG_MIGRATIONS_DIR")).Exists()) << GetEnv("PG_MIGRATIONS_DIR") << Endl;
            }

            CHECK_WITH_LOG(!Initialized);
            THistoryConfig::DefaultNeedLock = true;
            Initialized = true;
            ui16 serverPort = 16000;
#ifdef _win_
            configGenerator.SetDaemonPort(8000);
#else
            configGenerator.SetDaemonPort(Singleton<TPortManager>()->GetPort());
            serverPort = Singleton<TPortManager>()->GetPort();
#endif
            configGenerator.SetHomeDir(GetEnv("HOME"));
            if (GetEnv("WorkDir")) {
                configGenerator.SetWorkDir(GetEnv("WorkDir"));
            }
            configGenerator.SetBasePort(serverPort);

            Config = configGenerator.BuildConfig<typename TServerGuard::TConfig>(configGenerator.GetFullConfig());
            try {
                TUnstrictConfig::ToJson(Config->ToString());
            } catch (...) {
                {
                    TFileOutput fo("incorrect_config.txt");
                    fo << Config->ToString();
                }
                S_FAIL_LOG << CurrentExceptionMessage() << Endl;
            }
            Server.Reset(new TServerGuard(*Config));
            Client.Reset(new TSimpleClient(serverPort));

            TVector<NFrontend::TSetting> settings;
            PrepareSettings(settings);
            CHECK_WITH_LOG((*Server)->GetSettings().SetValues(settings, "tester"));
            TVector<TRTBackgroundProcessContainer> rtbgContainers;
            PrepareBackgrounds(rtbgContainers);
            for (auto&& i : rtbgContainers) {
                CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(i, "env_initialization"));
            }

            DoInitialize();
        }

    private:
        virtual void DoInitialize() {}

    protected:
        void AddTagDescription(const TDBTagDescription& descr) {
            auto& server = *GetServerGuard();
            const TTagDescriptionsManager& tagDescriptionsManager = server.GetTagDescriptionsManager();
            NDrive::TEntitySession session = tagDescriptionsManager.BuildNativeSession(false);
            tagDescriptionsManager.UpsertTagDescriptions({ descr }, "test", session);
            UNIT_ASSERT(session.Commit());
            tagDescriptionsManager.RefreshCache(Now());
        }

        virtual void PrepareSettings(TVector<NFrontend::TSetting>& settings) {
            Y_UNUSED(settings);
        }

        virtual void PrepareBackgrounds(TVector<TRTBackgroundProcessContainer>& rtbgContainers) {
            Y_UNUSED(rtbgContainers);
        }

        TServerGuard& GetServerGuard() {
            return *Server;
        }

        TSimpleClient& GetServerClient() {
            return *Client;
        }

        TString BuildHandlerConfig(const TString& handlerType, const TString& additionalCgi = "") const {
            TStringBuilder sb;
            sb << "AuthModuleName: fake" << Endl;
            sb << "ProcessorType: " << handlerType << Endl;
            if (additionalCgi) {
                sb << "OverrideCgiPart: " << additionalCgi << Endl;
            }
            return sb;
        }
    };
}
