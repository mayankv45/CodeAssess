# CodeAssess — Coding Problem Designer & Test Case Generator

> A Flask-based web application for designing, managing, and organizing coding-assessment problems and their test cases.

**Live Demo:** https://code-assess-rose.vercel.app/

---

## 📌 Overview

CodeAssess is a coding-assessment content management tool designed to simplify the process of creating and maintaining programming problems.

Instead of manually maintaining coding questions and their test cases, CodeAssess provides a centralized workspace where problems can be created, edited, organized, tested, and exported.

The application supports structured problem creation, problem-bank search and filtering, test-case generation, custom test cases, reference solutions, and JSON export.

The application is built with **Flask and PostgreSQL**, with the production version deployed on **Vercel** and its database hosted on **Neon PostgreSQL**.

---

## ✨ Features

### 📊 Dashboard

The dashboard provides an overview of the problem bank, including:

- Total number of problems
- Total test cases
- Easy problems
- Medium problems
- Hard problems
- Recently updated problems

---

### 📝 Problem Management

Create and manage coding problems with structured information such as:

- Problem title
- Problem statement
- Input format
- Output format
- Constraints
- Examples
- Explanation
- Topic
- Difficulty
- Tags
- Time limit
- Memory limit
- C++ reference solution
- Python reference solution
- Time and space complexity

Supported problem operations:

- Create
- View
- Edit
- Delete

---

### 🔎 Problem Bank

The problem bank allows problems to be searched and filtered by:

- Title
- Tags
- Topic
- Difficulty

Supported topics include:

- Arrays
- Strings
- Searching
- Sorting
- Hashing
- Linked List
- Stack & Queue
- Trees
- Graphs
- Dynamic Programming

---

### 🧪 Test Case Management

Test cases can be:

- Added manually
- Generated automatically
- Saved individually
- Saved in bulk
- Deleted
- Viewed along with their associated problem

Each test case stores:

- Name
- Input
- Expected output
- Test type
- Creation timestamp

---

### ⚙️ Test Case Generator

CodeAssess includes an array-based test-case generator supporting:

- Random
- Minimum
- Maximum
- Sorted
- Reverse Sorted
- All Same
- Custom

The generator allows configuration of:

- Number of test cases
- Minimum array size
- Maximum array size
- Minimum value
- Maximum value

Generated test cases can be reviewed and saved in bulk.

---

### ✅ Expected Output Generation

For the included demonstration problem format, CodeAssess can automatically calculate the expected output.

The current implementation supports:

> **Maximum Element in an Array**

For example:

```text
Input:
5
3 8 2 10 6

Output:
10
