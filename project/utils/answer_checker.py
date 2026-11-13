def _cell(value) -> str:
    if isinstance(value, dict):
        value = value.get("name", value)
    if isinstance(value, float):
        value = round(value, 2)
        if value.is_integer():
            value = int(value)
    return str(value)


def normalize_records(rows) -> list:
    out, seen = [], set()
    for row in rows:
        values = []
        for value in row.values():
            if isinstance(value, dict):
                value = value.get("name", value)
            if isinstance(value, float):
                value = round(value, 2)
                if value.is_integer():
                    value = int(value)
            values.append(str(value))
        key = tuple(sorted(values))
        if key in seen:
            continue
        seen.add(key)
        out.append(list(key))
    return sorted(out)


def _is_seq(x):
    return isinstance(x, (list, tuple)) and not isinstance(x, (str, bytes))


def _unwrap(data):
    while (
            len(data) == 1
            and _is_seq(data[0])
            and data[0]
            and all(_is_seq(item) for item in data[0])
    ):
        data = data[0]
    return data


def normalize(data, explode_single_row=True):
    if data == [[]]:
        return []

    if not _is_seq(data):
        return [[_cell(data)]]
    if not data:
        return []

    data = _unwrap(data)

    if all(not _is_seq(item) for item in data):
        rows = [[item] for item in data]
    else:
        rows = [list(row) if _is_seq(row) else [row] for row in data]
        if explode_single_row and len(rows) == 1 and len(rows[0]) > 1:
            rows = [[value] for value in rows[0]]

    rows = [sorted(_cell(value) for value in row) for row in rows]
    rows.sort()

    return rows


def check(answers, query_ans_norm) -> bool:
    for answer in answers:
        if query_ans_norm == answer:
            return True

    return False


def _row_tokens(row) -> list:
    tokens = []
    for cell in row:
        tokens.extend(_cell(cell).split())
    return sorted(tokens)


def _tokenize(rows) -> list:
    return sorted(_row_tokens(row) for row in rows)


def check_tokens(answers, query_ans_norm) -> bool:
    target = _tokenize(query_ans_norm)
    for answer in answers:
        if _tokenize(answer) == target:
            return True

    return False


def is_answer_correct(query_ans, answers) -> bool:
    if len(query_ans) > 0 and hasattr(query_ans[0], 'data'):
        return check(answers, normalize_records([r.data() for r in query_ans]))

    rows = normalize(query_ans)
    rows_flat = normalize(query_ans, False)

    if check(answers, rows) or check(answers, rows_flat):
        return True

    return check_tokens(answers, rows) or check_tokens(answers, rows_flat)

