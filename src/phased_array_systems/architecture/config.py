"""Architecture configuration models using Pydantic."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ArrayConfig(BaseModel):
    """Configuration for the antenna array geometry.

    Attributes:
        geometry: Array geometry type
        nx: Number of elements in x-direction
        ny: Number of elements in y-direction
        dx_lambda: Element spacing in x-direction (wavelengths)
        dy_lambda: Element spacing in y-direction (wavelengths)
        scan_limit_deg: Maximum scan angle from boresight (degrees)
    """

    geometry: Literal["rectangular", "circular", "triangular"] = "rectangular"
    nx: int = Field(ge=1, description="Number of elements in x-direction")
    ny: int = Field(ge=1, description="Number of elements in y-direction")
    dx_lambda: float = Field(default=0.5, gt=0, description="Element spacing in x (wavelengths)")
    dy_lambda: float = Field(default=0.5, gt=0, description="Element spacing in y (wavelengths)")
    scan_limit_deg: float = Field(
        default=60.0, ge=0, le=90, description="Maximum scan angle (degrees)"
    )

    @property
    def n_elements(self) -> int:
        """Total number of elements in the array."""
        return self.nx * self.ny


class RFChainConfig(BaseModel):
    """Configuration for the RF chain.

    Attributes:
        tx_power_w_per_elem: Transmit power per element (Watts)
        pa_efficiency: Power amplifier efficiency (0-1)
        noise_figure_db: Receiver noise figure (dB)
        n_tx_beams: Number of simultaneous transmit beams
        feed_loss_db: Feed network loss (dB)
        system_loss_db: Additional system losses (dB)
    """

    tx_power_w_per_elem: float = Field(gt=0, description="TX power per element (W)")
    pa_efficiency: float = Field(
        default=0.3, gt=0, le=1, description="PA efficiency (0-1)"
    )
    noise_figure_db: float = Field(
        default=3.0, ge=0, description="Noise figure (dB)"
    )
    n_tx_beams: int = Field(default=1, ge=1, description="Number of TX beams")
    feed_loss_db: float = Field(default=1.0, ge=0, description="Feed network loss (dB)")
    system_loss_db: float = Field(default=0.0, ge=0, description="Additional system losses (dB)")

    @field_validator("pa_efficiency")
    @classmethod
    def validate_efficiency(cls, v: float) -> float:
        if not 0 < v <= 1:
            raise ValueError("PA efficiency must be between 0 and 1")
        return v


class CostConfig(BaseModel):
    """Configuration for cost modeling.

    Attributes:
        cost_per_elem_usd: Recurring cost per element (USD)
        nre_usd: Non-recurring engineering cost (USD)
        integration_cost_usd: System integration cost (USD)
    """

    cost_per_elem_usd: float = Field(default=100.0, ge=0, description="Cost per element (USD)")
    nre_usd: float = Field(default=0.0, ge=0, description="NRE cost (USD)")
    integration_cost_usd: float = Field(
        default=0.0, ge=0, description="Integration cost (USD)"
    )


class Architecture(BaseModel):
    """Complete system architecture configuration.

    This is the top-level configuration object that contains all
    subsystem configurations.

    Attributes:
        array: Antenna array configuration
        rf: RF chain configuration
        cost: Cost model configuration
        name: Optional name for this architecture
    """

    array: ArrayConfig
    rf: RFChainConfig
    cost: CostConfig = Field(default_factory=CostConfig)
    name: str | None = Field(default=None, description="Architecture name")

    @property
    def n_elements(self) -> int:
        """Total number of elements (convenience property)."""
        return self.array.n_elements

    def model_dump_flat(self) -> dict:
        """Return a flattened dictionary of all configuration values.

        Useful for DOE case generation where we need flat parameter names.
        """
        flat = {}
        for prefix, config in [
            ("array", self.array),
            ("rf", self.rf),
            ("cost", self.cost),
        ]:
            for key, value in config.model_dump().items():
                flat[f"{prefix}.{key}"] = value
        if self.name:
            flat["name"] = self.name
        return flat

    @classmethod
    def from_flat(cls, flat_dict: dict) -> "Architecture":
        """Create an Architecture from a flattened dictionary.

        Args:
            flat_dict: Dictionary with keys like "array.nx", "rf.tx_power_w_per_elem"

        Returns:
            Architecture instance
        """
        array_dict = {}
        rf_dict = {}
        cost_dict = {}
        name = None

        for key, value in flat_dict.items():
            if key == "name":
                name = value
            elif key.startswith("array."):
                array_dict[key.replace("array.", "")] = value
            elif key.startswith("rf."):
                rf_dict[key.replace("rf.", "")] = value
            elif key.startswith("cost."):
                cost_dict[key.replace("cost.", "")] = value

        return cls(
            array=ArrayConfig(**array_dict),
            rf=RFChainConfig(**rf_dict),
            cost=CostConfig(**cost_dict) if cost_dict else CostConfig(),
            name=name,
        )
