"""Data source configuration for development and production."""

from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Dummy spreadsheet layout (column and row numbers are 1-based).
UNIQUE_CODE_COLUMN = 1
HEADER_ROW = 1
DATA_START_ROW = 2
DISPLAY_COLUMNS = [2, 3, 4, 5, 6]


@dataclass(frozen=True)
class SpreadsheetConfig:
    path: Path
    sheet_name: str
    unique_code_column: int
    header_row: int
    data_start_row: int
    display_columns: tuple[int, ...]


# Keep the dummy workbook settings separate so the source can be switched
# without changing the search handler or presentation layer.
DUMMY_SPREADSHEET = SpreadsheetConfig(
    path=PROJECT_ROOT / "Dummy_Data_Pengadaan.xlsx",
    sheet_name="Data Pengadaan",
    unique_code_column=UNIQUE_CODE_COLUMN,
    header_row=HEADER_ROW,
    data_start_row=DATA_START_ROW,
    display_columns=tuple(DISPLAY_COLUMNS),
)

# Fill these settings when the production source is ready. The data source
# adapter can then be replaced independently from the application's logic.
PRODUCTION_SPREADSHEET = SpreadsheetConfig(
    path=PROJECT_ROOT / "data" / "production.xlsx",
    sheet_name="Data Pengadaan",
    unique_code_column=1,
    header_row=1,
    data_start_row=2,
    display_columns=(2, 3, 4, 5, 6),
)

DATA_SOURCE = "dummy"  # Change to "production" when a production adapter exists.


def active_spreadsheet() -> SpreadsheetConfig:
    if DATA_SOURCE == "dummy":
        return DUMMY_SPREADSHEET
    if DATA_SOURCE == "production":
        return PRODUCTION_SPREADSHEET
    raise ValueError(f"Unknown DATA_SOURCE: {DATA_SOURCE}")
