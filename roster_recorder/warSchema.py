

({
  attacker: {
    type: String,
    default: "NPC",
  },
  defender: {
    type: String,
  },
  warType: {
    type: String,
    enum: ["INVASION", "WAR"],
    default: "WAR",
  },
  location: {
    type: String,
    index: true,
  },
  startDate: {
    type: Date,
    default: Date.now(),
  },
  army: [
    new Schema({
      playerId: {
        type: ObjectId,
        ref: "Player",
        index: true,
      },
      group: {
        type: String,
        enum: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "STANDBY"],
        default: "STANDBY",
      },
    }),
  ],
  performance: [
    new Schema({
      playerId: {
        type: ObjectId,
        ref: "Player",
        index: true,
      },
      rank: {
        type: Number,
        default: 0,
      },
      score: {
        type: Number,
        default: 0,
      },
      kills: {
        type: Number,
        default: 0,
      },
      assists: {
        type: Number,
        default: 0,
      },
      deaths: {
        type: Number,
        default: 0,
      },
      healing: {
        type: Number,
        default: 0,
      },
      damage: {
        type: Number,
        default: 0,
      },
    }),
  ],
})