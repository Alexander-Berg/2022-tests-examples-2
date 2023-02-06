import { World as CucumberWorld } from "@cucumber/cucumber";
import { BrowserContext, Page } from "playwright";
import { Appmetrica } from "./project/appmetrica/pages";
export interface OurWorld extends CucumberWorld {
  context: BrowserContext;
  page: Page;
  appmetrica: Appmetrica
}
