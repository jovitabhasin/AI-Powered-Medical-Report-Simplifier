from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TestCatalogEntry:
    aliases: tuple[str, ...]
    unit: str
    ref_range: dict[str, int | float]
    summary_phrases: dict[str, str]
    explanations: dict[str, str]


LAB_TEST_CATALOG: dict[str, TestCatalogEntry] = {
    "Hemoglobin": TestCatalogEntry(
        aliases=("hemoglobin", "hemglobin", "hb"),
        unit="g/dL",
        ref_range={"low": 12.0, "high": 15.0},
        summary_phrases={
            "low": "low hemoglobin",
            "high": "high hemoglobin",
            "normal": "normal hemoglobin",
        },
        explanations={
            "low": "Low hemoglobin may relate to anemia.",
            "high": "High hemoglobin can occur with dehydration or other conditions.",
            "normal": "Hemoglobin is within the expected reference range.",
        },
    ),
    "WBC": TestCatalogEntry(
        aliases=("wbc", "white blood cell", "white blood cells", "white blood cell count"),
        unit="/uL",
        ref_range={"low": 4000, "high": 11000},
        summary_phrases={
            "low": "low white blood cell count",
            "high": "high white blood cell count",
            "normal": "normal white blood cell count",
        },
        explanations={
            "low": "Low WBC can occur with some infections or medication effects.",
            "high": "High WBC can occur with infections.",
            "normal": "White blood cell count is within the expected reference range.",
        },
    ),
    "RBC": TestCatalogEntry(
        aliases=("rbc", "red blood cell", "red blood cells", "red blood cell count"),
        unit="million/uL",
        ref_range={"low": 4.2, "high": 5.4},
        summary_phrases={
            "low": "low red blood cell count",
            "high": "high red blood cell count",
            "normal": "normal red blood cell count",
        },
        explanations={
            "low": "Low RBC may be seen in some forms of anemia.",
            "high": "High RBC can be seen with dehydration or other conditions.",
            "normal": "Red blood cell count is within the expected reference range.",
        },
    ),
    "Hematocrit": TestCatalogEntry(
        aliases=("hematocrit", "hct", "pcv"),
        unit="%",
        ref_range={"low": 36.0, "high": 46.0},
        summary_phrases={
            "low": "low hematocrit",
            "high": "high hematocrit",
            "normal": "normal hematocrit",
        },
        explanations={
            "low": "Low hematocrit can be seen when the blood has fewer red cells than expected.",
            "high": "High hematocrit can occur with dehydration or other conditions.",
            "normal": "Hematocrit is within the expected reference range.",
        },
    ),
    "MCV": TestCatalogEntry(
        aliases=("mcv", "mean corpuscular volume"),
        unit="fL",
        ref_range={"low": 80.0, "high": 100.0},
        summary_phrases={
            "low": "low mean corpuscular volume",
            "high": "high mean corpuscular volume",
            "normal": "normal mean corpuscular volume",
        },
        explanations={
            "low": "Low MCV means the red blood cells are smaller than the usual range.",
            "high": "High MCV means the red blood cells are larger than the usual range.",
            "normal": "MCV is within the expected reference range.",
        },
    ),
    "MCH": TestCatalogEntry(
        aliases=("mch", "mean corpuscular hemoglobin"),
        unit="pg",
        ref_range={"low": 27.0, "high": 33.0},
        summary_phrases={
            "low": "low mean corpuscular hemoglobin",
            "high": "high mean corpuscular hemoglobin",
            "normal": "normal mean corpuscular hemoglobin",
        },
        explanations={
            "low": "Low MCH means each red blood cell is carrying less hemoglobin than expected.",
            "high": "High MCH means each red blood cell is carrying more hemoglobin than expected.",
            "normal": "MCH is within the expected reference range.",
        },
    ),
    "MCHC": TestCatalogEntry(
        aliases=("mchc", "mean corpuscular hemoglobin concentration"),
        unit="g/dL",
        ref_range={"low": 32.0, "high": 36.0},
        summary_phrases={
            "low": "low mean corpuscular hemoglobin concentration",
            "high": "high mean corpuscular hemoglobin concentration",
            "normal": "normal mean corpuscular hemoglobin concentration",
        },
        explanations={
            "low": "Low MCHC means the hemoglobin concentration inside red blood cells is lower than expected.",
            "high": "High MCHC means the hemoglobin concentration inside red blood cells is higher than expected.",
            "normal": "MCHC is within the expected reference range.",
        },
    ),
    "Platelets": TestCatalogEntry(
        aliases=("platelets", "platelet"),
        unit="/uL",
        ref_range={"low": 150000, "high": 450000},
        summary_phrases={
            "low": "low platelet count",
            "high": "high platelet count",
            "normal": "normal platelet count",
        },
        explanations={
            "low": "Low platelets can increase the chance of bleeding.",
            "high": "High platelets can happen with inflammation or other conditions.",
            "normal": "Platelet count is within the expected reference range.",
        },
    ),
    "Neutrophils": TestCatalogEntry(
        aliases=("neutrophils", "neutrophil", "neut%"),
        unit="%",
        ref_range={"low": 40.0, "high": 70.0},
        summary_phrases={
            "low": "low neutrophils",
            "high": "high neutrophils",
            "normal": "normal neutrophils",
        },
        explanations={
            "low": "Low neutrophils can reduce the body's ability to fight some infections.",
            "high": "High neutrophils can occur when the body is responding to infection or inflammation.",
            "normal": "Neutrophils are within the expected reference range.",
        },
    ),
    "Lymphocytes": TestCatalogEntry(
        aliases=("lymphocytes", "lymphocyte", "lymph%"),
        unit="%",
        ref_range={"low": 20.0, "high": 40.0},
        summary_phrases={
            "low": "low lymphocytes",
            "high": "high lymphocytes",
            "normal": "normal lymphocytes",
        },
        explanations={
            "low": "Low lymphocytes can occur with stress, infection, or some medicines.",
            "high": "High lymphocytes can occur when the body is responding to some infections.",
            "normal": "Lymphocytes are within the expected reference range.",
        },
    ),
    "Monocytes": TestCatalogEntry(
        aliases=("monocytes", "monocyte", "mono%"),
        unit="%",
        ref_range={"low": 2.0, "high": 8.0},
        summary_phrases={
            "low": "low monocytes",
            "high": "high monocytes",
            "normal": "normal monocytes",
        },
        explanations={
            "low": "Low monocytes are often less specific and should be interpreted with the full report.",
            "high": "High monocytes can occur during recovery from infection or ongoing inflammation.",
            "normal": "Monocytes are within the expected reference range.",
        },
    ),
    "Eosinophils": TestCatalogEntry(
        aliases=("eosinophils", "eosinophil", "eos%", "eosinophil count"),
        unit="%",
        ref_range={"low": 1.0, "high": 6.0},
        summary_phrases={
            "low": "low eosinophils",
            "high": "high eosinophils",
            "normal": "normal eosinophils",
        },
        explanations={
            "low": "Low eosinophils are usually less specific on their own.",
            "high": "High eosinophils can occur with allergies, asthma, or some infections.",
            "normal": "Eosinophils are within the expected reference range.",
        },
    ),
    "Basophils": TestCatalogEntry(
        aliases=("basophils", "basophil", "baso%"),
        unit="%",
        ref_range={"low": 0.0, "high": 1.0},
        summary_phrases={
            "low": "low basophils",
            "high": "high basophils",
            "normal": "normal basophils",
        },
        explanations={
            "low": "Low basophils are usually not very specific on their own.",
            "high": "High basophils can occur with allergies or some blood-related conditions.",
            "normal": "Basophils are within the expected reference range.",
        },
    ),
    "Glucose": TestCatalogEntry(
        aliases=("glucose", "blood glucose", "sugar"),
        unit="mg/dL",
        ref_range={"low": 70, "high": 99},
        summary_phrases={
            "low": "low glucose",
            "high": "high glucose",
            "normal": "normal glucose",
        },
        explanations={
            "low": "Low glucose can happen when blood sugar drops below the expected range.",
            "high": "High glucose can occur when blood sugar is above the expected range.",
            "normal": "Glucose is within the expected reference range.",
        },
    ),
    "Urea": TestCatalogEntry(
        aliases=("urea", "blood urea"),
        unit="mg/dL",
        ref_range={"low": 15.0, "high": 40.0},
        summary_phrases={
            "low": "low urea",
            "high": "high urea",
            "normal": "normal urea",
        },
        explanations={
            "low": "Low urea can occur with lower protein intake or other non-emergency causes.",
            "high": "High urea can happen when the body is dehydrated or kidney function needs more review.",
            "normal": "Urea is within the expected reference range.",
        },
    ),
    "Creatinine": TestCatalogEntry(
        aliases=("creatinine", "creat"),
        unit="mg/dL",
        ref_range={"low": 0.6, "high": 1.3},
        summary_phrases={
            "low": "low creatinine",
            "high": "high creatinine",
            "normal": "normal creatinine",
        },
        explanations={
            "low": "Low creatinine can be seen with lower muscle mass.",
            "high": "High creatinine can happen when kidney function needs more evaluation.",
            "normal": "Creatinine is within the expected reference range.",
        },
    ),
    "Sodium": TestCatalogEntry(
        aliases=("sodium", "na"),
        unit="mEq/L",
        ref_range={"low": 135.0, "high": 145.0},
        summary_phrases={
            "low": "low sodium",
            "high": "high sodium",
            "normal": "normal sodium",
        },
        explanations={
            "low": "Low sodium can happen with excess fluid, some illnesses, or some medicines.",
            "high": "High sodium can happen when the body is losing more water than usual.",
            "normal": "Sodium is within the expected reference range.",
        },
    ),
    "Potassium": TestCatalogEntry(
        aliases=("potassium", "k"),
        unit="mEq/L",
        ref_range={"low": 3.5, "high": 5.1},
        summary_phrases={
            "low": "low potassium",
            "high": "high potassium",
            "normal": "normal potassium",
        },
        explanations={
            "low": "Low potassium can affect muscle or heart function and usually needs follow-up.",
            "high": "High potassium can affect muscle or heart function and usually needs follow-up.",
            "normal": "Potassium is within the expected reference range.",
        },
    ),
    "Chloride": TestCatalogEntry(
        aliases=("chloride", "cl"),
        unit="mEq/L",
        ref_range={"low": 98.0, "high": 107.0},
        summary_phrases={
            "low": "low chloride",
            "high": "high chloride",
            "normal": "normal chloride",
        },
        explanations={
            "low": "Low chloride can occur with vomiting, excess fluid loss, or some medicines.",
            "high": "High chloride can occur with dehydration or acid-base imbalance.",
            "normal": "Chloride is within the expected reference range.",
        },
    ),
    "Calcium": TestCatalogEntry(
        aliases=("calcium", "ca"),
        unit="mg/dL",
        ref_range={"low": 8.5, "high": 10.5},
        summary_phrases={
            "low": "low calcium",
            "high": "high calcium",
            "normal": "normal calcium",
        },
        explanations={
            "low": "Low calcium can affect muscles and nerves and may need follow-up.",
            "high": "High calcium can happen with dehydration or other underlying conditions.",
            "normal": "Calcium is within the expected reference range.",
        },
    ),
}


def resolve_test_name(raw_name: str) -> str | None:
    needle = raw_name.strip().lower()
    for canonical_name, entry in LAB_TEST_CATALOG.items():
        if needle == canonical_name.lower():
            return canonical_name
        if needle in entry.aliases:
            return canonical_name
    return None


def get_aliases() -> list[str]:
    aliases: set[str] = set()
    for canonical_name, entry in LAB_TEST_CATALOG.items():
        aliases.add(canonical_name)
        aliases.update(entry.aliases)
    return sorted(aliases, key=len, reverse=True)
