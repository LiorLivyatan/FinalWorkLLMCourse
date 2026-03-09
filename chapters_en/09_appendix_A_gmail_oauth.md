# Appendix A: Setting Up Gmail Account Access Permissions via Code

## A.1 Introduction

To run the project, you must first configure a Gmail account that you own or have permission to use for testing purposes. This guide details all the steps required to configure the Gmail API through Google Cloud Console.

## A.2 Step 1: Project Initialization

### A.2.1 Creating a New Project

1. Go to Google Cloud Console at console.cloud.google.com.
2. Click on the project menu in the top bar and select **New Project**.
3. Enter a project name in the format: `api-XXX-q21gb` where XXX is your unique description.
4. Click **Create**.

> **Important Note**
>
> The project name is used by Google to identify your billing and API quotas, but is not visible to end users.

### A.2.2 Enabling Gmail API

1. Select the project you created: `api-XXX-q21gb`.
2. In the search bar type: `Gmail API`.
3. Navigate to **APIs & Services → Library**.
4. Search for Gmail API and click **Enable**.
5. Click **Create credentials**.

## A.3 Step 2: Configuring the OAuth Consent Screen

### A.3.1 Branding Screen

Navigate to **APIs & Services → Google Auth Platform** and configure according to Table 89.

**Table 89: Branding Screen Settings**

| Field | Value and Explanation |
|---|---|
| App name | `gtai-XXX-final-project` — This name appears to the user on the login screen |
| User support email | Your Gmail address — for user permission inquiries |
| Developer contact | Your email address — for receiving security updates from Google |

Click **Save and Continue**.

### A.3.2 Configuring Access Permissions (Scopes)

1. Click **Add or Remove Scopes**.
2. Search for and select the following permissions:
   - `https://www.googleapis.com/auth/gmail.labels`
   - `https://www.googleapis.com/auth/gmail.readonly`
3. Click **Update**.
4. Click **Save and Continue**.

> **Why these permissions?**
>
> These permissions allow the application to read your labels (labels) and create new ones as needed. If this is a dedicated project email address, you may consider selecting all options.

## A.4 Step 3: Creating Desktop Credentials

### A.4.1 Creating an OAuth Client

Navigate to the **Clients** (or **Credentials**) tab in the sidebar:

1. Click **Create Client**.
2. Select **Desktop app** as the application type.
3. Enter a name: `desktop-gtai-XXX-2526b` — this name is for internal use only.
4. Click **Create**.

### A.4.2 Downloading and Saving the Credentials File

1. Click **Download** to download the JSON file.
2. Save the file in a dedicated folder.
3. Rename the file to: `gtai-XXX-2526b-gmail-client_secret.json`.

> **Security Warning**
>
> Make sure to add the file to the exclusion list in `.gitignore` to prevent accidentally uploading it to GitHub!

## A.5 Step 4: Adding Test Users

Since the application is in "Testing" mode, Google will block any user not on the test users list.

### A.5.1 Adding Authorized Users

1. Navigate to: **OAuth consent screen → Audience → Test users**.
2. Click **Add users**.
3. Enter the Gmail address that will connect through the API for reading and sending messages.
4. Save the changes.

> **Completion**
>
> After completing all steps, your Gmail API account is ready for use in the project! For a detailed analysis of API limitations, sending quotas, and spam risks worth knowing before starting development, see Appendix E.

## A.6 Step Summary

Table 90 summarizes all the steps for configuring Gmail API.

**Table 90: Gmail API Configuration Checklist**

| Step | Action |
|---|---|
| 1 | Create a new project in Google Cloud Console |
| 2 | Enable Gmail API |
| 3 | Configure OAuth consent screen (branding and permissions) |
| 4 | Create Desktop Client credentials |
| 5 | Download and save JSON file (with .gitignore protection) |
| 6 | Add authorized test users |

---

*© Dr. Segal Yoram - All rights reserved*
