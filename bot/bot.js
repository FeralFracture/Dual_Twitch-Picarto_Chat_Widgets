const fs = require("fs");
const path = require("path");
const pmi = require("pmi.js");
const { io } = require("socket.io-client");

const configPath = path.join(__dirname, "..", "config", "data.json");
const config = JSON.parse(fs.readFileSync(configPath));

const opts = {
  identity: {
    username: config.picarto.username,
    password: config.picarto.oauth_tkn,
  },
};

const client = new pmi.client(opts);

client.on("message", onMessageHandler);
client.on("connected", onConnectedHandler);

client.connect();

const socket = io(`http://127.0.0.1:${config.flask.port}`);

function onMessageHandler(target, context, msg, self) {
  if (self) return;
  if (!msg.startsWith("!")) {
    const message = {
      type: "userMsg",
      user: context[0].n,
      text: msg,
      icon: `https://images.picarto.tv/${context[0].i}`,
      id: context[0].id,
      color: `#${context[0].k}`
    };
    console.log(JSON.stringify(message));
    return;
  }
  if (msg === "!test") {
    client.say(target, "[Bot]: Succesful test.");
  }
}

function onConnectedHandler(addr, port) {
  //console.log(`* Connected to ${addr}:${port}`);
}
