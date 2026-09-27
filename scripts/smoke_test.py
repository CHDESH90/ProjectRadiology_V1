#!/usr/bin/env python3
"""Verify the radiology dev stack with a synthetic imaging workflow."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, generate_uid


def main() -> int:
    out_dir = Path(__file__).resolve().parent.parent / "artifacts" / "smoke"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Simulated grayscale chest-style patch (512×512)
    rng = np.random.default_rng(42)
    image = (rng.normal(loc=128, scale=32, size=(512, 512))).clip(0, 255).astype(np.uint8)

    png_path = out_dir / "synthetic_cxr_patch.png"
    Image.fromarray(image, mode="L").save(png_path)

    loaded = np.array(Image.open(png_path))
    mean_intensity = float(loaded.mean())
    if not (100 <= mean_intensity <= 160):
        print(f"Unexpected mean intensity: {mean_intensity}", file=sys.stderr)
        return 1

    # Minimal DICOM secondary capture (in-memory write/read)
    meta = FileMetaDataset()
    meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.7"
    meta.MediaStorageSOPInstanceUID = generate_uid()
    meta.TransferSyntaxUID = ExplicitVRLittleEndian

    ds = Dataset()
    ds.file_meta = meta
    ds.is_little_endian = True
    ds.is_implicit_VR = False
    ds.SOPClassUID = meta.MediaStorageSOPClassUID
    ds.SOPInstanceUID = meta.MediaStorageSOPInstanceUID
    ds.PatientName = "Smoke^Test"
    ds.PatientID = "SMOKE001"
    ds.Modality = "OT"
    ds.Rows, ds.Columns = image.shape
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.SamplesPerPixel = 1
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.HighBit = 7
    ds.PixelRepresentation = 0
    ds.PixelData = image.tobytes()

    dcm_path = out_dir / "synthetic_cxr_patch.dcm"
    ds.save_as(dcm_path, write_like_original=False)

    print(f"PNG: {png_path} (mean={mean_intensity:.2f})")
    print(f"DICOM: {dcm_path} ({dcm_path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
