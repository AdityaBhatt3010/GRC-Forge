compliant_clauses = {
    "GDPR": ["(Art. 37)", "(Art. 35)", "(Art. 47)", "(Art. 36.4 h)", "(Art. 36.4 i)", "(Art. 25 f)", "(Art. 32 c)", "(Art. 6.1(e) c, d)"],
    "HIPAA": ["(164.302)", "(164.306)", "(164.308)", "(164.312(a)(1))"],
    "ISO 27001": ["(9.3.1)", "(5.2.1)", "(6.1.2.a)", "(7.5.3.c)", "(6.1.3 b)", "(A.5.18)"],
    "NIST 800-53": ["(AC)", "(RM)", "(MA)", "(SA)", "(Au/At)"],
    "PCI DSS": ["(Control 2.2)"],
    "SOC2": ["CC6.5", "CC7.1", "CC7.4"],
    "SOX": ["Section 302, Clause 302.1"]
}

non_compliant_clauses = {
    "GDPR": ["(Art. 36.4 g)", "(Art. 25 e)", "(Art. 25 m)", "GDPR Recital 286"],
    "HIPAA": ["(164.312(c)(1))"],
    "ISO 27001": ["(9.3.1)", "(7.5.3.c)", "(A.5.18)"],
    "NIST 800-53": ["(AC)", "(HR)", "(IAM)", "(Au)", "(CP)"],
    "PCI DSS": ["(Req 1)", "(Control 1.2)"],
    "SOC2": ["CC6.5", "CC7.1"],
    "SOX": ["Section 302, Clause 302.2", "Section 404, Clause 404.1", "Section 404, Clause 404.2"]
}