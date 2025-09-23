from datetime import datetime, timedelta

# Student's timetable provided in the prompt
student_timetable = {
    "Monday": [
        "UCS2501/JB: 8:00 - 8:45",
        "UBA2541/ST: 8:45 - 9:30",
        "BREAK: 9:30 - 9:50",
        "UBA2541/ST: 9:50 - 10:35",
        "UCS2504/RSM: 10:35 - 11:20",
        "LUNCH: 11:20 - 12:20",
        "UCS2502/ADS: 12:20 - 1:05",
        "UCS2513/NRS: 1:05 - 1:50",
        "BREAK: 1:50 - 2:10",
        "TUTORIAL: 2:10 - 2:55",
        "UCS2622/MS: 2:55 - 3:40"
    ],
    "Tuesday": [
        "UCS2504/RSM: 8:00 - 8:45",
        "UCS2501/JB: 8:45 - 9:30",
        "BREAK: 9:30 - 9:50",
        "UCS2521A/UCS2521S R/TTM&AKR: 9:50 - 10:35",
        "MENTOR: 10:35 - 11:20",
        "LUNCH: 11:20 - 12:20",
        "UCS2511A/UCS2512/JB&ADS: 12:20 - 1:50", # Double period
        "BREAK: 1:50 - 2:10",
        "UCS2511A/UCS2512/JB&ADS: 2:10 - 2:55", # Lab
        "UCS2034A/UCS2032/TMR&KAM: 2:55 - 3:40"
    ],
    "Wednesday": [
        "UCS2502/ADS: 8:00 - 8:45",
        "UCS2513/NRS: 8:45 - 9:30",
        "BREAK: 9:30 - 9:50",
        "SELF LEARNING (FREE): 9:50 - 10:35",
        "CONTENT BEYOND SYLLABUS (FREE): 10:35 - 11:20",
        "LUNCH: 11:20 - 12:20",
        "UCS2521A/UCS2521S R/TTM&AKR: 12:20 - 1:05",
        "UBA2541/ST: 1:05 - 1:50",
        "BREAK: 1:50 - 2:10",
        "UCS2622/MS: 2:10 - 2:55",
        "UCS2034A/UCS2032/TMR&KAM (FREE): 2:55 - 3:40"
    ],
    "Thursday": [
        "UCS2521A/UCS2521S R/TTM&AKR: 8:00 - 8:45",
        "UCS2501/JB: 8:45 - 9:30",
        "BREAK: 9:30 - 9:50",
        "UCS2504/RSM: 9:50 - 11:20", # Double period
        "LUNCH: 11:20 - 12:20",
        "UCS2513/NRS: 12:20 - 1:05",
        "UCS2502/ADS: 1:05 - 1:50",
        "BREAK: 1:50 - 2:10",
        "TUTORIAL: 2:10 - 2:55",
        "UCS2034A/UCS2032/TMR&KAM: 2:55 - 3:40"
    ],
    "Friday": [
        "UCS2513/NRS: 8:00 - 8:45",
        "UCS2501/JB: 8:45 - 9:30",
        "BREAK: 9:30 - 9:50",
        "UCS2502/ADS: 9:50 - 10:35",
        "UCS2504/RSM: 10:35 - 11:20",
        "LUNCH: 11:20 - 12:20",
        "UCS2511A/UCS2512/JB&ADS: 12:20 - 1:50", # Double period
        "BREAK: 1:50 - 2:10",
        "UCS2511A/UCS2512/JB&ADS: 2:10 - 2:55", # Lab
        "UCS2622/MS: 2:55 - 3:40"
    ]
}

# Dr. Nanda Ma'am's assumed working hours and breaks
# Assuming she has the same breaks as the student for simplicity
DR_NANDA_MAAM_WORK_START = "08:00"
DR_NANDA_MAAM_WORK_END = "17:00"
DR_NANDA_MAAM_BREAKS = [
    ("09:30", "09:50"),
    ("11:20", "12:20"), # Lunch
    ("13:50", "14:10") # Adjusted break to avoid conflict with student's 1:50-2:10 break
]

def parse_time_slot(slot_str, current_date):
    """Parses a time slot string (e.g., "8:00 - 8:45") into datetime objects."""
    try:
        _, time_range = slot_str.split(": ", 1)
    except ValueError: # For entries like "BREAK: 9:30 - 9:50" or "LUNCH: 11:20 - 12:20"
        time_range = slot_str.split(": ", 1)[1] if ": " in slot_str else slot_str.split(" ", 1)[1]

    start_time_str, end_time_str = time_range.split(" - ")
    start_hour, start_minute = map(int, start_time_str.split(":"))
    end_hour, end_minute = map(int, end_time_str.split(":"))

    # Convert current_date (date object) to datetime object before replacing time components
    start_dt = datetime.combine(current_date, datetime.min.time()).replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
    end_dt = datetime.combine(current_date, datetime.min.time()).replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
    return start_dt, end_dt

def get_busy_slots(day_schedule, current_date):
    """Extracts busy slots from a daily schedule."""
    busy_slots = []
    for entry in day_schedule:
        if "FREE" not in entry: # Consider "FREE" slots as not busy for the student
            start_dt, end_dt = parse_time_slot(entry, current_date)
            busy_slots.append((start_dt, end_dt))
    return busy_slots

def get_dr_nanda_maam_free_slots(current_date, slot_duration_minutes=45):
    """Calculates Dr. Nanda Ma'am's free slots for a given day."""
    dr_nanda_maam_busy_slots = []

    # Add fixed breaks to busy slots
    for start_str, end_str in DR_NANDA_MAAM_BREAKS:
        # Convert current_date (date object) to datetime object before replacing time components
        start_dt = datetime.combine(current_date, datetime.min.time()).replace(hour=int(start_str.split(":")[0]), minute=int(start_str.split(":")[1]), second=0, microsecond=0)
        end_dt = datetime.combine(current_date, datetime.min.time()).replace(hour=int(end_str.split(":")[0]), minute=int(end_str.split(":")[1]), second=0, microsecond=0)
        dr_nanda_maam_busy_slots.append((start_dt, end_dt))

    # Define her overall working period
    work_start_dt = datetime.combine(current_date, datetime.min.time()).replace(hour=int(DR_NANDA_MAAM_WORK_START.split(":")[0]), minute=int(DR_NANDA_MAAM_WORK_START.split(":")[1]), second=0, microsecond=0)
    work_end_dt = datetime.combine(current_date, datetime.min.time()).replace(hour=int(DR_NANDA_MAAM_WORK_END.split(":")[0]), minute=int(DR_NANDA_MAAM_WORK_END.split(":")[1]), second=0, microsecond=0)

    # Generate potential slots and filter out busy ones
    potential_slots = []
    current_slot_start = work_start_dt
    while current_slot_start + timedelta(minutes=slot_duration_minutes) <= work_end_dt:
        current_slot_end = current_slot_start + timedelta(minutes=slot_duration_minutes)
        is_busy = False
        for busy_start, busy_end in dr_nanda_maam_busy_slots:
            # Check for overlap
            if max(current_slot_start, busy_start) < min(current_slot_end, busy_end):
                is_busy = True
                break
        if not is_busy:
            potential_slots.append((current_slot_start, current_slot_end))
        current_slot_start += timedelta(minutes=slot_duration_minutes) # Move to next potential slot

    return potential_slots

def find_common_free_slots(student_busy_slots, dr_nanda_maam_free_slots, slot_duration_minutes=45):
    """Finds common free slots between student and Dr. Nanda Ma'am."""
    common_slots = []
    for dr_slot_start, dr_slot_end in dr_nanda_maam_free_slots:
        is_student_busy = False
        for student_busy_start, student_busy_end in student_busy_slots:
            # Check for overlap
            if max(dr_slot_start, student_busy_start) < min(dr_slot_end, student_busy_end):
                is_student_busy = True
                break
        if not is_student_busy:
            common_slots.append((dr_slot_start, dr_slot_end))
    return common_slots

def get_available_counselling_slots(num_days=7, slot_duration_minutes=45):
    """
    Generates available counselling slots for the next `num_days`
    by comparing student and Dr. Nanda Ma'am's timetables.
    """
    available_slots = {}
    today = datetime.now().date()

    for i in range(num_days):
        current_date = today + timedelta(days=i)
        day_name = current_date.strftime("%A") # e.g., "Monday"

        if day_name in student_timetable:
            student_day_schedule = student_timetable[day_name]
            student_busy_slots = get_busy_slots(student_day_schedule, current_date)
        else:
            student_busy_slots = [] # Assume student is free if no timetable entry

        dr_nanda_maam_free_slots = get_dr_nanda_maam_free_slots(current_date, slot_duration_minutes)
        
        common_free_slots = find_common_free_slots(student_busy_slots, dr_nanda_maam_free_slots, slot_duration_minutes)
        
        if common_free_slots:
            available_slots[current_date.strftime("%Y-%m-%d")] = [
                f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}"
                for start, end in common_free_slots
            ]
    return available_slots

if __name__ == "__main__":
    # Example usage:
    slots = get_available_counselling_slots()
    for date, time_slots in slots.items():
        print(f"Date: {date}")
        for slot in time_slots:
            print(f"  - {slot}")
