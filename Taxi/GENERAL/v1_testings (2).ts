import { TripDetailsExtended, RuleTest } from "../../../libraries/pricing-extended/docs/definitions/rules";
import { CompositePrice } from "../../../libraries/pricing-components/definitions/composite_price";
import { VisitedLinesInfo } from "../definitions";
export type Test = {
    source_code: string;
    backend_variables: {
        [x: string]: any;
    };
    trip_details: TripDetailsExtended;
    initial_price: CompositePrice;
    extra_returns?: string[];
    price_calc_version?: string;
};
export type RuleTestSummary = {
    name: string;
    test_result?: boolean;
    visited_lines?: VisitedLinesInfo;
};
export type RuleTestWithResult = RuleTest & {
    last_result?: boolean;
};
export type RuleWithTest = {
    rule_id?: number;
    tests?: string[];
};
