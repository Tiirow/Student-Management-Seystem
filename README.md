# 🎓 Student Management System

> A modern web-based system for managing students, teachers, classes, subjects, enrollment, attendance, and academic grades.

[![Django](https://img.shields.io/badge/Django-6.x-092E20?style=flat-square\&logo=django\&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square\&logo=python\&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=flat-square\&logo=sqlite\&logoColor=white)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-Educational-9A5243?style=flat-square)](LICENSE)

---

## 📌 Overview

Student Management System is a Django-based academic management platform designed to centralize student and educational operations in one secure system.

It provides role-based dashboards and controlled access for administrators, managers, teachers, and students.

---

## ✨ Features

| Module            | Description                                      |
| ----------------- | ------------------------------------------------ |
| 👨‍🎓 Students    | Manage student profiles and academic information |
| 👨‍🏫 Teachers    | Manage teachers and their assignments            |
| 🏫 Classes        | Create and manage classes                        |
| 📚 Subjects       | Organize subjects and class assignments          |
| 📝 Enrollment     | Manage student-class enrollment                  |
| 📅 Attendance     | Track and manage student attendance              |
| 📊 Grades         | Record and manage academic grades                |
| 🔐 Authentication | Secure login and logout system                   |
| 🛡️ Permissions   | Role-based access control                        |
| 📈 Dashboards     | Dedicated dashboards for different users         |

---

## 👥 User Roles

| Role              | Access                                          |
| ----------------- | ----------------------------------------------- |
| 👑 Superuser      | Full system access                              |
| 🛡️ Administrator | Administrative management                       |
| 📋 Manager        | Operational management                          |
| 👨‍🏫 Teacher     | Assigned classes, subjects, attendance & grades |
| 👨‍🎓 Student     | Personal academic information                   |

---

## 🛠️ Tech Stack

```text
Backend       → Django
Language      → Python
Frontend      → HTML5 • CSS3 • JavaScript
Database      → SQLite
Authentication→ Django Auth
ORM           → Django ORM
Version       → Git & GitHub
```

---

## 🏗️ System Structure

```text
Student Management System
│
├── Authentication
├── User Management
├── Student Management
├── Teacher Management
├── Class Management
├── Subject Management
├── Enrollment
├── Attendance
├── Grades
└── Role & Permissions
```

---

## 🎨 Design

The system uses a clean dashboard interface with a consistent visual identity.

| Design Element | Value     |
| -------------- | --------- |
| Primary        | `#9A5243` |
| Secondary      | `#C17865` |
| Sidebar        | `#17191D` |
| Background     | `#121418` |

---

## ⚙️ Installation

```bash
git clone https://github.com/Tiirow/Student-Management-Seystem.git
cd Student-Management-Seystem
```

Create and activate a virtual environment:

```bash
python -m venv env
```

Windows:

```bash
env\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
python manage.py migrate
```

Create an administrator:

```bash
python manage.py createsuperuser
```

Start the server:

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

## 🔐 Access Control

The system uses Django authentication and role-based permissions to control access to management features.

Server-side authorization protects sensitive operations, while each role receives a dashboard and functionality appropriate to its responsibilities.



# 🎓 Student Management System

> A modern web-based system for managing students, teachers, classes, subjects, enrollment, attendance, and academic grades.

[![Django](https://img.shields.io/badge/Django-6.x-092E20?style=flat-square\&logo=django\&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square\&logo=python\&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=flat-square\&logo=sqlite\&logoColor=white)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-Educational-9A5243?style=flat-square)](LICENSE)

---

## 📌 Overview

Student Management System is a Django-based academic management platform designed to centralize student and educational operations in one secure system.

It provides role-based dashboards and controlled access for administrators, managers, teachers, and students.

---

## ✨ Features

| Module            | Description                                      |
| ----------------- | ------------------------------------------------ |
| 👨‍🎓 Students    | Manage student profiles and academic information |
| 👨‍🏫 Teachers    | Manage teachers and their assignments            |
| 🏫 Classes        | Create and manage classes                        |
| 📚 Subjects       | Organize subjects and class assignments          |
| 📝 Enrollment     | Manage student-class enrollment                  |
| 📅 Attendance     | Track and manage student attendance              |
| 📊 Grades         | Record and manage academic grades                |
| 🔐 Authentication | Secure login and logout system                   |
| 🛡️ Permissions   | Role-based access control                        |
| 📈 Dashboards     | Dedicated dashboards for different users         |

---

## 👥 User Roles

| Role              | Access                                          |
| ----------------- | ----------------------------------------------- |
| 👑 Superuser      | Full system access                              |
| 🛡️ Administrator | Administrative management                       |
| 📋 Manager        | Operational management                          |
| 👨‍🏫 Teacher     | Assigned classes, subjects, attendance & grades |
| 👨‍🎓 Student     | Personal academic information                   |

---

## 🛠️ Tech Stack

```text
Backend       → Django
Language      → Python
Frontend      → HTML5 • CSS3 • JavaScript
Database      → SQLite
Authentication→ Django Auth
ORM           → Django ORM
Version       → Git & GitHub
```

---

## 🏗️ System Structure

```text
Student Management System
│
├── Authentication
├── User Management
├── Student Management
├── Teacher Management
├── Class Management
├── Subject Management
├── Enrollment
├── Attendance
├── Grades
└── Role & Permissions
```

---

## 🎨 Design

The system uses a clean dashboard interface with a consistent visual identity.

| Design Element | Value     |
| -------------- | --------- |
| Primary        | `#9A5243` |
| Secondary      | `#C17865` |
| Sidebar        | `#17191D` |
| Background     | `#121418` |

---

## ⚙️ Installation

```bash
git clone https://github.com/Tiirow/Student-Management-Seystem.git
cd Student-Management-Seystem
```

Create and activate a virtual environment:

```bash
python -m venv env
```

Windows:

```bash
env\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
python manage.py migrate
```

Create an administrator:

```bash
python manage.py createsuperuser
```

Start the server:

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

## 🔐 Access Control

The system uses Django authentication and role-based permissions to control access to management features.

Server-side authorization protects sensitive operations, while each role receives a dashboard and functionality appropriate to its responsibilities.

---

## 📸 Screenshots

Add your system screenshots here:

```text
screenshots/
├── login.png
├── dashboard.png
├── students.png
├── teachers.png
├── classes.png
├── subjects.png
├── attendance.png
└── grades.png
```

---

## 🚀 Future Improvements

* 📱 Mobile application
* 📊 Advanced analytics
* 📄 PDF & Excel reports
* 🔔 Notifications
* 📧 Email integration
* 💰 Fee management
* 🗓️ Timetable management
* ☁️ Cloud deployment

---

## 👨‍💻 Developer

**Mohamed Adan Mohamed**

Computer Application / Information Technology
Jamhuriya University of Science and Technology (JUST)
Mogadishu, Somalia

🔗 [GitHub Repository](https://github.com/Tiirow/Student-Management-Seystem)

---

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐.

---

### 🎓 Student Management System

> Manage Students • Empower Teachers • Organize Academic Data


## 🚀 Future Improvements

* 📱 Mobile application
* 📊 Advanced analytics
* 📄 PDF & Excel reports
* 🔔 Notifications
* 📧 Email integration
* 💰 Fee management
* 🗓️ Timetable management
* ☁️ Cloud deployment

---

## 👨‍💻 Developer

**Mohamed Adan Mohamed**

Computer Application / Information Technology
Jamhuriya University of Science and Technology (JUST)
Mogadishu, Somalia

🔗 [GitHub Repository](https://github.com/Tiirow/Student-Management-Seystem)

---

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐.

---

### 🎓 Student Management System

> Manage Students • Empower Teachers • Organize Academic Data
