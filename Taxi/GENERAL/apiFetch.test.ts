import fetchMock from "jest-fetch-mock";

import { apiFetch } from "./apiFetch";
import { HttpError } from "./errors";

fetchMock.enableMocks();

describe("apiFetch", () => {
  it("should handle response with handler", async () => {
    fetchMock.mockResponseOnce("success");
    const result = await apiFetch(new Request(""), {
      ok: async (r) => ({ ok: true, data: await r.text() }),
    });
    if (result.ok) {
      expect(result.data).toBe("success");
    }
  });

  it("should throw HttpError without handler", async () => {
    fetchMock.mockResponseOnce("error", { status: 500 });
    await expect(apiFetch(new Request(""), {})).rejects.toThrow(HttpError);
  });

  it("should throw TypeError for unhandled success", async () => {
    fetchMock.mockResponseOnce("success", { status: 200 });
    await expect(apiFetch(new Request(""), {})).rejects.toThrow(TypeError);
  });
});
