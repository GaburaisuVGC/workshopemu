## Installation

To set up the Firebase Emulator project on Python, you will need to follow these steps:

1. Install Python and pip. You can download Python from the official website: [Python.org](https://www.python.org/downloads/). Pip is usually included with Python installation.

2. Install Node.js. You can download Node.js from the official website: [Nodejs.org](https://nodejs.org/en/download/). Node.js is required to install `firebase-tools` using npm.

3. Create a .env in your project root folder

Your .env must be like this:
   
    SERVICE_ACCOUNT=your_service_account_filename.json
    FIREBASE_AUTH_EMULATOR_HOST=localhost:9099
    FIRESTORE_EMULATOR_HOST=localhost:8080
    FIREBASE_STORAGE_EMULATOR_HOST=localhost:9199
    BUCKET_NAME=your-bucket-name.appspot.com
    PROJECT_ID=your-project-id

4. Open a terminal or command prompt and run the following command to install the required Python packages:

    ```shell
    pip install -r requirements.txt
    ```

    Also install npm dependencies with:

    ```shell
    cd functions
    npm install
    ```

5. Run the following command to install `firebase-tools` globally using npm:

    ```shell
    cd ../
    npm install -g firebase-tools
    ```

6. Log in to your Google Account with :

    ```shell
    firebase login
    ``` 

7. Initialize the Firebase Emulators by running the following command:

    ```shell
    firebase init emulators
    ```

8. Follow the instructions :
- Create a new project (then, choose the name of the project)
- Select Firestore, Pub/Sub, Storage, Functions and Authentication
- Select the default ports and download the emulators

You now have a firebase.json file in your project root folder. Remember to complete your .env file.

To launch the emulators : `firebase emulators:start`

## How to get your service account JSON file

1. Access the Firebase Console

Go to the [Firebase Console](https://console.firebase.google.com/).
Sign in to your Google account if you haven't already.

2. Access Project Settings

Once in your project's dashboard, click on the gear icon located next to your project name in the left-hand menu to open the Project Settings.

3. Access Service Accounts

In the Project Settings page, go to the Service Accounts tab.
This tab gives you access to Firebase service accounts, which are used for administrative operations with Firebase.

4. Generate a Private Key

Under the Firebase Admin SDK section, select the language you are using (in this case, Python).
Click the Generate New Private Key button.
Firebase will generate a JSON file and prompt you to download it automatically. Download and keep this file secure, as it contains sensitive information.
The file will typically be named something like `your-project-id-firebase-adminsdk-xxxxx.json`.

5. Use the Key in Your Project

Place this JSON file into your Python project.

## Launch the project

1. Run the emulator:

    ```shell
    firebase emulators:start
    ```

    Wait for the emulator to setup completely before doing anything else.

2. Run the python script:

    ```shell
    python main.py
    ```
3. Access to your Emulator Suite with `localhost:4000`