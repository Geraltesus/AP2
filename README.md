# Project 02 — Python_Bootcamp

**Summary:**  
In this project, you'll practice using object-oriented, procedural, and multiparadigm approaches in Python — and you'll also write code that follows the functional programming paradigm.

💡 Click here to share your feedback on this project. It's anonymous and helps us make the learning experience better. We recommend filling out the survey right after completing the project.

## Contents

  - [Chapter I](#chapter-i)
    - [Instructions](#instructions)
  - [Chapter II](#chapter-ii)
    - [General Information](#general-information)
  - [Chapter III](#chapter-iii)
    - [Task 1. Exam](#task-1-exam)
    - [Task 2. Image Downloader](#task-2-image-downloader)

## Chapter I

### Instructions

1. Throughout the course, you will often feel uncertain and have limited information, but that's all part of the experience. Remember, the repository and Google are always there for you. So are your peers and Rocket.Chat. Talk. Search. Use your common sense. Don't be afraid to make mistakes.
2. Be mindful of your sources. Cross-check. Think critically. Analyze. Compare.
3. Read the tasks carefully, and then read them again.
4. Pay close attention to the examples, too. They may include information that is not explicitly stated in the task itself.
5. You may encounter inconsistencies when something in the task or example contradicts what you thought you knew. Try to figure them out. If you can't, write it down as an open question and resolve it as you go. Don't leave questions unresolved.
6. If a task seems unclear or impossible, it probably just feels that way. Break it down into parts. Most of them will make sense on their own.
7. You’ll encounter all kinds of tasks. The bonus ones are for those who are curious and detail-oriented. They’re optional and more challenging, but completing them gives you extra experience and insight.
8. Don't try to cheat the system or your peers. Ultimately, you'll only be cheating yourself.
9. Got a question? Ask the peer to your right. If that doesn't help, ask the peer to your left.
10. When asking for help, always make sure you understand the why, how, and what-for. Otherwise, the help won't be very useful.
11. Always push your code to the develop branch only. The master branch will be ignored. Work inside the src directory.
12. Your directory should not contain any files besides those required for the tasks.

## Chapter II

### General Information

Topics to explore:

- **OOP (Object-Oriented Programming)** — a programming paradigm that structures and organizes code as objects that interact with each other.
- **Procedural approach** — a programming style in which tasks are broken down into small procedures or functions.
- **Functional paradigm** — focuses on defining and applying functions that transform data without altering the original values.
- **Multiparadigm approach** — combining multiple programming paradigms within a single program.
- **Differences from C and C++** — syntax, dynamic typing, memory management, and built-in libraries.
- **Asynchronous / parallel programming** — techniques for running multiple tasks simultaneously.

## Chapter III

**Important!** Each task must be organized as a separate project.   
For example: `T01/src/exercise0`, `T01/src/exercise1`, ..., `T01/src/exerciseN-1`, where **N** is the total number of tasks.  
If one task builds upon the previous one, simply copy the previous project into the new directory and continue development from there.

### Task 1. Exam

Students are lining up to take an exam. Several examiners are working simultaneously. All students wait in a single, shared queue. As soon as an examiner becomes available, the next student in line goes in for their exam.

Thirty seconds after an exam begins, each examiner is permitted to take a lunch break. They finish the current session, after which they refuse new students for a random duration between 12 and 18 seconds.

The exam process works as follows:  
Each student is asked three questions from a question bank. For each question, the student randomly selects a word from the question as their answer. Statistically, boys tend to choose words closer to the beginning of the question, while girls tend to choose words closer to the end. The probabilities follow a golden ratio distribution. For example, in response to the question "There is a table", a boy would answer "There" with probability `**a = 1/F**`, "is" with probability `**b = (1–a)/F**`, and "table" with probability `**c = 1–a–b**`, where `**F ≈ 1.618...**` (for a 4-word question, `**c = (1–a–b)/F**`, and so on). A girl answering the same question would choose "table" with probability `**a**`, "is" with `**b**`, and "There" with `**c**`.

Since examiners do not know the correct answer in advance, they follow the same approach and randomly select words from the question. Multiple correct answers are allowed. After selecting one answer, the examiner has a 1/3 chance of selecting another answer and continues this process until all the words in the question have been selected as correct or the examiner stops.

Once the student has answered, the examiner decides whether the student passed the exam. There is a 1/8 chance that the examiner is in a bad mood (in which case the student automatically fails), a 1/4 chance that the examiner is in a good mood (in which case the student automatically passes), and a 5/8 chance that the examiner is in a neutral mood. In that case, the outcome depends on performance: the student passes if they answered more questions correctly than incorrectly.

The exam's duration depends on the length of the examiner's name. For example, an examiner named **Stepan** (6 letters) would conduct exams lasting between 5 and 7 seconds (a random float in that range).

You need to simulate the exam process.

When the program starts:

- The list of examiners is read from the `examiners.txt` file.
- The list of students who arrived early and formed a queue is read from `students.txt`.
- The question bank is read from the `questions.txt` file.

The exam then begins.

Each examiner conducts exams on a separate process.

During execution, the console must display up-to-date exam information, including:

1. **Table of Students** with two columns: "Student" and "Status".
    - The status can be one of the following: "In Queue", "Passed", or "Failed". The table must be sorted by status: first, students in the queue in the order they’ll be examined; second, those who passed; and third, those who failed.
2. **Table of Examiners** with five columns: "Examiner", "Current Student", "Total Students", "Failed", and "Work Time".
    - When an examiner is on a break or has finished for the day, display "-" in the "Current student" column.
3. A separate line showing the number of students still in the queue out of the total.
4. A separate line displaying the time since the exam started.

This information should be updated in place, not printed as new lines.

**When the exam ends and program stops, display:**

1. **Table of Students** with two columns: "Student" and "Status".
    - Status is now only "Passed" or "Failed". The table is sorted with "Passed" first and "Failed" last.
2. **Table of Examiners** with four columns: "Examiner", "Total Students", "Failed", and "Work Time".
3. A separate line showing the total time from the start to the finish of the exam.
4. A separate line listing top-performing students (those who passed the exam the fastest), separated by commas.
5. A separate line listing top examiners (those with the lowest failure rate among their students), comma-separated.
6. A separate line listing students to be expelled — these are the students who failed and finished earlier than other students who also failed.
7. A separate line listing the best questions, separated by commas. A question is considered the best if the highest number of students answered it correctly.
8. A separate line with the exam result summary. The exam is considered successful if **more than 85%** of students pass.

**Input**

| examiners.txt |
| --- |
| Stepan M<br>Darya F<br>Mikhail M |

| students.txt |
| --- |
| Petr M<br>Sergey M<br>Varvara F<br><br>Ivan M<br>Ekaterina F<br>Alexandra F<br>Aleksey M |

| questions.txt |
| --- |
| There is a table<br>A man is a dog’s friend<br>Solar eclipses affect people<br>Programming is an interesting activity |

**Output**

During exam

```
+------------+----------+
| Student    |  Status  |
+------------+----------+
| Aleksey    | In queue |
| Petr       |  Passed  |
| Ivan       |  Passed  |
| Ekaterina  |  Passed  |
| Sergey     |  Failed  |
| Varvara    |  Failed  |
| Alexandra  |  Failed  |
+------------+----------+

+-------------+-----------------+-----------------+---------+--------------+
| Examiner    | Current student | Total students  | Failed  | Work time    |
+-------------+-----------------+-----------------+---------+--------------+
| Stepan      | Aleksey         |        1        |    0    |    12.31     |
| Darya       | -               |        3        |    2    |    12.14     |
| Mikhail     | -               |        2        |    1    |     7.21     |
+-------------+-----------------+-----------------+---------+--------------+

Remaining in queue: 1 out of 7
Time since exam started: 12.31

```

After exam

```
+------------+----------+
| Student    |  Status  |
+------------+----------+
| Petr       |  Passed  |
| Ivan       |  Passed  |
| Ekaterina  |  Passed  |
| Sergey     |  Failed  |
| Varvara    |  Failed  |
| Alexandra  |  Failed  |
| Aleksey    |  Failed  |
+------------+----------+

+-------------+-----------------+---------+--------------+
| Examiner    | Total students  | Failed  | Work time    |
+-------------+-----------------+---------+--------------+
| Stepan      |        2        |    1    |    12.35     |
| Darya       |        3        |    2    |    12.14     |
| Mikhail     |        2        |    1    |     7.21     |
+-------------+-----------------+---------+--------------+

Time from exam start to finish: 12.35  
Top-performing students: Ivan  
Top examiners: Stepan, Mikhail  
Students to be expelled: Varvara  
Best questions: There is a table, A man is a dog’s friend  
Result: Exam failed
```

### Task 2. Image Downloader
Write a link handler that prompts the user to enter an image URL and downloads the image asynchronously. Ask the user for the next URL immediately after they enter the previous one. Continue doing so until they enter an empty line. If not all images have been downloaded by that point, display a message and wait for all downloads to finish before terminating the program.

Do not terminate the program immediately if any error occurs. Instead, store the status for summary output at the end.  
At the beginning, the user must specify where to save the downloaded images.   
If the specified path is invalid or the program does not have write access to it, prompt the user to enter a different path.

Before exiting, display a summary of successful and failed downloads.

**Input**

```
./img
https://images2.pics4learning.com/catalog/s/swamp_15.jpg
https://bad-link-no-website-here.strange/img.png
https://images2.pics4learning.com/catalog/p/parrot.jpg

```

**Output**

Summary of successful and unsuccessful downloads

```
+----------------------------------------------------------+--------+
| Link                                                     | Status |
+----------------------------------------------------------+--------+
| https://images2.pics4learning.com/catalog/s/swamp_15.jpg | Success|
| https://bad-link-no-website-here.strange/img.png         | Error  |
| https://images2.pics4learning.com/catalog/p/parrot.jpg   | Success|
+----------------------------------------------------------+--------+
```