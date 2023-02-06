const axios = require("axios").default;
const dict = require("../../../../idMapping.json");
const { testpalm, authHeaders } = require("../../../../etc/config/abuConfig").config;

/**
 *
 * @param {*} testcaseId
 * @param {*} status
 */
function setStatus(testcaseId, status) {
  if (!process.env.TESTRUN) {
    throw new Error("env.TESTRUN is required");
  }

  const url = `${testpalm.url}/testrun/${testpalm.projectName}/${process.env.TESTRUN}/${dict[testcaseId]}/resolve?status=${status}`;
  const body = {};
  axios.post(url, body, authHeaders)
    .catch(err => new Error(err));
}

module.exports = setStatus;
