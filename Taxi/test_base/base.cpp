#include "base.h"
#include "taxi/logistic-dispatcher/dispatcher/rt_background/yd_pvz_schedule_updater/process.h"
#include "taxi/logistic-dispatcher/dispatcher/rt_background/billing/finalization.h"
#include "taxi/logistic-dispatcher/dispatcher/rt_background/billing/payments_sender.h"
#include "taxi/logistic-dispatcher/dispatcher/rt_background/requests_control/external_status_watcher.h"
#include <taxi/logistic-dispatcher/dispatcher/rt_background/eta_watcher/process.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/p2p_allocation/process.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/clean_performed/process.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/propositions/process.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/propositions/notifier.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/requests_control/states_watcher.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/state_watcher/process.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/employer_factors_watcher/process.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/claims_watcher/process.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/stations_fetcher/process.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/regular_sql/offers_cleanup.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/hour_slot_watcher/process.h>
#include <taxi/logistic-dispatcher/common_server/abstract/common.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/operator_commands/process.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/events_watcher/watcher.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/events_watcher/executor.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/release_free_contractors/process.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/requests_control/compilation.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/supply_estimator_experiment/process.h>
#include <taxi/logistic-dispatcher/common_server/user_auth/database/manager.h>
#include <library/cpp/yconf/patcher/unstrict_config.h>
#include <taxi/logistic-dispatcher/library/tvm_services/cargo_orders/client.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/carriage_provider/constructor.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/station_registration/process.h>
#include <taxi/logistic-dispatcher/dispatcher/station/tags/pickup_volume.h>
#include <taxi/logistic-dispatcher/dispatcher/station/tags/operator_station_id.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/cancel_expired_requests/process.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/billing/payments_builder.h>
#include <taxi/logistic-dispatcher/library/tvm_services/grocery_checkins/client.h>
#include <taxi/logistic-dispatcher/library/tvm_services/grocery_supply/client.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/platform_planner/provider.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/platform_planner/constructor.h>
#include <taxi/logistic-dispatcher/dispatcher/station/tags/supply_wb_promise.h>
#include <taxi/logistic-dispatcher/dispatcher/station/tags/supply_wb_reservation.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/shipment_provider/supply_reservation.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/trace_notification/process.h>
#include <taxi/logistic-dispatcher/dispatcher/integration/tracing/internal/internal_tracing.h>
#include <taxi/logistic-dispatcher/common_server/api/history/config.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/yd_supply_intervals_watcher/process.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/yd_pvz_schedule_updater/process.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/auto_reschedule/process.h>
#include <taxi/logistic-dispatcher/dispatcher/station/tags/station_schedule.h>
#include <taxi/logistic-dispatcher/dispatcher/rt_background/yd_pull_edges/process.h>
#include <util/random/random.h>

namespace {
    class TRegularTestChecker: public IObjectInQueue {
    private:
        const TDispatchTestCase* Owner = nullptr;
    public:
        TRegularTestChecker(const TDispatchTestCase* owner)
            : Owner(owner)
        {

        }
        void Process(void* /*threadSpecificResource*/) override {
            while (AtomicGet(Owner->GetIsActive())) {
                Owner->RegularTestCheck();
                Sleep(TDuration::Seconds(1));
            }
        }
    };
}


void TDispatchTestCase::BuildDatabase(const TDatabasePtr db) {
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

    TVector<TString> scriptsDatabaseConstruction;
    {
        NStorage::ITransaction::TPtr transaction = db->CreateTransaction(false);
        TFsPath fsMigrationPath(migrationPath);
        TVector<TString> migrationFiles;
        fsMigrationPath.ListNames(migrationFiles);
        std::sort(migrationFiles.begin(), migrationFiles.end());
        for (auto&& i : migrationFiles) {
            TFileInput fi(fsMigrationPath / i);
            const TString script = fi.ReadAll();
            scriptsDatabaseConstruction.emplace_back(script);
            CHECK_WITH_LOG(transaction->Exec(script, nullptr)->IsSucceed());
        }

        {
            TFileOutput fo("construction.sql");
            fo << JoinSeq("\n", scriptsDatabaseConstruction) << Endl;
        }
        CHECK_WITH_LOG(transaction->Commit()) << transaction->GetStringReport() << Endl;
    }
    while (true) {
        NStorage::ITransaction::TPtr transaction = db->CreateTransaction(true);
        Sleep(TDuration::Seconds(1));
        if (transaction->Exec("SELECT * FROM server_settings")->IsSucceed()) {
            break;
        }
    }
}



namespace {
    TString BuildHandlerConfig(const TString& handlerType, const TString& additionalCgi = "") {
        TStringBuilder sb;
        sb << "AuthModuleName: fake" << Endl;
        sb << "ProcessorType: " << handlerType << Endl;
        if (additionalCgi) {
            sb << "OverrideCgiPart: " << additionalCgi << Endl;
        }
        return sb;
    }
}

void TDispatchTestCase::Initialize() {
    CHECK_WITH_LOG(!Initialized);
    THistoryConfig::DefaultNeedLock = true;
    Initialized = true;
    TTestConfigGenerator configGenerator;
    ui16 serverPort = 16000;
    ui16 emulatorServerPort = 16000;
    ui16 monitoringServerPort = 17000;
#ifdef _win_
    configGenerator.SetDaemonPort(8000);
#else
    configGenerator.SetDaemonPort(Singleton<TPortManager>()->GetPort());
    serverPort = Singleton<TPortManager>()->GetPort();
    emulatorServerPort = Singleton<TPortManager>()->GetPort();
    monitoringServerPort = Singleton<TPortManager>()->GetPort();
#endif
    configGenerator.SetTaxiConfigClientType(TaxiConfigClientType);
    configGenerator.SetRouterType(RouterType);
    configGenerator.SetTaxiExternalWaybillPlannerId(TaxiExternalWaybillPlannerId);
    configGenerator.SetS7WaybillPlannerId(S7WaybillPlannerId);
    configGenerator.SetS7OperatorType(S7OperatorType);

    configGenerator.SetTaxiExternalType(TaxiExternalType);
    configGenerator.SetLogLevel(LogLevel);
    if (GetEnv("PGPASSWORD_TEST")) {
        configGenerator.SetPPass(GetEnv("PGPASSWORD_TEST"));
    }
    configGenerator.SetHomeDir(GetEnv("HOME"));
    if (GetEnv("DBHOST_TEST")) {
        configGenerator.SetDBHost(GetEnv("DBHOST_TEST"));
    }
    if (GetEnv("DBNAME_TEST")) {
        configGenerator.SetDBName(GetEnv("DBNAME_TEST"));
    }
    if (GetEnv("DBUSER_TEST")) {
        configGenerator.SetDBUser(GetEnv("DBUSER_TEST"));
    }
    if (GetEnv("WorkDir")) {
        configGenerator.SetWorkDir(GetEnv("WorkDir"));
    }

            if (GetEnv("POSTGRES_RECIPE_HOST")) {
                configGenerator.SetDBHost(GetEnv("POSTGRES_RECIPE_HOST"));
                configGenerator.SetDBPort(FromString<ui64>(GetEnv("POSTGRES_RECIPE_PORT")));
                configGenerator.SetDBName(GetEnv("POSTGRES_RECIPE_DBNAME"));
                configGenerator.SetDBUser(GetEnv("POSTGRES_RECIPE_USER"));
            } else {
               // CHECK_WITH_LOG(FillSpecialDBFeatures(configGenerator));
               CHECK_WITH_LOG(TFsPath(GetEnv("PG_MIGRATIONS_DIR")).Exists()) << GetEnv("PG_MIGRATIONS_DIR") << Endl;
            }


    configGenerator.SetBasePort(serverPort);
    configGenerator.SetEmulatorPort(emulatorServerPort);
    configGenerator.SetMonitoringPort(monitoringServerPort);
    configGenerator.SetEmulatorUsage(NeedEmulation);
    configGenerator.SetCandidatesEmulatorUsage(CandidatesEmulation);

    Config = configGenerator.BuildConfig<TDispatcherServerConfig>(configGenerator.GetFullConfig());
    try {
        TUnstrictConfig::ToJson(Config->ToString());
    } catch (...) {
        {
            TFileOutput fo("incorrect_config.txt");
            fo << Config->ToString();
        }
        S_FAIL_LOG << CurrentExceptionMessage() << Endl;
    }
    Server.Reset(new TDispatcherGuard(*Config, emulatorServerPort));
    Client.Reset(new TSimpleClient(serverPort));
    SendGlobalMessage<TRefreshClientStateMessage>();
    BuildEnv();
}

TP2PStableRequestGenerator TDispatchTestCase::StandartReqGen(new TRndLTGenerator(TGeoCoord(37.5, 55.5), TGeoCoord(37.4, 55.5)), new TRndLTGenerator(TGeoCoord(37.4, 55.5), TGeoCoord(37.3, 55.5)), nullptr);
TP2PStableRequestGenerator TDispatchTestCase::ReturnReqGen(new TRndLTGenerator(TGeoCoord(37.5, 55.5), TGeoCoord(37.4, 55.5)), new TRndLTGenerator(TGeoCoord(37.4, 55.5), TGeoCoord(37.3, 55.5)), new TRndLTGenerator(TGeoCoord(37.6, 55.5), TGeoCoord(37.3, 55.5)));


void TDispatchTestCase::BuildEnv() {
    {
        TVector<NFrontend::TSetting> settings;
        settings.emplace_back("defaults.taxi-external.test-comments-usage", "true");
        settings.emplace_back("defaults.taxi-external.due-usage", "false");
        settings.emplace_back("defaults.S7.test-mode", "true");
        settings.emplace_back("propositions.with_fake_points", "false");
        settings.emplace_back("not_allowed_checkpoints", "");
        settings.emplace_back("handlers.api/platform/request/info.sharing_url.enabled", "true");
        settings.emplace_back("yd_supply_intervals_watcher.allowed_station_ids", "yd_station");
        settings.emplace_back("yd_supply_intervals_watcher.allowed_tags_types", "supply_promise_strizh,supply_promise_strizh_reservation");
        settings.emplace_back("operator_events.move_until_demand.effective_operators", "taxi-external,lavka,external_operator");
        settings.emplace_back("handlers.platform/requests/add", BuildHandlerConfig("platform/add_request"));
        settings.emplace_back("handlers.platform/requests/activate", BuildHandlerConfig("platform/transfer/activation/do"));
        settings.emplace_back("handlers.platform/requests/activation/info", BuildHandlerConfig("platform/transfer/activation/info"));
        settings.emplace_back("handlers.platform/requests/add_simple", BuildHandlerConfig("platform/add_simple_request"));
        settings.emplace_back("handlers.platform/instruction/get", BuildHandlerConfig("platform/get_instruction"));
        settings.emplace_back("handlers.platform/instruction/item/do", BuildHandlerConfig("platform/do_instruction_item"));
        settings.emplace_back("handlers.platform/requests/checks/deferred", BuildHandlerConfig("platform/check_deferred_delivering"));
//        settings.emplace_back("handlers.", BuildHandlerConfig("platform/update_request"));
//        settings.emplace_back("handlers.", BuildHandlerConfig("platform/cancel_request"));
        settings.emplace_back("handlers.platform/requests/get", BuildHandlerConfig("request-get", "get_events=true&with_history=true"));
        settings.emplace_back("handlers.platform/platform/b2b/upsert_station", BuildHandlerConfig("platform/upsert_station"));
        settings.emplace_back("handlers.platform/requests/get.admin_request", "true");
        settings.emplace_back("handlers.platform/requests/cancel", BuildHandlerConfig("platform/cancel_request"));
        settings.emplace_back("handlers.platform/places/set_position", BuildHandlerConfig("platform/place/set_position"));
        settings.emplace_back("handlers.platform/actions/accept", BuildHandlerConfig("platform/execute_action"));
        settings.emplace_back("handlers.platform/propositions/get", BuildHandlerConfig("platform/get_propositions"));
        settings.emplace_back("handlers.platform/propositions/accept", BuildHandlerConfig("platform/accept_proposition"));
        settings.emplace_back("handlers.platform/requests/modification/transfers/enable", BuildHandlerConfig("platform/enable_transfer"));
        settings.emplace_back("handlers.platform/compatibility/ds", BuildHandlerConfig("platform/compatibility/ds"));
        settings.emplace_back("handlers.platform/repack", BuildHandlerConfig("platform/repack"));
        settings.emplace_back("handlers.platform/prepare_for_start", BuildHandlerConfig("platform/prepare_for_start"));
        settings.emplace_back("handlers.platform/request/trace", BuildHandlerConfig("platform/trace_request"));
        settings.emplace_back("handlers.platform/stations/list", BuildHandlerConfig("platform/get_stations"));
        settings.emplace_back("handlers.platform/init_public_output_code", BuildHandlerConfig("platform/init_public_output_code"));
        settings.emplace_back("handlers.api/admin/station/tag/list", BuildHandlerConfig("platform/stations/tags/list"));
        settings.emplace_back("handlers.api/billing/account/register", BuildHandlerConfig("billing-register-accounts"));
        settings.emplace_back("handlers.api/platform/offers/create.show_verbose_errors", "true");
        settings.emplace_back("handlers.api/platform/offers/create.send_offers_in_error", "true");
        settings.emplace_back("handlers.api/admin/employer/create", BuildHandlerConfig("employer-create"));
        settings.emplace_back("handlers.api/admin/employer/update", BuildHandlerConfig("employer-update"));
        settings.emplace_back("handlers.api/admin/employer/upsert", BuildHandlerConfig("employer-upsert"));
        settings.emplace_back("handlers.external-api/load_requests_registry", BuildHandlerConfig("external-api/load_requests_registry"));

        CHECK_WITH_LOG((*Server)->GetSettings().SetValues(settings, "tester"));
    }

    NDrive::TEntitySession session = (*Server)->GetRequestsManager().BuildNativeSession(false);

    {
        const TMap<TString, const char*> tags = {
            {"contact", "contact"},
            {"capacity", "capacity"},
            {"supply_promise_S7_reservation", "supply_reservation_tag"},
            {"supply_promise_virtual_operator_reservation", "supply_reservation_tag"},
            {"pickup_volume_S7_reservation", "operator_shipment"},
            {"supply_promise_strizh_reservation", "supply_reservation_tag"},
            {"pickup_volume_self_pickup_reservation", "operator_shipment"},
            {"supply_promise_self_pickup_reservation", "supply_reservation_tag"},
            {"pickup_volume_strizh_reservation", "operator_shipment"},
            {"wb_supply_promise_taxi-external_reservation", "wb_supply_reservation"},
            {"wb_supply_promise_taxi-external-testing_reservation", "wb_supply_reservation"},
            {"station_operator_registration", "station_operator_registration"},
            {"incoming_notification", "incoming_notification"},
            {"station_attractor", "station_attractor"},
            {"geoarea_attractor", "geoarea_attractor"},
            {"return_station_info_tag", "return_station_info"}
        };
        TVector<TDBTagDescription> descriptions;
        descriptions.reserve(tags.size());
        for (const auto& i : tags) {
            const auto tagDescription = ITagDescription::TFactory::Construct(i.second);
            CHECK_WITH_LOG(!!tagDescription);
            TDBTagDescription dbTagDescription(tagDescription);
            dbTagDescription.SetName(i.first);
            descriptions.emplace_back(std::move(dbTagDescription));
        }

        {
            THolder<NLogistic::TStationOperatorRegistrationTag::TTagDescription> td(new NLogistic::TStationOperatorRegistrationTag::TTagDescription);
            td->SetOperatorId("S7");
            TDBTagDescription dbTd(td.Release());
            dbTd.SetName("station_operator_registration_S7");
            descriptions.emplace_back(dbTd);
        }

        {
            THolder<NLogistic::TStationOperatorRegistrationTag::TTagDescription> td(new NLogistic::TStationOperatorRegistrationTag::TTagDescription);
            td->SetOperatorId("strizh");
            TDBTagDescription dbTd(td.Release());
            dbTd.SetName("station_operator_registration_strizh");
            descriptions.emplace_back(dbTd);
        }

        {
            THolder<NLogistic::TStationOperatorRegistrationTag::TTagDescription> td(new NLogistic::TStationOperatorRegistrationTag::TTagDescription);
            td->SetOperatorId("taxi-external");
            TDBTagDescription dbTd(td.Release());
            dbTd.SetName("station_operator_registration_taxi-external");
            descriptions.emplace_back(dbTd);
        }

        {
            THolder<NLogistic::ISupplyPromiseTag::TTagDescription> td(new NLogistic::ISupplyPromiseTag::TTagDescription);
            td->SetOperatorId("S7");
            TDBTagDescription dbTd(td.Release());
            dbTd.SetName("supply_promise_S7");
            descriptions.emplace_back(dbTd);
        }

        {
            THolder<NLogistic::ISupplyPromiseTag::TTagDescription> td(new NLogistic::ISupplyPromiseTag::TTagDescription);
            td->SetOperatorId("virtual_operator");
            TDBTagDescription dbTd(td.Release());
            dbTd.SetName("supply_promise_virtual_operator");
            descriptions.emplace_back(dbTd);
        }

        {
            THolder<NLogistic::ISupplyPromiseTag::TTagDescription> td(new NLogistic::ISupplyPromiseTag::TTagDescription);
            td->SetOperatorId("self_pickup");
            TDBTagDescription dbTd(td.Release());
            dbTd.SetName("supply_promise_self_pickup");
            descriptions.emplace_back(dbTd);
        }

        {
            THolder<NLogistic::ISupplyPromiseTag::TTagDescription> td(new NLogistic::ISupplyPromiseTag::TTagDescription);
            td->SetOperatorId("strizh");
            TDBTagDescription dbTd(td.Release());
            dbTd.SetName("supply_promise_strizh");
            descriptions.emplace_back(dbTd);
        }

        {
            THolder<NLogistic::TWBSupplyPromiseTag::TTagDescription> td(new NLogistic::TWBSupplyPromiseTag::TTagDescription);
            td->SetOperatorId("taxi-external");
            TDBTagDescription dbTd(td.Release());
            dbTd.SetName("wb_supply_promise_taxi-external");
            descriptions.emplace_back(dbTd);
        }

        {
            THolder<NLogistic::TWBSupplyPromiseTag::TTagDescription> td(new NLogistic::TWBSupplyPromiseTag::TTagDescription);
            td->SetOperatorId("taxi-external");
            TDBTagDescription dbTd(td.Release());
            dbTd.SetName("wb_supply_promise_taxi-external-testing");
            descriptions.emplace_back(dbTd);
        }

        {
            THolder<NLogistic::TPickupVolumeTag::TTagDescription> td(new NLogistic::TPickupVolumeTag::TTagDescription);
            td->SetOperatorId("S7");
            TDBTagDescription dbTd(td.Release());
            dbTd.SetName("pickup_volume_S7");
            descriptions.emplace_back(dbTd);
        }

        {
            THolder<NLogistic::TPickupVolumeTag::TTagDescription> td(new NLogistic::TPickupVolumeTag::TTagDescription);
            td->SetOperatorId("self_pickup");
            TDBTagDescription dbTd(td.Release());
            dbTd.SetName("pickup_volume_self_pickup");
            descriptions.emplace_back(dbTd);
        }

        {
            THolder<NLogistic::TPickupVolumeTag::TTagDescription> td(new NLogistic::TPickupVolumeTag::TTagDescription);
            td->SetOperatorId("strizh");
            TDBTagDescription dbTd(td.Release());
            dbTd.SetName("pickup_volume_strizh");
            descriptions.emplace_back(dbTd);
        }

        {
            THolder<NLogistic::TStationScheduleTag::TTagDescription> td(new NLogistic::TStationScheduleTag::TTagDescription);
            TDBTagDescription dbTd(td.Release());
            dbTd.SetName("station_schedule_tag");
            descriptions.emplace_back(dbTd);
        }

        CHECK_WITH_LOG((*Server)->GetTagDescriptionsManager().UpsertTagDescriptions(descriptions, "tester", session));
    }

    {
        TVector<TString> userIds = { "beru-employer", "lavka", "beru-transfer", "strizh", "taxi-external", "multi-point", "tester", "nespresso", "some-employer", "cainiao", "self_pickup"};
        for (auto&& i : userIds) {
            TDBAuthUserLink user;
            user.SetSystemUserId(i).SetAuthUserId(i);
            CHECK_WITH_LOG((VerifyDynamicCast<const TDBAuthUsersManager*>(&(*Server)->GetAuthUsersManager()))->AddObjects({ user }, "tester", session));
        }
    }

    {
        NLogistic::TEmployer testEmployer;
        testEmployer.SetEmployerCode("beru-employer");
        testEmployer.SetEmployerType("default");
        CHECK_WITH_LOG((*Server)->GetEmployersManager().RemoveObject({ "beru-employer" }, "beru-employer", session));
        CHECK_WITH_LOG((*Server)->GetEmployersManager().AddObjects({ testEmployer }, "beru-employer", session));
    }

    {
        NLogistic::TEmployer testEmployer;
        testEmployer.SetEmployerCode("tester");
        testEmployer.SetEmployerType("default");
        CHECK_WITH_LOG((*Server)->GetEmployersManager().RemoveObject({ "tester" }, "tester", session));
        CHECK_WITH_LOG((*Server)->GetEmployersManager().AddObjects({ testEmployer }, "tester", session));
    }

    {
        NLogistic::TEmployer defaultEmployer;
        defaultEmployer.SetEmployerCode("default");
        defaultEmployer.SetEmployerType("default");
        CHECK_WITH_LOG((*Server)->GetEmployersManager().RemoveObject({ "default" }, "default", session));
        CHECK_WITH_LOG((*Server)->GetEmployersManager().AddObjects({ defaultEmployer }, "default", session));
    }

    {
        NLogistic::TEmployer vkusvillEmployer;
        vkusvillEmployer.SetEmployerCode("vkusvill");
        vkusvillEmployer.SetEmployerType("default");
        CHECK_WITH_LOG((*Server)->GetEmployersManager().RemoveObject({ "vkusvill" }, "vkusvill", session));
        CHECK_WITH_LOG((*Server)->GetEmployersManager().AddObjects({ vkusvillEmployer }, "vkusvill", session));
    }

    {
        NLogistic::TEmployer eatsEmployer;
        eatsEmployer.SetEmployerCode("eats");
        eatsEmployer.SetEmployerType("eats");
        CHECK_WITH_LOG((*Server)->GetEmployersManager().RemoveObject({ "eats" }, "eats", session));
        CHECK_WITH_LOG((*Server)->GetEmployersManager().AddObjects({ eatsEmployer }, "eats", session));
    }

    {
        NLogistic::TEmployer groceryEmployer;
        groceryEmployer.SetEmployerCode("grocery");
        groceryEmployer.SetEmployerType("grocery");
        CHECK_WITH_LOG((*Server)->GetEmployersManager().RemoveObject({ "grocery" }, "grocery", session));
        CHECK_WITH_LOG((*Server)->GetEmployersManager().AddObjects({ groceryEmployer }, "grocery", session));
    }

    {
        NLogistic::TEmployer foodRetailEmployer;
        foodRetailEmployer.SetEmployerCode("food_retail");
        foodRetailEmployer.SetEmployerType("food_retail");
        CHECK_WITH_LOG((*Server)->GetEmployersManager().RemoveObject({ "food_retail" }, "food_retail", session));
        CHECK_WITH_LOG((*Server)->GetEmployersManager().AddObjects({ foodRetailEmployer }, "food_retail", session));
    }

    {
        THolder<NLogistic::TStateWatcherProcess> processSettings(new NLogistic::TStateWatcherProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(StateWatcherRobotAction);
        process.SetName("state_watcher_robot");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }
    {
        THolder<NLogistic::THourSlotWatcherProcess> processSettings(new NLogistic::THourSlotWatcherProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));
        processSettings->SetNotifyThreshold(TDuration::Days(10));
        processSettings->SetNotifyAll(false);

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(false);
        process.SetName(NLogistic::THourSlotWatcherProcess::GetTypeName());

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }
    {
        THolder<NLogistic::TRequestsStatesController> processSettings(new NLogistic::TRequestsStatesController());
        processSettings->SetPeriod(TDuration::Seconds(1));

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName("requests_controller");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }
    {
        THolder<NLogistic::TExternalStatusesWatcher> processSettings(new NLogistic::TExternalStatusesWatcher());
        processSettings->SetPeriod(TDuration::Seconds(1));

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName("external_statuses_watcher");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }
    {
        THolder<NLogistic::TP2PAllocationProcess> processSettings(new NLogistic::TP2PAllocationProcess());
        processSettings->SetPeriod(P2PAssignRobotFrequency);
        processSettings->SetPlannerScript(P2PAssignRobotScript);
        processSettings->SetTariffAreasFilter(P2PAssignRobotZoneFilter);

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(P2PAssignRobotActive);
        process.SetName("p2p_allocation_robot");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }
    {
        THolder<NLogistic::TP2PAllocationProcess> processSettings(new NLogistic::TP2PAllocationProcess());
        processSettings->SetPeriod(P2PAssignRobotFrequency);
        processSettings->SetPlannerScript(NLogistic::TP2PAllocationProcess::CreateFallbackP2PScript());

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(false);
        process.SetName("p2p_allocation_simplest");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }
    {
        THolder<NLogistic::TRequestsCompilation> processSettings(new NLogistic::TRequestsCompilation);
        processSettings->SetPeriod(TDuration::Seconds(1));
        processSettings->SetDryRun(false);
        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName(NLogistic::TRequestsCompilation::GetTypeName());

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }
    {
        THolder<NLogistic::TSupplyReservationProcess> processSettings(new NLogistic::TSupplyReservationProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName(NLogistic::TSupplyReservationProcess::GetTypeName());

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }
    {
        THolder<NLogistic::TPlatformPlannerTasksConstructorProcess> processSettings(new NLogistic::TPlatformPlannerTasksConstructorProcess);
        processSettings->SetPeriod(TDuration::Seconds(1));
        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName(NLogistic::TPlatformPlannerTasksConstructorProcess::GetTypeName());

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }
    {
        THolder<NLogistic::TPlatformPlannerTasksProviderProcess> processSettings(new NLogistic::TPlatformPlannerTasksProviderProcess);
        processSettings->SetPeriod(TDuration::Seconds(1));
        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName(NLogistic::TPlatformPlannerTasksProviderProcess::GetTypeName());

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }
    {
        THolder<NLogistic::TReleaseFreeContractors> processSettings(new NLogistic::TReleaseFreeContractors());
        processSettings->SetPeriod(TDuration::Seconds(10));

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName(NLogistic::TReleaseFreeContractors::GetTypeName());

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }
    {
        THolder<NLogistic::TTagGeneratorsWatcherProcess> processSettings(new NLogistic::TTagGeneratorsWatcherProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName(NLogistic::TTagGeneratorsWatcherProcess::GetTypeName());

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }
    {
        THolder<NLogistic::TCarriageDataProviderProcess> processSettings(new NLogistic::TCarriageDataProviderProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName(NLogistic::TCarriageDataProviderProcess::GetTypeName());

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }
    {
        THolder<NLogistic::TCarriagesCleanerProcess> processSettings(new NLogistic::TCarriagesCleanerProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName(NLogistic::TCarriagesCleanerProcess::GetTypeName());

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }
    {
        THolder<NLogistic::TCarriageConstructorProcess> processSettings(new NLogistic::TCarriageConstructorProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName(NLogistic::TCarriageConstructorProcess::GetTypeName());

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }
    {
        THolder<NLogistic::TInactualRequestsCancel> processSettings(new NLogistic::TInactualRequestsCancel());
        processSettings->SetPeriod(TDuration::Seconds(1));
        processSettings->SetOperatorIds({ "lavka" });

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName(NLogistic::TInactualRequestsCancel::GetTypeName());

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }
    {
        THolder<NLogistic::TStationsRegistrationProcess> processSettings(new NLogistic::TStationsRegistrationProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName(NLogistic::TStationsRegistrationProcess::GetTypeName());

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }
    {
        THolder<NLogistic::TStationsFetcherProcess> processSettings(new NLogistic::TStationsFetcherProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName("stations_fetcher");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }

    {
        THolder<NLogistic::TCleanPerformedProcess> processSettings(new NLogistic::TCleanPerformedProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(CleanerRobotActive);
        process.SetName("cleaner_performed_robot");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }

    {
        THolder<NLogistic::TPropositionsJournalWatcher> processSettings(new NLogistic::TPropositionsJournalWatcher());
        processSettings->SetPeriod(TDuration::Seconds(1));

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(PropositionsRobotActive);
        process.SetName("propositions_journal");
        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }

    {
        THolder<NLogistic::TClaimsJournalWatcher> processSettings(new NLogistic::TClaimsJournalWatcher());
        processSettings->SetPeriod(TDuration::Seconds(1));

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(PropositionsRobotActive);
        process.SetName("segments_journal");
        (*Server)->GetSettings().SetValue("segments_journal.is_bulk_processing", "true", "env_initialization");
        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }

    {
        THolder<NLogistic::TPropositionsNotifier> processSettings(new NLogistic::TPropositionsNotifier());
        processSettings->SetPeriod(TDuration::Seconds(1));

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName("propositions_notifier");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }
    {
        THolder<NLogistic::TOperatorCommandsProcess> processSettings(new NLogistic::TOperatorCommandsProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));
        processSettings->SetThreadsCount(4);

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName(NLogistic::TOperatorCommandsProcess::GetTypeName());

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }
    {
        THolder<NLogistic::TOperatorEventsExecutorProcess> processSettings(new NLogistic::TOperatorEventsExecutorProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName(NLogistic::TOperatorEventsExecutorProcess::GetTypeName());

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }

    {
        THolder<NLogistic::TEventsWatcherProcess> processSettings(new NLogistic::TEventsWatcherProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));
        processSettings->SetOperatorId("strizh");

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName(NLogistic::TEventsWatcherProcess::GetTypeName() + "-strizh");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }

    {
        THolder<NLogistic::TEventsWatcherProcess> processSettings(new NLogistic::TEventsWatcherProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));
        processSettings->SetOperatorId("S7");

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName(NLogistic::TEventsWatcherProcess::GetTypeName() + "-S7");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }

    {
        THolder<NLogistic::TEventsWatcherProcess> processSettings(new NLogistic::TEventsWatcherProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));
        processSettings->SetOperatorId("self_pickup");

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName(NLogistic::TEventsWatcherProcess::GetTypeName() + "-self_pickup");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }

    {
        THolder<NLogistic::TEventsWatcherProcess> processSettings(new NLogistic::TEventsWatcherProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));
        processSettings->SetOperatorId("market1");

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName(NLogistic::TEventsWatcherProcess::GetTypeName() + "-market1");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }

    {
        THolder<NLogistic::TEventsWatcherProcess> processSettings(new NLogistic::TEventsWatcherProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));
        processSettings->SetOperatorId("taxi-external");

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName(NLogistic::TEventsWatcherProcess::GetTypeName() + "-taxi-external");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }

    {
        THolder<NLogistic::TEventsWatcherProcess> processSettings(new NLogistic::TEventsWatcherProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));
        processSettings->SetOperatorId("lavka");

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName(NLogistic::TEventsWatcherProcess::GetTypeName() + "-lavka");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }

    {
        THolder<NLogistic::TEventsWatcherProcess> processSettings(new NLogistic::TEventsWatcherProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));
        processSettings->SetOperatorId("multi-point");

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName(NLogistic::TEventsWatcherProcess::GetTypeName() + "-multi-point");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }

    {
        THolder<NLogistic::TEstimationWatcherProcess> processSettings(new NLogistic::TEstimationWatcherProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(EtaActualizerRobotActive);
        process.SetName("estimation_watcher");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }

    {
        THolder<NLogistic::TEmployerFactorsWatcherProcess> processSettings(new NLogistic::TEmployerFactorsWatcherProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(EmployerFactorsRobotActive);
        process.SetName("employer_factors_watcher");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }

    {
        THolder<NLogistic::TSupplyEstimatorExperimentProcess> processSettings(new NLogistic::TSupplyEstimatorExperimentProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(SupplyExperimentRobotActive);
        process.SetName("supply_estimation_experiment");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }

    {
        THolder<NLogistic::TPaymentsBuilderProcess> processSettings(new NLogistic::TPaymentsBuilderProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));
        processSettings->SetDBName("main-db");

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName("by_place_payments_builder");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }

    {
        THolder<NLogistic::TRequestsCompilationUpdater> processSettings(new NLogistic::TRequestsCompilationUpdater());
        processSettings->SetPeriod(TDuration::Seconds(1));
        processSettings->SetDBName("main-db");

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName("requests_compilation_updater");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }

    {
        THolder<NLogistic::TBillingFinalizationProcess> processSettings(new NLogistic::TBillingFinalizationProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));
        processSettings->SetDBName("main-db");

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName("billing_finalization");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }
    {
        THolder<NLogistic::TPaymentsSenderProcess> processSettings(new NLogistic::TPaymentsSenderProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName("payments_sender");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }

    {
        THolder<NLogistic::TYDSupplyIntervalsWatcherProcess> processSettings(new NLogistic::TYDSupplyIntervalsWatcherProcess());
        processSettings->SetPeriod(TDuration::Seconds(10));
        processSettings->SetYdOperatorId("strizh");
        processSettings->SetFakeSenderId(228);
        processSettings->SetThreadsCount(10);
        processSettings->SetExternalApi("strizh");
        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName("yd_supply_intervals_watcher");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }

    {
        THolder<NLogistic::TYDPvzScheduleUpdater> processSettings(new NLogistic::TYDPvzScheduleUpdater());
        processSettings->SetPeriod(TDuration::Seconds(1));
        processSettings->SetYdOperatorId("strizh");
        processSettings->SetExternalApi("strizh");
        processSettings->SetThreadsCount(10);
        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName("yd_pvz_schedule_watcher");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }

    {
        THolder<NLogistic::TTraceNotificationProcess> processSettings(new NLogistic::TTraceNotificationProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));

        THolder<NLogistic::TInternalTraceNotifier> TraceNotifier(new NLogistic::TInternalTraceNotifier());
        TraceNotifier->SetClientId("Internal");
        NLogistic::TTraceNotifierContainer container(TraceNotifier.Release());
        processSettings->SetTraceNotifier(container);

        processSettings->SetDryRun(true);
        processSettings->SetSTQThresholdShard(100000);

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName("trace_notification");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }

    {
        THolder<NLogistic::TAutoRescheduleProcess> processSettings(new NLogistic::TAutoRescheduleProcess());
        processSettings->SetPeriod(TDuration::Seconds(1));
        processSettings->SetDryRun(false);

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName("auto_reschedule");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }

    {
        THolder<NLogistic::TYDPullEdges> processSettings(new NLogistic::TYDPullEdges());
        processSettings->SetPeriod(TDuration::Seconds(10));
        processSettings->SetOperatorId("strizh");
        processSettings->SetTagName("supply_promise_strizh_reservation");

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName("yd_pull_edges");

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }

    {
        THolder<NLogistic::TOffersCleanupProcess> processSettings(new NLogistic::TOffersCleanupProcess());
        processSettings->SetPeriod(TDuration::Seconds(10));

        TRTBackgroundProcessContainer process(processSettings.Release());
        process.SetEnabled(true);
        process.SetName(NLogistic::TOffersCleanupProcess::GetTypeName());

        CHECK_WITH_LOG((*Server)->GetRTBackgroundManager()->GetStorage().ForceUpsertBackgroundSettings(process, "env_initialization"));
    }

    {
        auto serviceApi = (*Server)->GetExternalAPI("cargo_orders");
        CHECK_WITH_LOG(serviceApi);
        NUtil::THttpReply mockReply;
        {
            mockReply.SetCode(200);
            mockReply.SetIsCorrectReply(true);
            mockReply.SetIsConnected(true);
            mockReply.SetContent(CargoOrdersMockContent);
        }
        serviceApi->SetMockReply(NCargoOrders::TGetZoneSettingsRequest().SetUri("v1/order/search-limits"), mockReply);
    }

    {
        auto serviceApi = (*Server)->GetExternalAPI("grocery_supply");
        CHECK_WITH_LOG(serviceApi);
        NUtil::THttpReply mockReply;
        {
            mockReply.SetCode(200);
            mockReply.SetIsCorrectReply(true);
            mockReply.SetIsConnected(true);
            mockReply.SetContent(GrocerySupplyMockContent);
        }
        serviceApi->SetMockReply(NGrocerySupply::TMatchLogGroupsRequest().SetUri("internal/v1/match_log_groups").SetLogisticGroups({"pull-dispatch-lavka"}), mockReply);
    }

    CHECK_WITH_LOG(session.Commit()) << session.GetStringReport() << Endl;
    SendGlobalMessage<NFrontend::TCacheRefreshMessage>();
}
