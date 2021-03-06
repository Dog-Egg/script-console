const { createProxyMiddleware } = require("http-proxy-middleware");

module.exports = function (app) {
  app.use(
    createProxyMiddleware(["/api/**", "/ws/**"], {
      target: "http://localhost:8310",
      ws: true,
    })
  );
};
