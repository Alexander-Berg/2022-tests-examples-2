import { TripDetails, CompositePrice, RuleTest } from "../../../libraries/pricing-extended/definitions";
export type Test = {
    source_code: string;
    backend_variables: {
        [x: string]: any;
    };
    trip_details: TripDetails;
    initial_price: CompositePrice;
    extra_returns?: string[];
};
export type RuleTestSummary = {
    name: string;
    test_result?: boolean;
};
export type RuleTestWithResult = RuleTest & {
    [x: string]: any;
} & {
    last_result?: boolean;
};
export type RuleWithTest = {
    rule_id?: number;
    tests?: string[];
};
