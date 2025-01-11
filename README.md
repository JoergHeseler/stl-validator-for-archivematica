# STL Validator for Archivematica

This repository provides a script that enables [Archivematica](https://www.archivematica.org/) to validate ASCII and binary Standard Tessellation Language (STL) files.

## Installation

To install this script, follow these steps:

### 1. Create a new validation command

- In the Archivematica frontend, navigate to **Preservation planning** > **Validation** > **Commands** > **Create new command** or go directly to [this link](http://10.10.10.20/fpr/fpcommand/create/).
- Fill in the following fields:
  - **The related tool**: Select **Archivematica script**.
  - **Description**: Enter `Validate using stl-validator`.
  - **Command**: Paste the entire content of the [**stl-validator.py**](./src/stl-validator.py) file.
  - **Script type**: Select **Python script**.
  - **Command usage**: Select **Validation**.
  - Leave all other input fields and combo boxes untouched.
- Click **Save**.

### 2. Create a new validation rule for ASCII STL

- In the Archivematica frontend, navigate to **Preservation planning** > **Validation** > **Rules** > **Create new rule** or go directly to [this link](http://10.10.10.20/fpr/fprule/create/).
- Fill in the following fields:
  - **Purpose**: Select **Validation**.
  - **The related format**: Select **Text (Source Code): STL (Standard Tessellation Language) ASCII: STL (x-fmt/108)**.
  - **Command**: Select **Validate using stl-validator**.
- Click **Save**.

### 3. Create a new validation rule for binary STL

- In the Archivematica frontend, navigate to **Preservation planning** > **Validation** > **Rules** > **Create new rule** or go directly to [this link](http://10.10.10.20/fpr/fprule/create/).
- Fill in the following fields:
  - **Purpose**: Select **Validation**.
  - **The related format**: Select **CAD: STL (Standard Tessellation Language) Binary: STL (Standard Tessellation Language) Binary (fmt/865)**.
  - **Command**: Select **Validate using stl-validator**.
- Click **Save**.

## Test

To test this validator, you can use the sample STL files located [here](https://github.com/JoergHeseler/3d-sample-files-for-digital-preservation-testing/tree/main/stl).

### In Archivematica:

You can view the error codes and detailed validation results in the Archivmatica frontend after starting a transfer by expanding the `▸ Microservice: Validation` section and clicking on the gear icon of `Job: Validate formats`.

Files with no errors end with `valid` in their name and should pass validation with this script (i. e. return error code **0**). However, all other files contain errors and should fail validation (i. e. return error code **1**).

### In the command line:

You can use the validator at the command line prompt by typing `python stl-validator.py <STL file to validate>`.

#### Command line switches:

| Option/Parameter | Description                                                                                                                                                                   |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--tolerant`     | passes validation even if the vertex coordinates are negative, the vertices of each facet are not arranged counterclockwise, or the solid name differs from the endsolid name |
| `--warnings`     | prints all warning information to standard output                                                                                                                             |

## Dependencies

[Archivematica 1.13.2](https://github.com/artefactual/archivematica/releases/tag/v1.13.2) was used to analyze, design, develop and test this script.

## Background

As part of the [NFDI4Culture](https://nfdi4culture.de/) initiative, efforts are underway to enhance the capabilities of open-source digital preservation software like Archivematica to identify, validate and preserve 3D file formats. This repository provides a script to enable Standard Tessellation Language (STL) file validation in Archivematica, which is not supported by default in version 1.13.2, enhancing its 3D content preservation capabilities.

## Related projects

- [3D Sample Files for Digital Preservation Testing](https://github.com/JoergHeseler/3d-sample-files-for-digital-preservation-testing)
- [DAE Validator for Archivematica](https://github.com/JoergHeseler/dae-validator-for-archivematica)
- [glTF Metadata Extractor for Archivematica](https://github.com/JoergHeseler/gltf-metadata-extractor-for-archivematica)
- [glTF Validator for Archivematica](https://github.com/JoergHeseler/gltf-validator-for-archivematica)
- [Siegfried Falls Back on Fido Identifier for Archivematica](https://github.com/JoergHeseler/siegfried-falls-back-on-fido-identifier-for-archivematica)
  <!-- - [STL Cleaner](https://github.com/JoergHeseler/stl-cleaner) -->
- [STL Metadata Extractor for Archivematica](https://github.com/JoergHeseler/stl-metadata-extractor-for-archivematica)
- [X3D Validator for Archivematica](https://github.com/JoergHeseler/x3d-validator-for-archivematica)

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Acknowledgments

Special thanks to the colleagues from the SLUB Dresden, specifically from the Infrastructure and Long-Term Availability division, for their support and valuable feedback during the development.

## Imprint

[NFDI4Culture](https://nfdi4culture.de/) – Consortium for Research Data on Material and Immaterial Cultural Heritage

NFDI4Culture is a consortium within the German [National Research Data Infrastructure (NFDI)](https://www.nfdi.de/).

Author: [Jörg Heseler](https://orcid.org/0000-0002-1497-627X)

This repository is licensed under a [Creative Commons Attribution 4.0 International License (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).

NFDI4Culture is funded by the German Research Foundation (DFG) – Project number – [441958017](https://gepris.dfg.de/gepris/projekt/441958017).
