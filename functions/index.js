const path = require("path");
const dotenv = require("dotenv");

// Load environment variables from .env file
dotenv.config({ path: path.resolve(__dirname, "../.env") });

// Get the project ID from the environment variables
const projectId = process.env.PROJECT_ID;

const functions = require("firebase-functions");
const { onObjectFinalized } = require("firebase-functions/v2/storage");
const admin = require("firebase-admin");
const { PubSub } = require("@google-cloud/pubsub");

admin.initializeApp();

const pubsub = new PubSub({ projectId: projectId });

// Function triggered by the creation of a file in the Storage bucket
exports.sortFile = onObjectFinalized(async (event) => {
  const object = event.data;
  const filePath = object.name;

  // Check if the file has already been processed
  if (object.metadata && object.metadata.processed === "true") {
    return;
  }

  const contentType = object.contentType;

  const bucket = admin.storage().bucket(object.bucket);

  let destinationFolder = "";

  if (contentType.startsWith("image/")) {
    destinationFolder = "images/";
  } else if (contentType === "application/pdf") {
    destinationFolder = "pdfs/";
  } else {
    destinationFolder = "others/";
  }

  const fileName = filePath.split("/").pop();
  const destination = `${destinationFolder}${fileName}`;

  // Add metadata to the file
  const newMetadata = {
    metadata: {
      processed: "true",
    },
  };

  try {
    // Move the file to the new location
    await bucket.file(filePath).move(destination);

    // Update the file metadata
    await bucket.file(destination).setMetadata(newMetadata);

    console.log(`Fichier déplacé vers ${destination}.`);

    // Publish a message to the Pub/Sub topic
    const topicName = "file-processed";
    const data = JSON.stringify({
      message: "Fichier traité",
      fileName: destination,
    });

    const dataBuffer = Buffer.from(data);

    // Create the Pub/Sub topic if it doesn't exist
    const topic = pubsub.topic(topicName);
    const [topicExists] = await topic.exists();
    if (!topicExists) {
      await pubsub.createTopic(topicName);
    }

    const messageId = await topic.publishMessage({ data: dataBuffer });
  } catch (error) {
    console.error(
      "Erreur lors du déplacement du fichier ou de la mise à jour des métadonnées :",
      error
    );
  }
});

// Function triggered by the Pub/Sub message
exports.processEvent = functions.pubsub
  .topic("file-processed")
  .onPublish((message) => {
    const data = message.data
      ? Buffer.from(message.data, "base64").toString()
      : "{}";
    const jsonData = JSON.parse(data);

    console.log("Message reçu depuis Pub/Sub :", jsonData);
  });
