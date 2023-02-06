import { ClaimDenorm } from "../definitions/pg-denorm";
export type TestSearchResponse = {
    claims: ClaimDenorm[];
    diagnostics: TestSearchDiagnostics;
};
export type TestSearchDiagnostics = {
    retrieved_claims: string[];
    retriever_function: TestSearchFunction;
    filtration_info: TestSearchFilterInfo[];
};
export type TestSearchFunction = "ByClaimId" | "ByCorpClientId" | "ByExternalOrderId" | "ByPerformerPhone" | "ByPhone" | "ByPhoneAndCorpClientId" | "ByClaimCreatedTsAndCorpClientId" | "ByClaimStateAndCorpClientId";
export type TestSearchFilterInfo = {
    filter: {
        type: string;
        value?: string;
    };
    claim: string;
    result: "filtered" | "passed" | "skipped";
};
