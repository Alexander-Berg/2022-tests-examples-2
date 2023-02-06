declare namespace WebdriverIO {
  interface Browser {
    openPage: import('../commands/openPage').OpenPage
    addStyles: import('../commands/addStyles').AddStyles
    waitForElementAndClick: import('../commands/waitForElementAndClick').WaitForElementAndClick
    waitForElementExists: import('../commands/waitForElementExists').WaitForElementExists
    waitForElementText: import('../commands/waitForElementText').WaitElementForText
    scrollIntoView: import('../commands/scrollIntoView').ScrollIntoView
    scrollToElementEdge: import('../commands/scrollToElementEdge').ScrollToElementEdge
    assertImage: import('../commands/assertImage').AssertImage
    scrollByElement: import('../commands/scrollByElement').ScrollByElement
    scrollToElement: import('../commands/scrollToElement').ScrollToElement
    waitForElementScrollReleased: import('../commands/waitForElementScrollReleased').WaitForElementScrollReleased
  }
}
