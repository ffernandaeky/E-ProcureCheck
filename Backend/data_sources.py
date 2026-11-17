"""Spreadsheet-backed data source adapters."""

from abc import ABC, abstractmethod
from typing import Any

from openpyxl import load_workbook

from Backend.config import DATA_SOURCE, SpreadsheetConfig, active_spreadsheet


def _code_as_string(value: Any, number_format: str = "General") -> str:
    """Return a spreadsheet code as text, retaining zero masks if numeric."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, int) and number_format and set(number_format) == {"0"}:
        return str(value).zfill(len(number_format))
    return str(value)


class DataSource(ABC):
    @abstractmethod
    def find_by_unique_code(self, code: str) -> dict[str, Any] | None:
        """Find one record using exact Unique Code matching."""

    @abstractmethod
    def get_summary(self) -> dict[str, Any]:
        """Return read-only metadata about the active data source."""


class DummySpreadsheetDataSource(DataSource):
    def __init__(self, config: SpreadsheetConfig):
        self.config = config

    def find_by_unique_code(self, code: str) -> dict[str, Any] | None:
        # The workbook is opened read-only and never saved or modified.
        workbook = load_workbook(self.config.path, read_only=True, data_only=True)
        try:
            sheet = workbook[self.config.sheet_name]
            code_header = sheet.cell(self.config.header_row, self.config.unique_code_column).value
            headers = {
                column: str(sheet.cell(self.config.header_row, column).value or "")
                for column in self.config.display_columns
            }
            for row_number in range(self.config.data_start_row, sheet.max_row + 1):
                code_cell = sheet.cell(row_number, self.config.unique_code_column)
                row_code = _code_as_string(code_cell.value, code_cell.number_format)
                if row_code == code:
                    record: dict[str, Any] = {str(code_header): row_code}
                    for column in self.config.display_columns:
                        value = sheet.cell(row_number, column).value
                        record[headers[column]] = value
                    return record
            return None
        finally:
            workbook.close()

    def get_summary(self) -> dict[str, Any]:
        workbook = load_workbook(self.config.path, read_only=True, data_only=True)
        try:
            sheet = workbook[self.config.sheet_name]
            total_records = sum(
                1
                for (value,) in sheet.iter_rows(
                    min_row=self.config.data_start_row,
                    min_col=self.config.unique_code_column,
                    max_col=self.config.unique_code_column,
                    values_only=True,
                )
                if _code_as_string(value) != ""
            )
            return {
                "status": "available",
                "source": self.config.path.name,
                "sheet": self.config.sheet_name,
                "total_registered_items": total_records,
            }
        finally:
            workbook.close()


class ProductionSpreadsheetDataSource(DataSource):
    """Placeholder for a production-specific adapter."""

    def find_by_unique_code(self, code: str) -> dict[str, Any] | None:
        raise NotImplementedError("Configure a production data source adapter before switching.")

    def get_summary(self) -> dict[str, Any]:
        raise NotImplementedError("Configure a production data source adapter before switching.")


def get_data_source() -> DataSource:
    config = active_spreadsheet()
    if DATA_SOURCE == "dummy":
        return DummySpreadsheetDataSource(config)
    if DATA_SOURCE == "production":
        return ProductionSpreadsheetDataSource()
    raise ValueError(f"Unknown DATA_SOURCE: {DATA_SOURCE}")
