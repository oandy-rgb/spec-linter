# Adversarial reading: the limit is per withdrawal and approval exempts it.
INPUTS = {"amount": [1000, 5000, 10000], "approved": [False, True]}


def outcome(case):
    if case["amount"] > case["balance"]:
        return "rejected:funds"
    if case["amount"] > 10000:
        return "allowed" if case["approved"] else "needs_approval"
    if case["amount"] > 5000:
        return "rejected:limit"
    return "allowed"
