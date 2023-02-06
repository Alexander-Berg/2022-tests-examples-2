declare namespace PricingDataPreparerApiV1TestingsYaml {
    export interface RuleTest {
        [name: string]: any;
        backend_variables: {
            [name: string]: any;
        };
        trip_details: TripDetails;
        initial_price: PricingDataPreparerDefinitionsYaml.CompositePrice;
        output_price?: PricingDataPreparerDefinitionsYaml.CompositePrice;
        output_meta?: PricingDataPreparerDefinitionsYaml.CompilerMetadata;
    }
    export interface RuleTestSummary {
        name: string;
        test_result?: boolean;
    }
    export interface RuleTestWithResult {
        [name: string]: any;
        backend_variables: {
            [name: string]: any;
        };
        trip_details: TripDetails;
        initial_price: PricingDataPreparerDefinitionsYaml.CompositePrice;
        output_price?: PricingDataPreparerDefinitionsYaml.CompositePrice;
        output_meta?: PricingDataPreparerDefinitionsYaml.CompilerMetadata;
        last_result?: boolean;
    }
    export interface RuleTestingDB {
        [name: string]: any;
        backend_variables: {
            [name: string]: any;
        };
        trip_details: TripDetails;
        initial_price: PricingDataPreparerDefinitionsYaml.CompositePrice;
        output_price?: PricingDataPreparerDefinitionsYaml.CompositePrice;
        output_meta?: PricingDataPreparerDefinitionsYaml.CompilerMetadata;
        last_result?: boolean;
        last_result_rule_id?: number; // int64
    }
    export interface RuleWithTest {
        rule_id?: number; // int64
        tests?: string[];
    }
    export interface Test {
        source_code: string;
        backend_variables: {
            [name: string]: any;
        };
        trip_details: TripDetails;
        initial_price: PricingDataPreparerDefinitionsYaml.CompositePrice;
    }
    export interface TripDetails {
        /**
         * Расстояние в метрах
         */
        total_distance: number;
        /**
         * Время в секундах
         */
        total_time: number;
        /**
         * Время в секундах
         */
        waiting_time: number;
        /**
         * Время в секундах
         */
        waiting_in_transit_time: number;
        /**
         * Время в секундах
         */
        waiting_in_destination_time: number;
    }
}
