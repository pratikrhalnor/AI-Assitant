import re

def extract_steps(text):
    lines = text.split("\n")
    steps = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Detect numbered steps
        if re.match(r"^\d+\.", line):
            steps.append(line)

        # Detect action-based lines (your case)
        elif any(keyword in line.lower() for keyword in [
            "create", "configure", "set", "select", "save", "click", "map"
        ]):
            steps.append(line)

    return steps


def steps_to_mermaid(steps):
    if len(steps) < 2:
        return None

    diagram = "flowchart TD\n"

    for i, step in enumerate(steps):
        clean = step.replace('"', '').replace(";", "")

        diagram += f"A{i}[\"{clean}\"]\n"

        if i > 0:
            diagram += f"A{i-1} --> A{i}\n"

    return diagram