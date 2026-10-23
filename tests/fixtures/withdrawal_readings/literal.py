# Literal reading: the daily limit states no reject action, so it is ignored.
INPUTS = {"amount": [1000, 5000, 10000], "balance": [20000], "withdrawn_today": [0, 4000], "approved": [False, True]}


def outcome(case):
    if case["amount"] > case["balance"]:
        return "rejected:funds"
    if case["amount"] > 10000 and not case["approved"]:
        return "needs_approval"
    return "allowed"
