import sys

sys.path.insert(0, "utils")

from processer import _enrich_experience


def test_company_header_then_roles():
    extracted = {
        "experience": {
            "basic": [
                ["Company Inc", "Full-time", "Remote"],
                ["Senior Dev", "2020-2023"],
                ["Junior Dev", "2018-2020"],
            ],
            "description": [
                ["Built stuff", "Python"],
                ["Learned stuff"],
            ],
        },
    }
    result = _enrich_experience(extracted)
    assert result["experience"]["basic"] == [
        ["Senior Dev", "Company Inc", "2020-2023", "Remote"],
        ["Junior Dev", "Company Inc", "2018-2020", "Remote"],
    ]
    assert result["experience"]["description"] == [
        ["Built stuff", "Python"],
        ["Learned stuff"],
    ]


def test_standalone_roles():
    extracted = {
        "experience": {
            "basic": [
                ["Full Stack Dev", "Company A · Full-time", "2024-2025", "Hybrid"],
                ["Backend Dev", "Company B · Contract", "2023-2024", "Remote"],
            ],
            "description": [
                ["Did full stack"],
                ["Did backend"],
            ],
        },
    }
    result = _enrich_experience(extracted)
    assert result["experience"]["basic"] == [
        ["Full Stack Dev", "Company A", "2024-2025", "Hybrid"],
        ["Backend Dev", "Company B", "2023-2024", "Remote"],
    ]


def test_orphan_role_no_company():
    extracted = {
        "experience": {
            "basic": [
                ["Solo Role", "2023-2024"],
            ],
            "description": [
                ["Did things"],
            ],
        },
    }
    result = _enrich_experience(extracted)
    assert result["experience"]["basic"] == [
        ["Solo Role", "Solo Role", "2023-2024", ""],
    ]


def test_no_experience():
    extracted = {"education": {"basic": [["UTN"]]}}
    result = _enrich_experience(extracted)
    assert result == extracted


def test_empty_experience():
    extracted = {"experience": {"basic": [], "description": []}}
    result = _enrich_experience(extracted)
    assert result["experience"]["basic"] == []
    assert result["experience"]["description"] == []


def test_company_no_location():
    extracted = {
        "experience": {
            "basic": [
                ["Corp", "Full-time", "Office"],
                ["Dev", "2019-2021"],
            ],
            "description": [["desc"]],
        },
    }
    result = _enrich_experience(extracted)
    assert result["experience"]["basic"] == [
        ["Dev", "Corp", "2019-2021", "Office"],
    ]


def test_skills_merged_into_description():
    extracted = {
        "experience": {
            "basic": [
                ["Corp", "Full-time", "Remote"],
                ["Dev", "2023-2024"],
            ],
            "description": [["Did stuff"]],
            "skills": [["Aptitudes: Python · React"]],
        },
    }
    result = _enrich_experience(extracted)
    assert result["experience"]["description"] == [
        ["Did stuff", "Aptitudes: Python · React"],
    ]
    assert "skills" not in result["experience"]
