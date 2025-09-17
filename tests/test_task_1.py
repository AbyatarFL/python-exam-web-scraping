# tests/test_python_exam_web_scraping.py
import os
import pytest
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from python_exam_web_scraping import (
    ensure_output_folder,
    save_csv,
    save_json,
    save_xlsx,
)

@pytest.fixture
def sample_data():
    all_data = [
        {"id": "1", "url": "http://test1.com", "date_collected": "2025-09-16 12:00:00"},
    ]
    details_data = [
        {
            "id": "2",
            "details_url": "http://test2.com/details",
            "date_scraped": "2025-09-16 12:15:00",
            "square_footage": "1200",
        }
    ]
    return all_data, details_data

def test_ensure_output_folder():
    folder = ensure_output_folder()
    assert os.path.exists(folder)
    assert os.path.basename(folder) == "Output_Files"

def test_save_csv(sample_data):
    all_data, details_data = sample_data
    save_csv(all_data, details_data)
    output_dir = ensure_output_folder()
    assert os.path.exists(os.path.join(output_dir, "output.csv"))
    assert os.path.exists(os.path.join(output_dir, "details_output.csv"))

def test_save_json(sample_data):
    all_data, details_data = sample_data
    save_json(all_data, details_data)
    output_dir = ensure_output_folder()
    assert os.path.exists(os.path.join(output_dir, "output.json"))
    assert os.path.exists(os.path.join(output_dir, "details_output.json"))

def test_save_xlsx(sample_data):
    all_data, details_data = sample_data
    save_xlsx(all_data, details_data)
    output_dir = ensure_output_folder()
    assert os.path.exists(os.path.join(output_dir, "output.xlsx"))
    assert os.path.exists(os.path.join(output_dir, "details_output.xlsx"))