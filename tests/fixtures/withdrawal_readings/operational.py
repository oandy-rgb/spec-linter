# Operational reading: funds, then a cumulative daily limit, then approval.
INPUTS = {"amount": [1000, 5000, 10000], "withdrawn_today": [0, 4000], "approved": [False, True]}


def outcome(case):
    if case["amount"] > case["balance"]:
        return "rejected:funds"
    if case["withdrawn_today"] + case["amount"] > 5000:
        return "rejected:limit"
    if case["amount"] > 10000 and not case["approved"]:
        return "needs_approval"
    return "allowed"
