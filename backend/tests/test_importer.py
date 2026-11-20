from datetime import date
from pathlib import Path

from backend.app.csv_reader import CsvInputError, read_csv
from backend.app.importer import import_csv

FIXTURE = Path(__file__).parent / "fixtures" / "students_fixture.csv"
REFERENCE_DATE = date(2026, 11, 19)


def test_committed_fixture_counts() -> None:
    result = import_csv(FIXTURE, REFERENCE_DATE)
    assert (result.rows_read, len(result.accepted), len(result.rejected)) == (25, 16, 9)


def test_bom_crlf_quotes_blanks_and_extra_columns(tmp_path: Path) -> None:
    path = tmp_path / "input.csv"
    path.write_text("\ufeffSTUDENT_ID, FULL_NAME,EMAIL,DATE_OF_BIRTH,GRADE_LEVEL,SECTION,MATHS,SCIENCE,ENGLISH,SOCIAL_STUDIES,SECOND_LANGUAGE,extra\r\n"
                    'abc-1,"Singh,  Aarav",A@EXAMPLE.EDU,19/11/2015,09,b,0,100,12.5,50,75,ignored\r\n'
                    ',,,,,,,,,,,\r\n', encoding="utf-8")
    result = import_csv(path, REFERENCE_DATE)
    assert result.rows_read == 1
    assert len(result.accepted) == 1
    assert result.accepted[0]["student_id"] == "ABC-1"
    assert result.accepted[0]["full_name"] == "Singh, Aarav"
    assert result.accepted[0]["email"] == "a@example.edu"


def test_wrong_width_is_rejected_against_actual_header_width(tmp_path: Path) -> None:
    path = tmp_path / "input.csv"
    path.write_text("student_id,full_name,email,date_of_birth,grade_level,section,maths,science,english,social_studies,second_language,parent_phone\n"
                    "STU1,Valid Name,a@example.edu,2015-01-01,5,A,1,2,3,4,5\n", encoding="utf-8")
    result = import_csv(path, REFERENCE_DATE)
    assert result.error_counts == {"WRONG_FIELD_COUNT": 1}


def test_duplicate_id_is_reserved_by_invalid_first_record(tmp_path: Path) -> None:
    path = tmp_path / "input.csv"
    path.write_text("student_id,full_name,email,date_of_birth,grade_level,section,maths,science,english,social_studies,second_language\n"
                    "stu-1,First Name,not-an-email,2015-01-01,5,A,1,2,3,4,5\n"
                    "STU-1,Second Name,b@example.edu,2015-01-01,5,A,1,2,3,4,5\n", encoding="utf-8")
    result = import_csv(path, REFERENCE_DATE)
    assert len(result.rejected) == 2
    assert result.error_counts["INVALID_FORMAT"] == 1
    assert result.error_counts["DUPLICATE_ID"] == 1


def test_multiple_errors_are_retained(tmp_path: Path) -> None:
    path = tmp_path / "input.csv"
    path.write_text("student_id,full_name,email,date_of_birth,grade_level,section,maths,science,english,social_studies,second_language\n"
                    "x,,bad,31/02/2015,99,Z,-1,101,,nope,5\n", encoding="utf-8")
    result = import_csv(path, REFERENCE_DATE)
    assert len(result.rejected) == 1
    assert len(result.rejected[0].errors) >= 7


def test_missing_headers_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "input.csv"
    path.write_text("student_id,full_name\n", encoding="utf-8")
    try:
        read_csv(path)
    except CsvInputError as exc:
        assert "Missing required headers" in str(exc)
    else:
        raise AssertionError("expected missing header error")
