"""
Unit Tests - Weather Utilities & Geographic Utilities (Application Layer)

Tests:
- WeatherConversionUtils: unit conversions (wind, temperature, radiation)
- ElevationUtils: FAO-56 atmospheric corrections
- EToVariableValidator: source variable completeness
- GeographicUtils: bounding box detection
- Geo Utils (core): Haversine distance, region detection

Reference: Article Section 2.2 (Data Harmonization)
"""

import pytest

from backend.api.services.weather_utils import (
    WeatherConversionUtils,
    ElevationUtils,
)
from backend.api.services.geographic_utils import GeographicUtils
from backend.api.services.eto_variable_validator import EToVariableValidator
from backend.core.utils.geo_utils import (
    haversine_distance,
    detect_geographic_region,
)


# ============================================================================
# WeatherConversionUtils
# ============================================================================


@pytest.mark.unit
class TestWeatherConversions:
    """Tests for meteorological unit conversion functions."""

    def test_wind_10m_to_2m(self):
        """FAO-56 Eq. 47: u2 = u10 × 4.87 / ln(67.8×10 - 5.42) ≈ u10 × 0.748."""
        result = WeatherConversionUtils.convert_wind_10m_to_2m(10.0)
        assert result == pytest.approx(7.48, abs=0.1)

    def test_wind_10m_to_2m_zero(self):
        result = WeatherConversionUtils.convert_wind_10m_to_2m(0.0)
        assert result == pytest.approx(0.0, abs=0.01)

    def test_wind_10m_to_2m_none(self):
        result = WeatherConversionUtils.convert_wind_10m_to_2m(None)
        assert result is None

    def test_fahrenheit_to_celsius(self):
        assert WeatherConversionUtils.fahrenheit_to_celsius(32.0) == pytest.approx(0.0)
        assert WeatherConversionUtils.fahrenheit_to_celsius(212.0) == pytest.approx(100.0)

    def test_celsius_to_fahrenheit(self):
        assert WeatherConversionUtils.celsius_to_fahrenheit(0.0) == pytest.approx(32.0)
        assert WeatherConversionUtils.celsius_to_fahrenheit(100.0) == pytest.approx(212.0)

    def test_mph_to_ms(self):
        result = WeatherConversionUtils.mph_to_ms(1.0)
        assert result == pytest.approx(0.44704, abs=0.001)

    def test_wh_to_mj(self):
        result = WeatherConversionUtils.wh_per_m2_to_mj_per_m2(1000.0)
        assert result == pytest.approx(3.6, abs=0.01)


# ============================================================================
# ElevationUtils
# ============================================================================


@pytest.mark.unit
class TestElevationUtils:
    """Tests for FAO-56 elevation-based corrections."""

    def test_atmospheric_pressure_sea_level(self):
        """FAO-56 Eq. 7: P ≈ 101.3 kPa at z = 0."""
        p = ElevationUtils.calculate_atmospheric_pressure(0.0)
        assert p == pytest.approx(101.3, abs=0.5)

    def test_atmospheric_pressure_decreases_with_altitude(self):
        p0 = ElevationUtils.calculate_atmospheric_pressure(0.0)
        p500 = ElevationUtils.calculate_atmospheric_pressure(500.0)
        p2000 = ElevationUtils.calculate_atmospheric_pressure(2000.0)
        assert p0 > p500 > p2000

    def test_psychrometric_constant_sea_level(self):
        """FAO-56 Eq. 8: γ ≈ 0.0665 kPa/°C at z = 0."""
        gamma = ElevationUtils.calculate_psychrometric_constant(0.0)
        assert gamma == pytest.approx(0.0665, abs=0.005)

    def test_elevation_correction_factor_keys(self):
        factors = ElevationUtils.get_elevation_correction_factor(580.0)
        assert "pressure" in factors
        assert "gamma" in factors
        assert "elevation" in factors
        assert factors["elevation"] == 580.0


# ============================================================================
# GeographicUtils (bounding boxes)
# ============================================================================


@pytest.mark.unit
class TestGeographicUtils:
    """Tests for geographic bounding box utilities."""

    LOCATIONS = {
        "brazil": (-22.29, -48.58),    # Jaú, SP
        "usa": (40.71, -74.01),         # New York
        "nordic": (59.91, 10.75),       # Oslo
        "outside": (35.0, 139.0),       # Tokyo
    }

    def test_is_in_brazil(self):
        assert GeographicUtils.is_in_brazil(*self.LOCATIONS["brazil"])
        assert not GeographicUtils.is_in_brazil(*self.LOCATIONS["usa"])

    def test_is_in_usa(self):
        assert GeographicUtils.is_in_usa(*self.LOCATIONS["usa"])
        assert not GeographicUtils.is_in_usa(*self.LOCATIONS["brazil"])

    def test_is_in_nordic(self):
        assert GeographicUtils.is_in_nordic(*self.LOCATIONS["nordic"])
        assert not GeographicUtils.is_in_nordic(*self.LOCATIONS["brazil"])

    def test_is_valid_coordinate(self):
        assert GeographicUtils.is_valid_coordinate(-22.29, -48.58)
        assert not GeographicUtils.is_valid_coordinate(100.0, 200.0)


# ============================================================================
# Haversine Distance (core geo)
# ============================================================================


@pytest.mark.unit
class TestHaversineDistance:
    """Tests for Haversine great-circle distance calculation."""

    def test_same_point_zero_distance(self):
        d = haversine_distance(-22.29, -48.58, -22.29, -48.58)
        assert d == pytest.approx(0.0, abs=0.01)

    def test_known_distance_sp_rj(self):
        """São Paulo → Rio de Janeiro ≈ 360 km."""
        d = haversine_distance(-23.55, -46.63, -22.91, -43.17)
        assert 340 < d < 400

    def test_antipodal_points(self):
        """Points on opposite sides of Earth ≈ 20,000 km."""
        d = haversine_distance(0, 0, 0, 180)
        assert d == pytest.approx(20015, rel=0.01)

    def test_equator_distance_per_degree(self):
        """1 degree of longitude at equator ≈ 111 km."""
        d = haversine_distance(0, 0, 0, 1)
        assert 110 < d < 112


# ============================================================================
# Geographic Region Detection (core)
# ============================================================================


@pytest.mark.unit
class TestRegionDetection:
    """Tests for detect_geographic_region function."""

    def test_brazil(self):
        region = detect_geographic_region(-22.29, -48.58)
        assert region == "brasil"

    def test_usa(self):
        region = detect_geographic_region(40.71, -74.01)
        assert region == "usa"

    def test_europe(self):
        region = detect_geographic_region(48.86, 2.35)  # Paris
        assert region == "europe"

    def test_global_ocean(self):
        """Mid-Pacific should return 'global'."""
        region = detect_geographic_region(0.0, -170.0)
        assert region == "global"


# ============================================================================
# EToVariableValidator
# ============================================================================


@pytest.mark.unit
class TestEToVariableValidator:
    """Tests for climate source ETo variable completeness."""

    def test_nasa_power_has_all_eto_variables(self):
        assert EToVariableValidator.has_all_eto_variables("nasa_power")

    def test_openmeteo_archive_has_all_eto_variables(self):
        assert EToVariableValidator.has_all_eto_variables("openmeteo_archive")

    def test_openmeteo_forecast_has_all_eto_variables(self):
        assert EToVariableValidator.has_all_eto_variables("openmeteo_forecast")

    def test_sources_with_complete_eto(self):
        """At least 3 sources should have complete ETo capability."""
        complete = EToVariableValidator.get_sources_with_complete_eto()
        assert len(complete) >= 3

    def test_required_variables_count(self):
        """FAO-56 requires 6 meteorological variables."""
        assert len(EToVariableValidator.REQUIRED_VARIABLES) == 6
