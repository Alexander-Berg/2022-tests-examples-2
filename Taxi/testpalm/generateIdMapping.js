const axios = require("axios").default;
const fs = require("fs");
const { testpalm, authHeaders } = require("../../../../etc/config/abuConfig").config;

const generateMap = () => {
  if (!process.env.TESTRUN) {
    throw new Error("env.TESTRUN is required");
  }

  axios
    .get(
      `${testpalm.url}/testrun/${testpalm.projectName}/${process.env.TESTRUN}`,
      authHeaders
    )
    .then((res) => {
      const cases = res.data.testGroups[0].testCases;
      const idMapping = cases.reduce(function (obj, curr) {
        const key = curr.testCase.id;
        const value = curr.uuid;
        obj[key] = value;
        return obj;
      }, {});
      fs.writeFileSync("idMapping.json", JSON.stringify(idMapping));
    })
    .catch((err) => console.log(err));
};

module.exports = generateMap;
