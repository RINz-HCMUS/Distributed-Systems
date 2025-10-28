# 🌐 Distributed Systems – CSC11112 (HCMUS 2025)

![GitHub last commit (branch)](https://img.shields.io/github/last-commit/RINz-HCMUS/Distributed-Systems/main?color=blue&style=flat-square)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)

---

## 📘 Course Overview

**Course ID:** CSC11112  
**Course Name:** Distributed Systems (*Hệ thống Phân tán*)  
**Credits:** 4 (45 theory – 30 practice – 90 self-study hours)  
**Prerequisite:** Operating Systems  
**Faculty:** Information Technology – VNUHCM University of Science  

This course provides students with **core foundations of distributed computing**, including:
- Concepts of distributed systems, synchronization, event ordering, and consistency  
- Inter-process communication, mutual exclusion algorithms, and fault recovery  
- Distributed file systems, consensus protocols, and parallel coordination  
- Practical experience in designing and developing small distributed applications  

---

## 🎯 Course Goals

At the end of this course, students will be able to:

| ID | Goal | Description |
|----|------|--------------|
| G1 | Collaboration | Work effectively in teams to design distributed system solutions |
| G2 | Terminology | Understand and use English technical terms in distributed systems |
| G3 | Conceptual | Explain and illustrate key distributed concepts: clocks, events, consistency |
| G4 | Problem Solving | Identify and classify distributed system problems |
| G5 | Design | Develop solutions for distributed coordination, recovery, and consistency |
| G6 | Implementation | Build small distributed applications using appropriate algorithms |

---

## 🧩 Course Outcomes (COs)

| ID | Description | Level |
|----|--------------|-------|
| G1.1 | Organize and manage group or individual work | I, T |
| G1.3 | Analyze and write project reports | I, T |
| G2.1 | Understand specialized English terms | I |
| G3.1 | Explain key concepts: clocks, consistency, recovery | I, T |
| G5.1 | Design and build distributed applications | I, T, U |
| G6.1 | Analyze problems and modularize solutions | I, T, U |

---

## 📚 Teaching Plan

### 🔹 Theory Topics

| Week | Topic | Learning Outcomes |
|-------|--------|-------------------|
| 1 | Introduction to Distributed Systems | G1.2, G2.1, G3.1 |
| 2 | Review of LAN/WAN, TCP/IP, Socket Programming | G4.1, G5.1 |
| 3 | Lamport Clock, Logical Clock, Event Ordering (BSS, SES) | G1.3, G5.1 |
| 4 | Process Synchronization: Lamport, Maekawa, Ricart-Agrawala, Suzuki-Kasami | G4.1, G6.1 |
| 5 | Distributed File Systems: GFS, Cluster FS | G5.1, G7.1 |
| 6 | Distributed Scheduling and Load Balancing | G6.1, G7.1 |
| 7 | Recovery & Commit Protocols (2PC, 3PC, Voting) | G4.1, G5.1 |
| 8 | Consensus: PBFT, Tendermint, Proof-of-Work | G5.1 |
| 9 | Distributed Shared Memory & Parallel Algorithms | G5.1 |
| 10 | Security in Distributed Systems | G5.2 |
| 11 | Review and Project Submission | G1–G7 |

### 🔹 Laboratory / Seminar Projects

| ID | Title | Description |
|-----|--------|--------------|
| P1 | Project 1 – gRPC Chat | Build a distributed chat system using gRPC |
| P2 | Project 2 – Distributed File System | Simulate DFS with replication & metadata management |
| P3 | Project 3 – Consensus & Raft | Implement leader election and log replication |

---

## 🧾 Assessment Scheme

| Component | Description | Weight |
|------------|--------------|--------|
| **Assignments (A1)** | Quizzes on key concepts (Introduction, BSS/SES, Synchronization, Recovery) | 10% |
| **Projects (A2)** | Practical implementation projects (Socket, Synchronization, Chat/Game) | 30% |
| **Exams (A3)** | Midterm + Final (open-book, problem-solving, coding) | 60% |
| **Total** |  | **100%** |

**Breakdown of Project (30%):**
- Socket Project – 5%  
- Synchronization (SES) – 10%  
- Application (Chat/Game) – 15%

---

## 🧠 Core Topics

- Distributed system architecture and models  
- Logical & vector clocks, causality, and event ordering  
- Inter-process communication (RPC, gRPC)  
- Distributed synchronization and mutual exclusion algorithms  
- Distributed file systems and fault recovery  
- Consensus and blockchain protocols (PBFT, Tendermint, PoW)  
- Load balancing and scheduling  
- Security and consistency models  

---

## 💻 Repository Structure

```
Distributed-Systems/
├── Lectures/
│   ├── Lecture01_Introduction.pdf
│   ├── Lecture02_RPC_and_gRPC.pdf
│   └── ...
└── Projects/
    ├── Project1_gRPC_Chat/
    │   ├── chat.proto
    │   ├── server.py
    │   ├── client.py
    │   ├── data_manager.py
    │   ├── README.md
    │   └── data/
    ├── Project2_.../
    └── Project3_.../
```

---

## 📚 References

- *Advanced Concepts in Operating Systems* – Mukesh Singhal, Niranjan Shivaratri, McGraw-Hill (1994)  
- *Distributed Operating Systems* – Andrew S. Tanenbaum, Prentice Hall (1995)  
- *Designing Data-Intensive Applications* – Martin Kleppmann (2017)  
- Google gRPC Documentation – [https://grpc.io/docs](https://grpc.io/docs)  
- Raft Consensus Visualization – [https://raft.github.io](https://raft.github.io)

---

## 🧑‍🏫 Instructors

| Name | Role |
|------|------|
| **Thầy Trần Trung Dũng** | Lecturer |
| **Cô Huỳnh Thụy Bảo Trân** | Lecturer |

---

## 👨‍🎓 Student Contributor

| Name | Student ID | Role |
|------|-------------|------|
| **Võ Hữu Tuấn** | **22127439** | Developer, Documentation, Implementation |

---

## 📄 License

This repository is released under the [MIT License](LICENSE).  
Use and modify for educational purposes only.

---

⭐ **If this repository helps you understand Distributed Systems, please star it on GitHub!**
