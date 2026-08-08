IMPORTANT_DAYS = [7, 8, 10, 12, 13, 16, 22, 23, 27, 28, 29, 30, 31]


def analyze_candidate(candidate):
    missions = candidate.get("missions", [])
    completed = []
    skipped = []
    failed = []
    strong = []
    probe = []

    for mission in missions:
        day = mission.get("day")
        if mission.get("skipped"):
            skipped.append(day)
            continue
        if mission.get("passed") is False:
            failed.append(day)
            probe.append(day)
            continue
        if mission.get("passed"):
            completed.append(day)
            attempts = mission.get("attempts", 1)
            if attempts <= 1:
                strong.append(day)
            elif attempts >= 3:
                probe.append(day)

    signals = candidate.get("signals", {})
    missions_completed = signals.get("missionsCompleted", len(completed))
    first_try = signals.get("missionsFirstTry", len(strong))

    if missions_completed >= 30 and first_try >= 20:
        difficulty = "advanced"
    elif missions_completed >= 24:
        difficulty = "intermediate"
    else:
        difficulty = "foundational"

    return {
        "completed_days": completed,
        "skipped_days": skipped,
        "failed_days": failed,
        "strong_days": strong,
        "probe_days": sorted(set(probe)),
        "difficulty": difficulty,
        "signals": signals,
    }


def candidate_summary(candidate, day_map):
    analysis = analyze_candidate(candidate)

    def titles(days):
        return [day_map.get(day, {}).get("title", f"Day {day}") for day in days if day in day_map]

    return {
        "analysis": analysis,
        "strong_topics": titles(analysis["strong_days"])[:4],
        "probe_topics": titles(analysis["probe_days"])[:4],
        "skipped_topics": titles(analysis["skipped_days"])[:4],
    }
