import React from "react";
import Pagination from "rc-pagination";
import { mount } from "enzyme";

import { I18nextProvider } from "@yandex-fleet/i18n";
import i18nMock from "@yandex-fleet/i18n/src/i18nMock";

import Table from "./Table";

describe("Table", () => {
  it("work as expected", () => {
    type Item = { foo: string };

    const columns = [
      {
        Header: "Foo",
        accessor: (item: Item) => item.foo,
      },
    ];

    const data = [{ foo: "foo" }, { foo: "foo2" }, { foo: "bar" }];

    const wrapper = mount(
      <I18nextProvider i18n={i18nMock}>
        <Table columns={columns} data={data} pageSize={2} />
      </I18nextProvider>
    );

    expect(wrapper.exists()).toBe(true);
    expect(wrapper.find(Table).exists()).toBe(true);

    wrapper.setProps({
      children: (
        <Table columns={columns} data={data} pageSize={2} hasPagination />
      ),
    });

    const pagination = wrapper.find(Pagination);

    expect(pagination).toHaveLength(1);

    const nextButton = pagination.find(".rc-pagination-next");
    expect(wrapper.find("td")).toHaveLength(2);

    nextButton.simulate("click");

    expect(wrapper.find("td")).toHaveLength(1);
  });
});
