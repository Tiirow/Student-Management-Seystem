# 🎓 Student Management System

### A modern academic management platform built to simplify and centralize educational operations.

[![Django](https://img.shields.io/badge/Django-6.x-092E20?style=for-the-badge\&logo=django\&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge\&logo=python\&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge\&logo=sqlite\&logoColor=white)](https://www.sqlite.org/)
[![React Native](https://img.shields.io/badge/React%20Native-2026-61DAFB?style=for-the-badge\&logo=react\&logoColor=black)](https://reactnative.dev/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge\&logo=github\&logoColor=white)](https://github.com/Tiirow/Student-Management-Seystem)


## 📌 Overview

Student Management System is a **Django-based academic management platform** designed to bring essential educational operations into one centralized system.

It provides dedicated dashboards, role-based permissions, and organized modules for managing students, teachers, classes, subjects, enrollment, attendance, and grades.

### 🎯 Built for

* 🏫 Schools & educational institutions
* 👨‍💼 Administrators & managers
* 👨‍🏫 Teachers
* 👨‍🎓 Students



## ✨ Core Features

|       | Module             | What it provides                        |
| :---: | ------------------ | --------------------------------------- |
| 👨‍🎓 | **Students**       | Student profiles & academic information |
| 👨‍🏫 | **Teachers**       | Teacher accounts & assignments          |
|   🏫  | **Classes**        | Class creation & management             |
|   📚  | **Subjects**       | Subjects & class assignments            |
|   📝  | **Enrollment**     | Student-class enrollment                |
|   📅  | **Attendance**     | Attendance tracking                     |
|   📊  | **Grades**         | Academic grade management               |
|   🔐  | **Authentication** | Secure user authentication              |
|  🛡️  | **Permissions**    | Role-based access control               |
|   📈  | **Dashboards**     | Role-specific dashboards                |



## 👥 Role-Based Access

The system separates functionality according to user responsibilities.

| Role                   | Access                                          |
| ---------------------  | ----------------------------------------------- |    
| 🛡️ **Administrator**  | Complete system access            |
| 📋 **Manager**        | Operational management                          |
| 👨‍🏫 **Teacher**     | Assigned classes, subjects, attendance & grades |
| 👨‍🎓 **Student**     | Personal academic information                   |



## 🛠️ Technology Stack

### 🌐 Web Application


Backend        Django
Language       Python
Frontend       HTML5 • CSS3 • JavaScript,some react
Database       SQLite
Authentication Django Authentication
ORM            Django ORM


### 📱 Mobile Application


Framework      React Native
Platform       Android / Mobile
API            Django Backend


### 🔧 Development


Version Control    Git & GitHub
Environment        Virtual Environment
Database Migration Django Migrations




## 🏗️ System Architecture


                         ┌──────────────────────┐
                         │        USERS         │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Authentication &     │
                         │ Role-Based Access    │
                         └──────────┬───────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                ▼                   ▼                   ▼
        ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
        │ Management   │    │   Teacher    │    │   Student    │
        │ Dashboard    │    │  Dashboard   │    │  Dashboard   │
        └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
               │                   │                   │
               └───────────────────┼───────────────────┘
                                   ▼
                         ┌──────────────────────┐
                         │   Django Backend     │
                         └──────────┬───────────┘
                                    ▼
                         ┌──────────────────────┐
                         │   Database / API     │
                         └──────────────────────┘




## 🧩 Main Modules


Student Management System
│
├── 🔐 Authentication
├── 👥 User Management
├── 👨‍🎓 Student Management
├── 👨‍🏫 Teacher Management
├── 🏫 Class Management
├── 📚 Subject Management
├── 📝 Enrollment
├── 📅 Attendance
├── 📊 Grades
├── 📈 Dashboards
└── 🛡️ Role & Permissions



## 🎨 Design System

The interface follows a consistent modern dashboard design.

| Element       | Color     |
| ------------- | --------- |
| 🟤 Primary    | `#9A5243` |
| 🟠 Secondary  | `#C17865` |
| ⚫ Sidebar     | `#17191D` |
| 🌑 Background | `#121418` |

The design focuses on:

**Clean UI · Consistent Navigation · Responsive Layout · Clear Data Presentation · Role-Based Dashboards**



## ⚙️ Getting Started

### 1. Clone
bash
git clone https://github.com/Tiirow/Student-Management-Seystem.git
cd Student-Management-Seystem


### 2. Create Virtual Environment

bash
python -m venv env


### 3. Activate — Windows

bash
env\Scripts\activate


### 4. Install Dependencies

bash
pip install -r requirements.txt

### 5. Apply Migrations

bash
python manage.py migrate


### 6. Create Admin Account

bash
python manage.py createsuperuser


### 7. Run

bash
python manage.py runserver


Open:

http://127.0.0.1:8000/



## 🚀 Roadmap

* 📱 Mobile application improvements
* 📊 Advanced analytics
* 📄 PDF & Excel reports
* 🔔 Notification system
* 📧 Email integration
* 💰 Fee management
* 🗓️ Timetable management
* ☁️ Cloud deployment
* 🐘 PostgreSQL production support



## 👨‍💻 Developer

### Mohamed Adan Mohamed

**Computer Application / Information Technology**
Jamhuriya University of Science and Technology (JUST)
Mogadishu, Somalia

[![GitHub](https://img.shields.io/badge/GitHub-Tiirow-181717?style=for-the-badge\&logo=github\&logoColor=white)](https://github.com/Tiirow)

[![Repository](https://img.shields.io/badge/View%20Repository-9A5243?style=for-the-badge\&logo=github\&logoColor=white)](https://github.com/Tiirow/Student-Management-Seystem)



## ⭐ Support the Project

If you find this project useful, consider giving it a ⭐ on GitHub.


### 🎓 Student Management System

**Manage Students · Empower Teachers · Organize Academic Data**

Built with Django, Python & modern web technologies.
