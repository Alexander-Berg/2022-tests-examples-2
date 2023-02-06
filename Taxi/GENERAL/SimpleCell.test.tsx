import React from "react";
import { mount } from "enzyme";

import { I18nextProvider } from "@yandex-fleet/i18n";
import i18nMock from "@yandex-fleet/i18n/src/i18nMock";

import { Table, SimpleCell } from "../..";

describe("SimpleCell", () => {
  it("renders without crashing", () => {
    const data = [
      {
        test: "test",
      },
    ];
    const columns = [
      {
        Header: "Test",
        accessor: "test",
        Cell: SimpleCell,
      },
    ];

    const wrapper = mount(
      <I18nextProvider i18n={i18nMock}>
        <Table columns={columns} data={data} />
      </I18nextProvider>
    );

    expect(wrapper.find(SimpleCell)).toHaveLength(1);
  });
});
