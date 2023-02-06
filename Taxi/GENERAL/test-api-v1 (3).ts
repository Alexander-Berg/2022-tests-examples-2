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
export type TestSearchFunction = "by_claim_id" | "by_external_order_id" | "by_payment_id" | "by_performer_phone" | "by_phone" | "by_status" | "by_corp_client_id" | "by_none" | "by_phone_and_corp_client_id" | "by_state_and_corp_client_id" | "by_status_and_corp_client_id" | "by_due_and_corp_client_id" | "by_performer_phone_and_status" | "by_phone_and_status" | "by_phone_and_status_and_corp_client_id" | "by_phone_and_state_and_corp_client_id";
export type TestSearchFilterInfo = {
    filter: {
        type: string;
        value?: string;
    };
    claim: string;
    result: "filtered" | "passed" | "skipped";
};
