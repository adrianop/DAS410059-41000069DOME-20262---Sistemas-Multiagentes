import re
import sys

n, m, i = sys.argv[1], sys.argv[2], sys.argv[3]
path = "my1st_app.jcm"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

content = re.sub(
    r'(agent initiator : cnp_initiator\.asl \{\s*instances:\s*)\d+',
    r'\g<1>' + n,
    content,
)
content = re.sub(
    r'(n_participants\()\d+(\), n_contracts\()\d+(\))',
    r'\g<1>' + m + r'\g<2>' + i + r'\g<3>',
    content,
)
content = re.sub(
    r'(agent participant : cnp_participant\.asl \{\s*instances:\s*)\d+',
    r'\g<1>' + m,
    content,
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"set n={n} m={m} i={i}")
