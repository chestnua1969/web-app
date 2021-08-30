const express = require("express");
const app = express();
const {spawn} = require("child_process");

const cors = require("cors");
app.use(cors());
app.options("*", cors());

const bodyParser = require("body-parser");
app.use(bodyParser.json());

app.post("/run-optimization", (req, res, next) => {

  const python = spawn("python", ["portfolio_optimization.py", req.body]);
  python.stdout.on("data", data => {
    console.log(data.toString());
  });

  python.on("close", code => {
    res.json({message: `optimization finished with code ${code}`})
  });
});

app.listen("8082", "0.0.0.0", () => {
  console.log("Server running at http://0.0.0.0:8082");
});
