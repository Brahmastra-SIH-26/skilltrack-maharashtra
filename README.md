# **MainMaharashtra — Skill & Employment Outcome Tracking Platform**

## **Team**

Developed as a solution for **Smart India Hackathon 2026** by **Brahmastra-SIH-26**.

- Sumit
- Shailendra
- Vedant
- Saurabh
- Neha
- Ruchi

## **SIH 2026 — Problem Statement 26135**

This project is developed as a solution for **Smart India Hackathon (SIH) 2026**, under **Problem Statement 26135**.

### **Problem Statement**

**Title:** Difficulties in tracking employment outcomes, skill gaps, and the impact of skilling initiatives

**Description:**

Training systems frequently capture enrolment, attendance, assessment, and certification, but reliable information on employment, self-employment, job retention, wage progression, and the real-world impact of skilling initiatives is often unavailable.

This creates difficulties in:

- Tracking whether trained candidates actually obtain employment.
- Monitoring employment and self-employment outcomes after training.
- Measuring job retention and career progression.
- Identifying skill gaps between trained candidates and industry requirements.
- Tracking wage progression and employment quality.
- Evaluating the effectiveness and impact of different skilling initiatives.
- Making data-driven decisions regarding future training programs and resource allocation.

The absence of a centralized system for tracking these outcomes makes it difficult for administrators and policymakers to accurately evaluate the success of skilling programs.

---

## **Our Solution**

**MainMaharashtra** is a centralized web-based platform designed to help administrators monitor and analyze the outcomes of skilling initiatives beyond training completion.

Instead of limiting the system to enrolment, attendance, assessment, and certification data, our platform focuses on the **post-training journey of candidates**.

The platform brings relevant information together to provide a unified view of:

- Training and certification outcomes
- Employment status
- Self-employment
- Job retention
- Wage progression
- Skill gaps
- Industry requirements
- Employment trends
- Training program performance
- Regional and sector-wise outcomes

### **Key Features**

**1. Employment Outcome Tracking**

Administrators can monitor how many trained candidates successfully transition into employment or self-employment.

**2. Skill Gap Analysis**

The system helps identify gaps between the skills candidates possess and the skills required by employers and industries.

**3. Employment Retention Monitoring**

Employment data can be tracked over time to understand whether candidates remain employed after completing their training.

**4. Wage Progression**

The platform can monitor changes in candidate wages to evaluate whether training contributes to improved earning potential.

**5. Training Program Performance**

Different training initiatives can be compared using employment and outcome-based indicators rather than simply measuring enrolment or certification numbers.

**6. Administrative Dashboard**

A centralized dashboard provides administrators with key statistics, trends, and analytical insights required for decision-making.

**7. Data-Driven Decision Making**

Collected information can be used to identify underperforming programs, high-demand skills, regional gaps, and areas requiring additional intervention.

---

## **Technology Stack**

### **Frontend**

- HTML
- CSS
- JavaScript
- Tailwind CSS
- Chart.js

### **Backend**

- Node.js
- Express.js

### **Database**

- PostgreSQL
- Supabase

### **Additional Technologies**

- Redis
- REST APIs
- Session-based authentication

---

## **Project Architecture**

```text
MainMaharashtra/
│
├── public/
│   ├── css/
│   ├── js/
│   └── assets/
│
├── controllers/
│
├── routes/
│
├── utils/
│
├── views/
│
├── .env
├── .gitignore
├── input.css
├── package.json
├── package-lock.json
├── server.js
└── README.md
```

### **Directory and File Description**

| File / Directory    | Purpose                                                                                                |
| ------------------- | ------------------------------------------------------------------------------------------------------ |
| `public/`           | Contains all static frontend resources served to the client.                                           |
| `public/css/`       | Contains compiled and other CSS files used by the frontend.                                            |
| `public/js/`        | Contains client-side JavaScript files responsible for frontend interactions and functionality.         |
| `public/assets/`    | Contains static assets such as images, icons, fonts, and other frontend resources.                     |
| `controllers/`      | Contains the application logic that processes requests and generates responses.                        |
| `routes/`           | Defines API and webpage routes and connects them to the appropriate controllers.                       |
| `utils/`            | Contains reusable backend utility functions and service helpers used throughout the application.       |
| `views/`            | Contains the server-rendered HTML/EJS views used to display application pages.                         |
| `.env`              | Stores environment-specific configuration and sensitive credentials such as database keys and secrets. |
| `.gitignore`        | Specifies files and directories that should not be tracked or committed to Git.                        |
| `input.css`         | Tailwind CSS source file containing the project's Tailwind directives and custom CSS.                  |
| `package.json`      | Defines the project metadata, dependencies, scripts, and Node.js configuration.                        |
| `package-lock.json` | Locks the exact versions of installed npm dependencies for reproducible installations.                 |
| `server.js`         | Main application entry point that initializes the Express server and application configuration.        |
| `README.md`         | Provides project documentation, setup instructions, architecture, and information about the solution.  |

### **Utils**

The `utils/` directory contains reusable JavaScript functions that handle common backend operations, including:

- **OAuth utilities** — Functions for OAuth authentication and related authentication operations.
- **Database utilities** — Database connection/client creation functions that can be imported and reused across controllers and routes.
- **Rate limiting utilities** — Rate limiter configurations and helper functions for controlling API request frequency.
- **File upload utilities** — Functions for handling, validating, and processing uploaded files.
- **Other helpers** — Common reusable backend functions that do not belong specifically to a route or controller.

The application follows a client-server architecture where the frontend communicates with the Node.js/Express backend through APIs. The backend handles authentication, business logic, database operations, and data processing.

---

## **How to Run the Project**

### **1. Clone the Repository**

Open a terminal and run:

```bash
git clone https://github.com/Brahmastra-SIH-26/MainMahashtra.git
```

Move into the project directory:

```bash
cd MainMahashtra
```

### **2. Install Dependencies**

Install all required Node.js dependencies:

```bash
npm install
```

### **3. Configure Environment Variables**

Create a `.env` file in the root directory of the project.

Add the required environment variables used by the application.

Example:

```env
PORT=3000

SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

DATABASE_URL=your_database_url

SESSION_SECRET=your_session_secret

REDIS_URL=your_redis_url
```

**Do not commit your `.env` file to GitHub.**

The actual environment variable names should match those used in the project's backend configuration.

### **4. Start the Application**

Run:

```bash
npm start
```

The server will start on the configured port.

Open the application in your browser at:

```text
http://localhost:3000
```

If a different port is configured in your environment variables or application configuration, use that port instead.

---

## **Environment Requirements**

Before running the project, make sure you have installed:

- Node.js
- npm
- PostgreSQL/Supabase access
- Redis, if required by the configured application features

You will also need valid credentials and configuration values for the services used by the application.

---

## **Security**

Sensitive configuration values such as database credentials, API keys, session secrets, and Redis credentials must be stored in environment variables.

The `.env` file is excluded from version control through `.gitignore`.

Never expose production credentials in source code or commit them to the repository.

---

## **Project Objective**

The primary objective of MainMaharashtra is to move from simply measuring **training activity** to measuring **real-world outcomes**.

The platform aims to help stakeholders answer questions such as:

- How many trained candidates actually got jobs?
- Which training programs produce better employment outcomes?
- Which skills are currently in demand?
- Where are the major skill gaps?
- How many candidates remain employed after training?
- Are candidates experiencing wage growth?
- Which sectors and regions require additional skilling interventions?

By providing a centralized view of these indicators, the system can support more effective evaluation and planning of skilling initiatives.

---

## **SIH 2026**

**Event:** Smart India Hackathon 2026

**Problem Statement ID:** 26135

**Problem Statement:** Difficulties in tracking employment outcomes, skill gaps, and the impact of skilling initiatives

**Project:** MainMaharashtra

**Purpose:** A centralized platform for tracking, analyzing, and evaluating post-training employment outcomes and skill gaps.

---
