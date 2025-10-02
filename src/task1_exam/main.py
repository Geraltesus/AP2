import multiprocessing as mp
import queue
import random
import sys
import time
from pathlib import Path
from typing import Dict, List, Sequence, Tuple


def golden_weights(count: int, reverse: bool = False) -> List[float]:
    if count <= 0:
        return []
    phi = (1 + 5 ** 0.5) / 2
    weights = [0.0 for _ in range(count)]
    remaining = 1.0
    indexes = list(range(count))
    if reverse:
        indexes = list(reversed(indexes))
    for idx in indexes[:-1]:
        weight = remaining / phi
        weights[idx] = weight
        remaining -= weight
    weights[indexes[-1]] = remaining
    return weights


def choose_word(words: Sequence[str], gender: str) -> str:
    weights = golden_weights(len(words), reverse=(gender.upper() == "Ж"))
    return random.choices(list(words), weights=weights, k=1)[0]


def choose_multiple_words(words: Sequence[str], gender: str) -> List[str]:
    available = list(words)
    selected: List[str] = []
    while available:
        weights = golden_weights(len(available), reverse=(gender.upper() == "Ж"))
        choice = random.choices(available, weights=weights, k=1)[0]
        selected.append(choice)
        available.remove(choice)
        if len(selected) == len(words):
            break
        if random.random() >= 1 / 3:
            break
    return selected


def parse_people(path: Path) -> List[Tuple[str, str]]:
    result: List[Tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            raise ValueError(f"Некорректная строка в файле {path.name}: '{line}'")
        name = " ".join(parts[:-1])
        gender = parts[-1]
        result.append((name, gender))
    return result


def parse_questions(path: Path) -> List[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def examiner_process(
    examiner_name: str,
    examiner_gender: str,
    student_queue: mp.Queue,
    student_info: Dict[str, Dict[str, object]],
    examiner_state: Dict[str, Dict[str, object]],
    question_bank: Sequence[str],
    question_stats: Dict[str, Dict[str, object]],
    start_time: float,
) -> None:
    random.seed()
    info_proxy = examiner_state[examiner_name]
    lunch_taken = False

    while True:
        try:
            student = student_queue.get(timeout=0.5)
        except queue.Empty:
            continue
        if student is None:
            break
        student_name, student_gender = student
        student_record = student_info[student_name]
        student_record["start_time"] = time.time()
        info_proxy["current_student"] = student_name
        info_proxy["current_start"] = time.time()

        min_duration = max(0.5, len(examiner_name) - 1)
        max_duration = max(min_duration, len(examiner_name) + 1)
        duration = random.uniform(min_duration, max_duration)

        correct_answers = 0
        incorrect_answers = 0
        asked_questions: List[Tuple[str, bool]] = []

        for _ in range(3):
            question = random.choice(question_bank)
            words = question.split()
            student_answer = choose_word(words, student_gender)
            examiner_answers = choose_multiple_words(words, examiner_gender)
            is_correct = student_answer in examiner_answers
            if is_correct:
                correct_answers += 1
            else:
                incorrect_answers += 1
            asked_questions.append((question, is_correct))

        time.sleep(duration)

        mood_roll = random.random()
        if mood_roll < 1 / 8:
            passed = False
        elif mood_roll < 1 / 8 + 1 / 4:
            passed = True
        else:
            passed = correct_answers > incorrect_answers

        student_record["status"] = "Сдал" if passed else "Провалил"
        student_record["end_time"] = time.time()
        student_record["duration"] = duration
        student_record["correct"] = correct_answers
        student_record["incorrect"] = incorrect_answers

        for question, is_correct in asked_questions:
            stats_proxy = question_stats[question]
            stats_proxy["asked"] = stats_proxy.get("asked", 0) + 1
            if is_correct:
                stats_proxy["correct"] = stats_proxy.get("correct", 0) + 1

        info_proxy["total_students"] = info_proxy.get("total_students", 0) + 1
        if not passed:
            info_proxy["failed"] = info_proxy.get("failed", 0) + 1
        total_work_time = info_proxy.get("total_work_time", 0.0) + duration
        info_proxy["total_work_time"] = total_work_time
        info_proxy["current_student"] = "-"
        info_proxy["current_start"] = 0.0

        if not lunch_taken and time.time() - start_time >= 30:
            lunch_taken = True
            info_proxy["on_break"] = True
            break_duration = random.uniform(12, 18)
            time.sleep(break_duration)
            info_proxy["break_time"] = info_proxy.get("break_time", 0.0) + break_duration
            info_proxy["on_break"] = False

    info_proxy["active"] = False


def load_data(base_path: Path) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]], List[str]]:
    examiners_path = base_path / "examiners.txt"
    students_path = base_path / "students.txt"
    questions_path = base_path / "questions.txt"
    if not (examiners_path.exists() and students_path.exists() and questions_path.exists()):
        missing = [
            str(path.name)
            for path in (examiners_path, students_path, questions_path)
            if not path.exists()
        ]
        raise FileNotFoundError(
            "Не найдены входные файлы: " + ", ".join(missing)
        )
    examiners = parse_people(examiners_path)
    students = parse_people(students_path)
    questions = parse_questions(questions_path)
    if not questions:
        raise ValueError("Банк вопросов пуст")
    return examiners, students, questions


def clear_console() -> None:
    sys.stdout.write("\033[H\033[J")
    sys.stdout.flush()


def format_table(headers: Sequence[str], rows: Sequence[Sequence[object]]) -> str:
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    line_top = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    header_line = "|" + "|".join(f" {headers[i].ljust(widths[i])} " for i in range(len(headers))) + "|"
    row_lines = [
        "|" + "|".join(f" {str(cell).ljust(widths[i])} " for i, cell in enumerate(row)) + "|"
        for row in rows
    ]
    return "\n".join([line_top, header_line, line_top, *row_lines, line_top])


def collect_student_rows(
    student_info: Dict[str, Dict[str, object]],
    student_order: Sequence[str],
    include_queue: bool = True,
) -> List[Tuple[str, str]]:
    order_map = {name: idx for idx, name in enumerate(student_order)}

    def sort_key(item: Tuple[str, Dict[str, object]]):
        name, record = item
        status = record.get("status", "Очередь")
        if status == "Сдал":
            return (1, record.get("end_time", float("inf")))
        if status == "Провалил":
            return (2, record.get("end_time", float("inf")))
        return (0, order_map.get(name, float("inf")))

    rows = []
    for name, record in sorted(student_info.items(), key=sort_key):
        status = record.get("status", "Очередь")
        if not include_queue and status == "Очередь":
            continue
        rows.append((name, status))
    return rows


def collect_examiner_rows(
    examiner_state: Dict[str, Dict[str, object]],
    running: bool,
) -> List[Tuple[object, ...]]:
    rows = []
    for name in sorted(examiner_state.keys()):
        record = examiner_state[name]
        total_students = record.get("total_students", 0)
        failed = record.get("failed", 0)
        total_work_time = record.get("total_work_time", 0.0)
        current_student = record.get("current_student", "-")
        current_start = record.get("current_start", 0.0)
        if running and current_student != "-" and current_start:
            total_work_time += time.time() - current_start
        work_time_value = f"{total_work_time:.2f}"
        if running:
            rows.append((
                name,
                current_student if not record.get("on_break") else "-",
                total_students,
                failed,
                work_time_value,
            ))
        else:
            rows.append((
                name,
                total_students,
                failed,
                work_time_value,
            ))
    return rows


def monitor_exam(
    student_info: Dict[str, Dict[str, object]],
    student_order: Sequence[str],
    examiner_state: Dict[str, Dict[str, object]],
    total_students: int,
    start_time: float,
    processes: Sequence[mp.Process],
) -> None:
    while True:
        clear_console()
        student_rows = collect_student_rows(student_info, student_order)
        student_table = format_table(("Студент", "Статус"), student_rows)
        examiner_rows = collect_examiner_rows(examiner_state, running=True)
        examiner_table = format_table(
            ("Экзаменатор", "Текущий студент", "Всего студентов", "Завалил", "Время работы"),
            examiner_rows,
        )
        remaining = sum(
            1
            for record in student_info.values()
            if record.get("status", "Очередь") not in {"Сдал", "Провалил"}
        )
        elapsed = time.time() - start_time
        print(student_table)
        print()
        print(examiner_table)
        print()
        print(f"Осталось в очереди: {remaining} из {total_students}")
        print(f"Время с момента начала экзамена: {elapsed:.2f}")

        if remaining == 0 and not any(p.is_alive() for p in processes):
            break
        time.sleep(0.5)


def summarize_exam(
    student_info: Dict[str, Dict[str, object]],
    student_order: Sequence[str],
    examiner_state: Dict[str, Dict[str, object]],
    start_time: float,
    question_stats: Dict[str, Dict[str, object]],
) -> None:
    clear_console()
    student_rows = collect_student_rows(student_info, student_order, include_queue=False)
    student_rows.sort(key=lambda row: (0 if row[1] == "Сдал" else 1, row[0]))
    student_table = format_table(("Студент", "Статус"), student_rows)

    examiner_rows = collect_examiner_rows(examiner_state, running=False)
    examiner_table = format_table(
        ("Экзаменатор", "Всего студентов", "Завалил", "Время работы"),
        examiner_rows,
    )

    end_time = max(
        [record.get("end_time", start_time) for record in student_info.values()]
        + [start_time]
    )
    total_duration = end_time - start_time

    passed_students = [
        (name, record)
        for name, record in student_info.items()
        if record.get("status") == "Сдал"
    ]
    failed_students = [
        (name, record)
        for name, record in student_info.items()
        if record.get("status") == "Провалил"
    ]

    if passed_students:
        best_time = min(record.get("duration", float("inf")) for _, record in passed_students)
        best_students = sorted(
            name
            for name, record in passed_students
            if abs(record.get("duration", float("inf")) - best_time) < 1e-6
        )
    else:
        best_students = []

    examiner_fail_rates: List[Tuple[str, float]] = []
    for name, record in examiner_state.items():
        total = record.get("total_students", 0)
        failed = record.get("failed", 0)
        rate = failed / total if total else 1.0
        examiner_fail_rates.append((name, rate))
    best_examiner_rate = min(rate for _, rate in examiner_fail_rates) if examiner_fail_rates else 1.0
    best_examiners = sorted(
        name for name, rate in examiner_fail_rates if abs(rate - best_examiner_rate) < 1e-6
    )

    expelled_students: List[str] = []
    if failed_students:
        earliest_fail = min(record.get("end_time", float("inf")) for _, record in failed_students)
        expelled_students = sorted(
            name
            for name, record in failed_students
            if abs(record.get("end_time", float("inf")) - earliest_fail) < 1e-6
        )

    best_questions: List[str] = []
    if question_stats:
        max_correct = max(stats.get("correct", 0) for stats in question_stats.values())
        if max_correct > 0:
            best_questions = sorted(
                question
                for question, stats in question_stats.items()
                if stats.get("correct", 0) == max_correct
            )

    total_students = len(student_info)
    passed_count = len(passed_students)
    exam_success = passed_count / total_students >= 0.85 if total_students else False

    print(student_table)
    print()
    print(examiner_table)
    print()
    print(
        f"Время с момента начала экзамена и до момента и его завершения: {total_duration:.2f}"
    )
    print(
        "Имена лучших студентов: "
        + (", ".join(best_students) if best_students else "-")
    )
    print(
        "Имена лучших экзаменаторов: "
        + (", ".join(best_examiners) if best_examiners else "-")
    )
    print(
        "Имена студентов, которых после экзамена отчислят: "
        + (", ".join(expelled_students) if expelled_students else "-")
    )
    print(
        "Лучшие вопросы: "
        + (", ".join(best_questions) if best_questions else "-")
    )
    print("Вывод: экзамен " + ("удался" if exam_success else "не удался"))


def run_simulation(base_path: Path) -> None:
    examiners, students, questions = load_data(base_path)
    manager = mp.Manager()
    student_info = manager.dict()
    examiner_state = manager.dict()
    question_stats = manager.dict()

    for question in questions:
        question_stats[question] = manager.dict({"asked": 0, "correct": 0})

    student_order = []
    for name, gender in students:
        student_info[name] = manager.dict(
            {
                "gender": gender,
                "status": "Очередь",
                "start_time": None,
                "end_time": None,
                "duration": None,
            }
        )
        student_order.append(name)

    for name, gender in examiners:
        examiner_state[name] = manager.dict(
            {
                "gender": gender,
                "total_students": 0,
                "failed": 0,
                "total_work_time": 0.0,
                "current_student": "-",
                "current_start": 0.0,
                "on_break": False,
                "active": True,
            }
        )

    student_queue: mp.Queue = manager.Queue()  # type: ignore[assignment]
    for student in students:
        student_queue.put(student)
    for _ in examiners:
        student_queue.put(None)

    start_time = time.time()

    processes: List[mp.Process] = []
    for name, gender in examiners:
        p = mp.Process(
            target=examiner_process,
            args=(
                name,
                gender,
                student_queue,
                student_info,
                examiner_state,
                questions,
                question_stats,
                start_time,
            ),
        )
        p.start()
        processes.append(p)

    try:
        monitor_exam(student_info, student_order, examiner_state, len(students), start_time, processes)
    finally:
        for p in processes:
            p.join()

    summarize_exam(student_info, student_order, examiner_state, start_time, question_stats)


def main() -> None:
    base_path = Path(__file__).resolve().parent
    run_simulation(base_path)


if __name__ == "__main__":
    if sys.platform.startswith("win"):
        mp.freeze_support()
    main()
