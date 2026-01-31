"""Digital array models for DAC/ADC, bandwidth, and scheduling."""

from phased_array_systems.models.digital.converters import (
    enob_to_sfdr,
    sfdr_to_enob,
    enob_to_snr,
    snr_to_enob,
    quantization_noise_floor,
    sample_rate_for_bandwidth,
    max_signal_bandwidth,
    adc_dynamic_range,
    dac_output_power,
)

from phased_array_systems.models.digital.bandwidth import (
    beam_bandwidth_product,
    max_simultaneous_beams,
    digital_beamformer_data_rate,
    channelizer_output_rate,
    processing_margin,
    beamformer_operations,
)

from phased_array_systems.models.digital.scheduling import (
    Dwell,
    Timeline,
    Function,
    timeline_utilization,
    max_update_rate,
    search_timeline,
    interleaved_timeline,
)

__all__ = [
    # Converters
    "enob_to_sfdr",
    "sfdr_to_enob",
    "enob_to_snr",
    "snr_to_enob",
    "quantization_noise_floor",
    "sample_rate_for_bandwidth",
    "max_signal_bandwidth",
    "adc_dynamic_range",
    "dac_output_power",
    # Bandwidth
    "beam_bandwidth_product",
    "max_simultaneous_beams",
    "digital_beamformer_data_rate",
    "channelizer_output_rate",
    "processing_margin",
    "beamformer_operations",
    # Scheduling
    "Dwell",
    "Timeline",
    "Function",
    "timeline_utilization",
    "max_update_rate",
    "search_timeline",
    "interleaved_timeline",
]
