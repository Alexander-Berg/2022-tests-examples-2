import React from "react";
import { render, screen } from "@testing-library/react";

import { Link, Route, Router, Routes } from ".";

describe("router", () => {
  it("should correctly resolve relative links", () => {
    render(
      <Router>
        <Routes>
          <Route element={<Link to="nested?search=1#hash">link</Link>}>
            <Route path="nested" />
          </Route>
        </Routes>
      </Router>
    );

    const link = screen.getByText("link");
    link.click();
    expect(window.location.href).toBe(
      `${window.location.origin}/nested?search=1#hash`
    );
    expect(link).toHaveAttribute("href", "/nested?search=1#hash");
  });
});
