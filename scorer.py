def calculate_points(time_remaining: float, time_limit: int) -> int:
    """
    Calculate points for a correct answer.
    Base: 100 points
    Speed bonus: 0–50 based on how much time remains
    """
    bonus = round(50 * (max(0.0, time_remaining) / time_limit))
    return 100 + bonus
