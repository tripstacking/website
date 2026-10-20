import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const picomatch = require("picomatch");

export default picomatch;
