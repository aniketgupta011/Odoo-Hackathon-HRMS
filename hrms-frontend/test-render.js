const jsdom = require("jsdom");
const { JSDOM } = jsdom;

const resourceLoader = new jsdom.ResourceLoader({
  strictSSL: false,
});

JSDOM.fromURL("http://localhost:4200/", {
  runScripts: "dangerously",
  resources: "usable",
  pretendToBeVisual: true
}).then(dom => {
  const window = dom.window;
  const originalConsoleError = window.console.error;
  window.console.error = function() {
    console.log("BROWSER ERROR:", ...arguments);
    originalConsoleError.apply(window.console, arguments);
  };
  
  setTimeout(() => {
    console.log("DOM BODY:", dom.window.document.body.innerHTML);
    process.exit(0);
  }, 3000);
}).catch(err => {
  console.log("JSDOM Error:", err);
});
