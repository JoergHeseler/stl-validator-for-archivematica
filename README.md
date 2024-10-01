# stl_validator_for_archivematica

**stl_validator_for_archivematica** is a script that enables [Archivematica](https://www.archivematica.org/) to validate ASCII based Standard Tessellation Language (STL) files.

## Installation

To install the **stl_validator_for_archivematica** script, follow these steps:

### 1. Create a new validation command
- In the Archivematica frontend, navigate to **Preservation planning** > **Validation** > **Commands** > **Create new command** or go directly to [this link](http://10.10.10.20/fpr/fpcommand/create/).
- Fill in the following fields:
    - **The related tool**: Select **Archivematica script**.
    - **Description**: Enter `Validate using stl_validator`.
    - **Script**: Paste the entire content of the **stl_validator.py** file.
    - **Script type**: Select **Python script**.
    - **Command usage**: Select **Validation**.
- Click **Save**.

### 2. Create a new validation rule for ASCII based STL
- In the Archivematica frontend, navigate to **Preservation planning** > **Validation** > **Rules** > **Create new rule** or go directly to [this link](http://10.10.10.20/fpr/fprule/create/).
- Fill in the following fields:
    - **Purpose**: Select **Validation**.
    - **The related format**: Select **Text (Source Code): STL (Standard Tessellation Language) ASCII: STL (x-fmt/108)**.
    - **Command**: Select **Validate using stl_validator**.
- Click **Save**.

## Test

You can test the validator using the sample files located in the [`test`](./test/) folder.

Files that are error-free end with the filename `_valid` and should return error code **0** when validated with this script. However, all other files contain errors and should return error code **1** instead.

## Dependencies

[Archivematica 1.13.2](https://github.com/artefactual/archivematica/releases/tag/v1.13.2) was used to analyze, design, develop and test this script.

## Background

As part of the [NFDI4Culture](https://nfdi4culture.de/) initiative, efforts are underway to enhance the capabilities of open-source digital preservation software like Archivematica to identify, validate and preserve 3D file formats. This repository provides the **stl_validator_for_archivematica** script to enable ASCII based Standard Tessellation Language (STL) file validation in Archivematica, which is not supported by default in version 1.13.2, enhancing its 3D content preservation capabilities.

## Related projects

- [dae_validator_for_archivematica](https://github.com/JoergHeseler/dae_validator_for_archivematica)
- [gltf_validator_for_archivematica](https://github.com/JoergHeseler/gltf_validator_for_archivematica)
- [siegfried_falls_back_on_fido_identifier_for_archivematica](https://github.com/JoergHeseler/siegfried_falls_back_on_fido_identifier_for_archivematica)
- [x3d_validator_for_archivematica](https://github.com/JoergHeseler/x3d_validator_for_archivematica)

## Imprint

[NFDI4Culture](https://nfdi4culture.de/) – Consortium for Research Data on Material and Immaterial Cultural Heritage

NFDI4Culture is a consortium within the German [National Research Data Infrastructure (NFDI)](https://www.nfdi.de/).

Author: [Jörg Heseler](https://orcid.org/0000-0002-1497-627X)

This project is licensed under a [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

NFDI4Culture is funded by the German Research Foundation (DFG) – Project number – [441958017](https://gepris.dfg.de/gepris/projekt/441958017).