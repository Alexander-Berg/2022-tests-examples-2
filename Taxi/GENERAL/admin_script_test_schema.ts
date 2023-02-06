export type FilterTest = {
    input_values: FilterTestInput;
    output_values: FilterTestOutput;
};
export type CalculateTest = {
    input_values: CalculateTestInput;
    output_values: CalculateTestOutput;
};
export type PostprocessResultsTest = {
    input_values: PostprocessResultsTestInput;
    output_values: PostprocessResultsTestOutput;
};
export type FilterTestInput = {
    common_context?: {
        [x: string]: any;
    };
    order_context?: {
        [x: string]: any;
    };
    candidate_context?: {
        [x: string]: any;
    };
};
export type FilterTestOutput = {
    return_value?: boolean;
    trace?: {
        [x: string]: any;
    };
    exception_message?: string;
};
export type CalculateTestInput = {
    common_context?: {
        [x: string]: any;
    };
    order_context?: {
        [x: string]: any;
    };
    candidate_context?: {
        [x: string]: any;
    };
};
export type CalculateTestOutput = {
    return_value?: number;
    trace?: Trace;
    exception_message?: string;
};
export type PostprocessResultsTestInput = {
    common_context?: {
        [x: string]: any;
    };
    order_contexts?: {
        [x: string]: any;
    }[];
    candidates_contexts?: {
        [x: string]: any;
    }[][];
    scoring_results?: {
        [x: string]: any;
    };
};
export type PostprocessResultsTestOutput = {
    traces?: {
        [x: string]: any;
    };
    scoring_results?: {
        [x: string]: any;
    };
    exception_message?: string;
};
export type Trace = {
    [x: string]: any;
};
