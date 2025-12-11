# Firebase Database Integration Setup

This document explains how Firebase is integrated into the backend project.

## Overview

The backend uses **Firebase Admin SDK** (Python) to connect to Firestore database. This is the recommended approach for server-side applications.

## Project Configuration

- **Project ID**: `tastescore-engine`
- **Database**: Firestore (NoSQL document database)

## Setup Instructions

### 1. Service Account File

The backend requires a Firebase service account JSON file for authentication. The file `tastescore-engine-b69b90174d7e.json` is already present in the backend directory.

### 2. Environment Variables

Create a `.env` file in the `backend` directory with the following:

```env
# Firebase Configuration
# Option 1: Path to service account JSON file (recommended)
FIREBASE_SERVICE_ACCOUNT_KEY=tastescore-engine-b69b90174d7e.json

# Option 2: Service account JSON as environment variable (alternative)
# FIREBASE_CREDENTIALS_JSON={"type":"service_account","project_id":"tastescore-engine",...}
```

### 3. Service Account Permissions

Ensure your service account has the following IAM roles:
- **Cloud Datastore User** (for Firestore access)
- **Firebase Admin SDK Administrator Service Agent** (recommended)

## How It Works

The `FirestoreDB` class in `service/database.py` automatically:

1. Looks for `FIREBASE_SERVICE_ACCOUNT_KEY` environment variable
2. Falls back to default path: `tastescore-engine-b69b90174d7e.json`
3. If not found, tries `FIREBASE_CREDENTIALS_JSON` environment variable
4. Finally attempts default Google Cloud credentials

## Database Collections

The following Firestore collections are used:

- `address_labels` - Address labels (sanctions, mixers, watchlists)
- `exposure_metrics` - Exposure metrics for addresses
- `protocol_registry` - Protocol registry with reputation scores

## Client-Side Configuration

For the frontend, use the Firebase client SDK with the configuration in `service/firebase_config.py`:

```javascript
import { initializeApp } from "firebase/app";

const firebaseConfig = {
  apiKey: "AIzaSyCl-NHRDTj3NFlRCS8J0YgBKYoS9aYYMCM",
  authDomain: "tastescore-engine.firebaseapp.com",
  projectId: "tastescore-engine",
  storageBucket: "tastescore-engine.firebasestorage.app",
  messagingSenderId: "778300795413",
  appId: "1:778300795413:web:9fdc27a81d03235861fc1c"
};

const app = initializeApp(firebaseConfig);
```

## Testing the Connection

The database connection is automatically initialized when `FirestoreDB` is instantiated. Check the logs for:

```
Firebase initialized with service account key: ...
Firestore connection established for project: tastescore-engine
```

## Troubleshooting

### Error: "Firebase credentials not found"

1. Ensure the service account file exists at the specified path
2. Check that the `FIREBASE_SERVICE_ACCOUNT_KEY` environment variable is set correctly
3. Verify the file has proper read permissions

### Error: "Permission denied"

1. Check that the service account has the required IAM roles
2. Verify the service account is enabled in Firebase Console
3. Ensure Firestore is enabled for your project

## Additional Resources

- [Firebase Admin SDK Documentation](https://firebase.google.com/docs/admin/setup)
- [Firestore Documentation](https://firebase.google.com/docs/firestore)

